"""Query understanding node: extracts intent, structured location, temporal range, variables, vessel, route, and constraints from marine queries."""

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.agents.schemas.intent import (
    MarineIntent,
    MarineVariable,
    StructuredLocation,
    StructuredTimeRange,
    StructuredVessel,
    StructuredRoute,
    QueryIntent,
)
from backend.agents.state.marine_state import MarineState

# Minimal, focused known coastal reference database (preserves Mangalore and primary Indian ports)
KNOWN_COASTAL_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "mangalore": {
        "name": "Mangalore",
        "latitude": 12.8681,
        "longitude": 74.8427,
        "harbor": "Mangalore Old Port",
        "region": "Karnataka Coast",
    },
    "kochi": {
        "name": "Kochi",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "harbor": "Cochin Fisheries Harbour",
        "region": "Kerala Coast",
    },
    "cochin": {
        "name": "Kochi",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "harbor": "Cochin Fisheries Harbour",
        "region": "Kerala Coast",
    },
    "chennai": {
        "name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "harbor": "Kasimedu Fishing Harbour",
        "region": "Tamil Nadu Coast",
    },
    "mumbai": {
        "name": "Mumbai",
        "latitude": 18.9220,
        "longitude": 72.8347,
        "harbor": "Sassoon Docks",
        "region": "Maharashtra Coast",
    },
    "visakhapatnam": {
        "name": "Visakhapatnam",
        "latitude": 17.6868,
        "longitude": 83.2185,
        "harbor": "Vizag Fishing Harbour",
        "region": "Andhra Coast",
    },
    "vizag": {
        "name": "Visakhapatnam",
        "latitude": 17.6868,
        "longitude": 83.2185,
        "harbor": "Vizag Fishing Harbour",
        "region": "Andhra Coast",
    },
    "veraval": {
        "name": "Veraval",
        "latitude": 20.9077,
        "longitude": 70.3678,
        "harbor": "Veraval Port",
        "region": "Gujarat Coast",
    },
    "goa": {
        "name": "Goa",
        "latitude": 15.2993,
        "longitude": 74.1240,
        "harbor": "Malim Jetty",
        "region": "Goa Coast",
    },
}

# Recognized temporal patterns: (regex_pattern, raw_str, relative_day, period, is_historical)
TIME_PATTERNS: List[Tuple[str, str, str, Optional[str], bool]] = [
    (r"tomorrow\s+morning", "tomorrow morning", "tomorrow", "morning", False),
    (r"tomorrow\s+afternoon", "tomorrow afternoon", "tomorrow", "afternoon", False),
    (r"tomorrow\s+evening", "tomorrow evening", "tomorrow", "evening", False),
    (r"tomorrow\s+night", "tomorrow night", "tomorrow", "night", False),
    (r"\btomorrow\b", "tomorrow", "tomorrow", "all-day", False),
    (r"this\s+morning", "this morning", "today", "morning", False),
    (r"today\s+morning", "today morning", "today", "morning", False),
    (r"today\s+afternoon", "today afternoon", "today", "afternoon", False),
    (r"today\s+evening", "today evening", "today", "evening", False),
    (r"\btonight\b", "tonight", "today", "night", False),
    (r"\btoday\b", "today", "today", "all-day", False),
    (r"this\s+weekend", "this weekend", "this weekend", "all-day", False),
    (r"this\s+week", "this week", "this week", "all-day", False),
    (r"next\s+week", "next week", "next week", "all-day", False),
    (r"next\s+24\s+hours", "next 24 hours", "next 24 hours", "all-day", False),
    (r"next\s+48\s+hours", "next 48 hours", "next 48 hours", "all-day", False),
    (r"last\s+7\s+days", "last 7 days", "last 7 days", "all-day", True),
    (r"last\s+30\s+days", "last 30 days", "last 30 days", "all-day", True),
    (r"past\s+month", "past month", "past month", "all-day", True),
    (r"last\s+month", "last month", "last month", "all-day", True),
    (r"last\s+year", "last year", "last year", "all-day", True),
    (r"\byesterday\b", "yesterday", "yesterday", "all-day", True),
]

# Non-location stopwords & action words to ignore when checking place matches
PLACE_STOPWORDS = {
    "this", "that", "the", "point", "this point", "restricted", "restricted area",
    "restricted marine zone", "marine zone", "zone", "area", "vessel", "ocean",
    "sea", "water", "here", "there", "tomorrow", "today", "tonight", "last 30 days",
    "pfz", "sst", "chlorophyll", "weather", "port", "harbor"
}

ACTION_STOPWORDS = {
    "go", "fishing", "fish", "sail", "sailing", "swim", "swimming", "catch",
    "tell", "me", "navigate", "cross", "venture", "see", "find", "this point",
    "the ocean", "ocean", "restricted", "restricted area", "marine zone",
    "restricted marine zone", "point", "here", "there", "tomorrow", "today",
    "tonight", "last 30 days", "pfz", "sst", "chlorophyll", "weather", "vessel"
}

# Recognized vessel types
VESSEL_TYPES = [
    "small motorized boat",
    "motorized boat",
    "artisanal boat",
    "small craft",
    "small boat",
    "fishing boat",
    "trawler",
    "mechanized boat",
    "cargo ship",
    "cargo",
    "tanker",
    "catamaran",
    "canoe",
    "yacht",
    "patrol vessel",
]


def extract_location(query: str, lower_query: str) -> Optional[StructuredLocation]:
    """
    Extracts location details from query.
    - If explicit coordinates are present (e.g. '12.91, 74.85'), extracts coordinates.
    - If known port is matched (e.g. 'Mangalore'), populates known coordinates.
    - If unknown location is detected, preserves name with latitude=None, longitude=None.
    - If no location is mentioned, returns None (never invents missing information).
    """
    # 1. Check explicit coordinates (e.g. '12.91, 74.85', '12.91 N, 74.85 E', '12.91°N 74.85°E')
    coord_match = re.search(
        r"(-?\d{1,2}\.?\d*)\s*°?\s*([NS])?[\s,]+(-?\d{1,3}\.?\d*)\s*°?\s*([EW])?",
        query,
        re.IGNORECASE
    )
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(3))
            if coord_match.group(2) and coord_match.group(2).upper() == "S":
                lat = -lat
            if coord_match.group(4) and coord_match.group(4).upper() == "W":
                lon = -lon
            coord_str = f"{lat:.2f}, {lon:.2f}"
            return StructuredLocation(
                name=coord_str,
                latitude=lat,
                longitude=lon,
                harbor=None,
                region="Coordinates",
            )
        except ValueError:
            pass

    # 2. Check minimal known coastal ports
    for key, loc_data in KNOWN_COASTAL_LOCATIONS.items():
        if re.search(rf"\b{re.escape(key)}\b", lower_query):
            return StructuredLocation(
                name=loc_data["name"],
                latitude=loc_data["latitude"],
                longitude=loc_data["longitude"],
                harbor=loc_data.get("harbor"),
                region=loc_data.get("region"),
            )

    # 3. Check for named unknown location (e.g. 'near X', 'around X', 'off X', 'offshore X')
    place_match = re.search(
        r"\b(?:near|around|off|outside|offshore)\s+([A-Za-z][A-Za-z0-9\s'-]{2,25})",
        query,
        re.IGNORECASE
    )
    if place_match:
        raw_place = place_match.group(1).strip()
        # Clean trailing query tokens
        raw_place = re.sub(r"\b(waters|coast|sea|port|harbor|bay|gulf|for|tomorrow|today|tonight|this|next|with|\?|\.|$)\b.*", "", raw_place, flags=re.IGNORECASE).strip()
        raw_place = re.sub(r"^(?:the|a|an)\s+", "", raw_place, flags=re.IGNORECASE).strip()
        cleaned_lower = raw_place.lower().strip()
        tokens = cleaned_lower.split()

        if (
            cleaned_lower
            and cleaned_lower not in PLACE_STOPWORDS
            and len(cleaned_lower) >= 3
            and not any(t in ACTION_STOPWORDS for t in tokens)
        ):
            if cleaned_lower in KNOWN_COASTAL_LOCATIONS:
                loc_data = KNOWN_COASTAL_LOCATIONS[cleaned_lower]
                return StructuredLocation(
                    name=loc_data["name"],
                    latitude=loc_data["latitude"],
                    longitude=loc_data["longitude"],
                    harbor=loc_data.get("harbor"),
                    region=loc_data.get("region"),
                )
            return StructuredLocation(
                name=raw_place.title(),
                latitude=None,
                longitude=None,
                harbor=None,
                region=None,
            )

    # No location detected
    return None


def extract_time_range(lower_query: str) -> Optional[StructuredTimeRange]:
    """
    Extracts structured temporal parameters from user query.
    Returns None if no temporal expression is present.
    """
    for pattern, raw_str, rel_day, period, hist in TIME_PATTERNS:
        if re.search(pattern, lower_query):
            return StructuredTimeRange(
                raw=raw_str,
                relative_day=rel_day,
                period=period,
                forecast_horizon_hours=0 if hist else (36 if "tomorrow" in raw_str else 24),
                is_historical=hist,
            )

    return None


def extract_marine_variables(lower_query: str) -> List[str]:
    """
    Extracts explicitly requested marine domain variables from query.
    """
    variables: List[str] = []

    if re.search(r"\b(?:sst|sea surface temperature|surface temp|water temperature|water temp)\b", lower_query):
        variables.append(MarineVariable.SST.value)
    if re.search(r"\b(?:chlorophyll|chlorophyll-a|chla)\b", lower_query):
        variables.append(MarineVariable.CHLOROPHYLL.value)
    if re.search(r"\b(?:pfz|potential fishing zone)\b", lower_query):
        variables.append(MarineVariable.PFZ.value)
    if re.search(r"\b(?:wind|wind speed|wind direction|gust)\b", lower_query):
        variables.append(MarineVariable.WIND.value)
    if re.search(r"\b(?:waves?|wave height|sea height|chop)\b", lower_query):
        variables.append(MarineVariable.WAVE.value)
    if re.search(r"\b(?:swell|high swell|swell period|swell wave)\b", lower_query):
        variables.append(MarineVariable.SWELL.value)
    if re.search(r"\b(?:tides?|tidal)\b", lower_query):
        variables.append(MarineVariable.TIDE.value)
    if re.search(r"\b(?:currents?|ocean currents?)\b", lower_query):
        variables.append(MarineVariable.CURRENT.value)
    if re.search(r"\b(?:vessel activity|boat traffic|ais traffic|boat density)\b", lower_query):
        variables.append(MarineVariable.VESSEL_ACTIVITY.value)

    return variables


def extract_vessel(lower_query: str, query: str) -> Optional[StructuredVessel]:
    """
    Extracts vessel information (e.g. IMO, MMSI, vessel ID, or vessel type).
    """
    # 1. Match IMO numbers (e.g. 'IMO1234567' or 'IMO 1234567')
    imo_match = re.search(r"\bIMO\s*([0-9]{6,8})\b", query, re.IGNORECASE)
    if imo_match:
        return StructuredVessel(
            type=None,
            id=f"IMO{imo_match.group(1)}",
            name=None,
            length_m=None,
        )

    # 2. Match MMSI (e.g. 'MMSI: 412345678' or 'MMSI 412345678')
    mmsi_match = re.search(r"\bMMSI[:\s]*([0-9]{9})\b", query, re.IGNORECASE)
    if mmsi_match:
        return StructuredVessel(
            type=None,
            id=mmsi_match.group(1),
            name=None,
            length_m=None,
        )

    # 3. Match generic vessel identifier (e.g. 'vessel IND-1234', 'vessel 45')
    vessel_id_match = re.search(r"\bvessel\s+([A-Za-z0-9-]+)\b", query, re.IGNORECASE)
    if vessel_id_match and vessel_id_match.group(1).lower() not in ("traffic", "activity", "type", "speed"):
        return StructuredVessel(
            type=None,
            id=vessel_id_match.group(1),
            name=None,
            length_m=None,
        )

    # 4. Match vessel type
    for v_type in VESSEL_TYPES:
        if re.search(rf"\b{re.escape(v_type)}\b", lower_query):
            return StructuredVessel(
                type=v_type,
                id=None,
                name=None,
                length_m=None,
            )

    return None


def extract_route(query: str, lower_query: str) -> Optional[StructuredRoute]:
    """
    Extracts route parameters (origin, destination) if specified.
    """
    # Pattern 1: from <origin> to <destination>
    route_match = re.search(
        r"\bfrom\s+([A-Za-z0-9\s'-]+?)\s+to\s+([A-Za-z0-9\s'-]+?)(?:\s+(?:tomorrow|today|tonight|this|next|via|with|\.|\?|$))",
        query,
        re.IGNORECASE
    )
    if not route_match:
        # Pattern 2: between <origin> and <destination>
        route_match = re.search(
            r"\bbetween\s+([A-Za-z0-9\s'-]+?)\s+and\s+([A-Za-z0-9\s'-]+?)(?:\s+(?:tomorrow|today|tonight|this|next|via|with|\.|\?|$))",
            query,
            re.IGNORECASE
        )

    if route_match:
        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()
        origin = re.sub(r"^(?:the|a|an)\s+", "", origin, flags=re.IGNORECASE).strip()
        destination = re.sub(r"^(?:the|a|an)\s+", "", destination, flags=re.IGNORECASE).strip()
        if origin and destination:
            return StructuredRoute(
                origin=origin.title(),
                destination=destination.title(),
                waypoints=[],
            )

    # Pattern 3: general route query mention (e.g. 'Can my route cross this restricted area?')
    if "route" in lower_query or "transit" in lower_query or "passage" in lower_query:
        return StructuredRoute(origin=None, destination=None, waypoints=[])

    return None


def extract_constraints(lower_query: str) -> Dict[str, Any]:
    """
    Extracts operational constraints (e.g. max wave height, max wind speed).
    """
    constraints: Dict[str, Any] = {}

    # Wave height limit (e.g. 'waves under 1.5m', 'max wave 2m')
    wave_match = re.search(r"\bwaves?\s*(?:under|below|less\s+than|<=|<|max|up\s+to)?\s*(\d+(?:\.\d+)?)\s*(?:m|meter|meters)?\b", lower_query)
    if wave_match and any(w in lower_query for w in ["under", "below", "less than", "<", "max", "limit"]):
        try:
            constraints["max_wave_height_m"] = float(wave_match.group(1))
        except ValueError:
            pass

    # Wind speed limit (e.g. 'wind below 15 kts')
    wind_match = re.search(r"\bwind(?:\s+speed)?\s*(?:under|below|less\s+than|<=|<|max)?\s*(\d+(?:\.\d+)?)\s*(?:kts|knots|km/h|m/s)?\b", lower_query)
    if wind_match and any(w in lower_query for w in ["under", "below", "less than", "<", "max", "limit"]):
        try:
            constraints["max_wind_speed_knots"] = float(wind_match.group(1))
        except ValueError:
            pass

    # Distance constraint (e.g. 'within 20 NM')
    dist_match = re.search(r"\b(?:within|under|less\s+than)\s*(\d+(?:\.\d+)?)\s*(?:nm|nautical\s+miles|km)\b", lower_query)
    if dist_match:
        try:
            constraints["max_distance_nm"] = float(dist_match.group(1))
        except ValueError:
            pass

    return constraints


def classify_intent(lower_query: str) -> Tuple[str, float]:
    """
    Deterministically classifies query into one of the 10 standard MarineIntent categories with simple bounded confidence.
    """
    # 1. Historical Analysis
    if any(k in lower_query for k in [
        "last 30 days", "last 7 days", "past month", "last month", "last year", "last 5 years", "last 10 years",
        "historical", "past data", "archive", "climatology", "trends in 20", "records for", "over the last", "historical trends"
    ]) or re.search(r"\b(?:last|past)\s+\d+\s+(?:years|months|days|decades)\b", lower_query):
        return MarineIntent.HISTORICAL_ANALYSIS.value, 0.95

    # 2. Vessel Query
    if re.search(r"\b(?:where is vessel|track vessel|vessel tracking|ais position|vessel speed|imo\s*[0-9]+|mmsi|fleet activity)\b", lower_query):
        return MarineIntent.VESSEL_QUERY.value, 0.95

    # 3. PFZ Search (explicit PFZ queries)
    if any(k in lower_query for k in ["nearest pfz", "pfz map", "potential fishing zone", "find pfz", "pfz hotspots", "ocean color front"]):
        return MarineIntent.PFZ_SEARCH.value, 0.95

    # 4. Route Query (route crossing, passage, route planning)
    if re.search(r"\b(?:route cross|can my route|passage route|transit from|route from|route between|channel entry|harbor entry|passage navigation)\b", lower_query):
        return MarineIntent.ROUTE_QUERY.value, 0.95

    # 5. Geofence Query (restricted area / boundary checks)
    if any(k in lower_query for k in [
        "restricted marine zone", "restricted zone", "restricted area", "inside a restricted",
        "geofence", "boundary", "imbl", "international maritime boundary", "eez", "mpa",
        "marine protected area", "sanctuary", "no-fishing zone", "prohibited area"
    ]):
        return MarineIntent.GEOFENCE_QUERY.value, 0.95

    # 6. Hazard Query
    if any(k in lower_query for k in [
        "dangerous conditions", "dangerous", "danger", "cyclone", "storm", "tsunami",
        "gale warning", "squall", "high wave warning", "evacuation", "hazard bulletin", "emergency"
    ]):
        return MarineIntent.HAZARD_QUERY.value, 0.95

    # 7. Marine Safety
    if any(k in lower_query for k in [
        "is it safe", "safe to go", "safe to fish", "safety advisory", "can small boat sail",
        "venture out", "danger at sea", "small craft advisory", "safety check"
    ]):
        return MarineIntent.MARINE_SAFETY.value, 0.95

    # 8. Fishing Recommendation
    if any(k in lower_query for k in [
        "where should i fish", "where can i fish", "where to fish", "where to catch",
        "fishing recommendation", "good spot to fish", "good spot for fish", "fish catch",
        "target tuna", "catch sardine", "mackerel catch", "fish shoal", "fishing ground"
    ]):
        return MarineIntent.FISHING_RECOMMENDATION.value, 0.95
    if any(k in lower_query for k in ["fish", "fishing", "catch", "tuna", "sardine", "mackerel"]):
        return MarineIntent.FISHING_RECOMMENDATION.value, 0.85

    # 9. Weather Query
    if any(k in lower_query for k in [
        "weather", "wave", "waves", "wind", "swell", "sea state", "tide", "tides",
        "current", "currents", "rain", "ocean condition", "rough sea"
    ]):
        return MarineIntent.WEATHER_QUERY.value, 0.90

    # 10. General Marine Query (Fallback)
    return MarineIntent.GENERAL_MARINE_QUERY.value, 0.70


import logging
import time
from backend.agents.llm.base import classify_llm_error
from backend.agents.llm.factory import get_llm_provider
from backend.agents.llm.providers.fake_provider import FakeLLMProvider
from backend.agents.prompts.extraction_prompts import STRUCTURED_QUERY_UNDERSTANDING_PROMPT
from backend.agents.prompts.system_prompts import MARINE_SYSTEM_DIRECTIVE

logger = logging.getLogger(__name__)


async def understand_query_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Parses user query into structured QueryIntent, location, time range,
    marine variables, vessel, route, and operational constraints.
    Supports LLM-backed extraction with 100% deterministic fallback and latency telemetry.
    """
    t0 = time.perf_counter()
    query = state.get("query", "") or state.get("raw_query", "")
    lower_query = query.lower().strip()

    llm_used = False
    llm_fallback = False
    llm_fallback_reason: Optional[str] = None

    # Check if LLM extraction should be attempted
    llm = get_llm_provider()
    attempt_llm = False
    if state.get("use_llm") is True:
        attempt_llm = True
    elif llm.provider_name in ("gemini", "openai"):
        attempt_llm = True
    elif isinstance(llm, FakeLLMProvider) and (llm.canned_structured is not None or llm.error_mode is not None):
        attempt_llm = True

    if attempt_llm and query:
        try:
            extracted_intent: QueryIntent = await llm.generate_structured(
                prompt=STRUCTURED_QUERY_UNDERSTANDING_PROMPT.format(query=query),
                schema_class=QueryIntent,
                system_prompt=MARINE_SYSTEM_DIRECTIVE,
            )
            # Enrich location if name matches known ports and coords are missing
            loc_obj = getattr(extracted_intent, "location", None)
            if loc_obj:
                loc_name = getattr(loc_obj, "name", None) if hasattr(loc_obj, "name") else (loc_obj.get("name") if isinstance(loc_obj, dict) else None)
                if loc_name:
                    loc_key = loc_name.lower().strip()
                    if loc_key in KNOWN_COASTAL_LOCATIONS:
                        known = KNOWN_COASTAL_LOCATIONS[loc_key]
                        if hasattr(loc_obj, "latitude"):
                            if getattr(loc_obj, "latitude", None) is None:
                                loc_obj.latitude = known["latitude"]
                            if getattr(loc_obj, "longitude", None) is None:
                                loc_obj.longitude = known["longitude"]
                            if not getattr(loc_obj, "harbor", None) and known.get("harbor"):
                                loc_obj.harbor = known.get("harbor")
                            if not getattr(loc_obj, "region", None) and known.get("region"):
                                loc_obj.region = known.get("region")
                        elif isinstance(loc_obj, dict):
                            if loc_obj.get("latitude") is None:
                                loc_obj["latitude"] = known["latitude"]
                            if loc_obj.get("longitude") is None:
                                loc_obj["longitude"] = known["longitude"]
                            if not loc_obj.get("harbor") and known.get("harbor"):
                                loc_obj["harbor"] = known.get("harbor")
                            if not loc_obj.get("region") and known.get("region"):
                                loc_obj["region"] = known.get("region")

            if hasattr(extracted_intent, "raw_query") and not extracted_intent.raw_query:
                extracted_intent.raw_query = query
            elif isinstance(extracted_intent, dict) and not extracted_intent.get("raw_query"):
                extracted_intent["raw_query"] = query

            query_intent_dict = extracted_intent.model_dump() if hasattr(extracted_intent, "model_dump") else extracted_intent
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            latency_telemetry = dict(state.get("latency_telemetry") or {})
            latency_telemetry["understand_query_ms"] = latency_ms

            return {
                "intent": getattr(extracted_intent, "intent", query_intent_dict.get("intent")),
                "confidence": getattr(extracted_intent, "confidence", query_intent_dict.get("confidence")),
                "location": query_intent_dict.get("location"),
                "time_range": query_intent_dict.get("time_range"),
                "variables": getattr(extracted_intent, "variables", query_intent_dict.get("variables")),
                "vessel": query_intent_dict.get("vessel"),
                "route": query_intent_dict.get("route"),
                "constraints": getattr(extracted_intent, "constraints", query_intent_dict.get("constraints")),
                "query_intent": query_intent_dict,
                "structured_query": query_intent_dict,
                "llm_used": True,
                "llm_fallback": False,
                "llm_provider": llm.provider_name,
                "llm_model": llm.model_name,
                "latency_telemetry": latency_telemetry,
            }
        except Exception as e:
            classified_err = classify_llm_error(e)
            logger.debug(f"LLM query understanding fallback triggered: {classified_err} ({type(e).__name__})")
            llm_fallback = True
            llm_fallback_reason = classified_err

    # Deterministic Rule-Based Fallback Parser
    # 1. Intent Detection
    intent, confidence = classify_intent(lower_query)

    # 2. Location Extraction (None if not mentioned)
    location_obj = extract_location(query, lower_query)
    location_dict = location_obj.model_dump() if location_obj else None

    # 3. Time Range Extraction (None if not mentioned)
    time_range_obj = extract_time_range(lower_query)
    time_range_dict = time_range_obj.model_dump() if time_range_obj else None

    # 4. Marine Variables Extraction (Only explicitly requested)
    variables = extract_marine_variables(lower_query)

    # 5. Vessel Extraction (None if not mentioned)
    vessel_obj = extract_vessel(lower_query, query)
    vessel_dict = vessel_obj.model_dump() if vessel_obj else None

    # 6. Route Extraction (None if not mentioned)
    route_obj = extract_route(query, lower_query)
    route_dict = route_obj.model_dump() if route_obj else None

    # 7. Constraints Extraction
    constraints = extract_constraints(lower_query)

    # 8. Normalized QueryIntent Object
    query_intent = QueryIntent(
        intent=intent,
        confidence=confidence,
        location=location_obj,
        time_range=time_range_obj,
        variables=variables,
        vessel=vessel_obj,
        route=route_obj,
        constraints=constraints,
        raw_query=query,
    )

    query_intent_dict = query_intent.model_dump()
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    latency_telemetry = dict(state.get("latency_telemetry") or {})
    if "pipeline_start_perf" not in latency_telemetry:
        latency_telemetry["pipeline_start_perf"] = t0
    latency_telemetry["understand_query_ms"] = latency_ms

    result_dict = {
        "intent": intent,
        "confidence": confidence,
        "location": location_dict,
        "time_range": time_range_dict,
        "variables": variables,
        "vessel": vessel_dict,
        "route": route_dict,
        "constraints": constraints,
        "query_intent": query_intent_dict,
        "structured_query": query_intent_dict,
        "llm_used": llm_used,
        "llm_fallback": llm_fallback,
        "llm_provider": llm.provider_name if llm else "none",
        "llm_model": llm.model_name if llm else "none",
        "latency_telemetry": latency_telemetry,
    }
    if llm_fallback_reason:
        result_dict["llm_fallback_reason"] = llm_fallback_reason

    return result_dict


# Backwards compatibility aliases
understand_query = understand_query_node
query_understanding_node = understand_query_node

