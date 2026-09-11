"""Query understanding node: extracts intent, structured location, and temporal range from marine queries."""

import re
from typing import Any, Dict

from backend.agents.schemas.intent import MarineIntent
from backend.agents.state.marine_state import MarineState

# Geographic reference database of major coastal ports & landing centers
COASTAL_LOCATIONS = {
    "mangalore": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427, "harbor": "Mangalore Old Port", "region": "Karnataka Coast"},
    "kochi": {"name": "Kochi", "latitude": 9.9312, "longitude": 76.2673, "harbor": "Cochin Fisheries Harbour", "region": "Kerala Coast"},
    "cochin": {"name": "Kochi", "latitude": 9.9312, "longitude": 76.2673, "harbor": "Cochin Fisheries Harbour", "region": "Kerala Coast"},
    "chennai": {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707, "harbor": "Kasimedu Fishing Harbour", "region": "Tamil Nadu Coast"},
    "kasimedu": {"name": "Kasimedu", "latitude": 13.1250, "longitude": 80.2980, "harbor": "Kasimedu Fishing Harbour", "region": "Tamil Nadu Coast"},
    "visakhapatnam": {"name": "Visakhapatnam", "latitude": 17.6868, "longitude": 83.2185, "harbor": "Vizag Fishing Harbour", "region": "Andhra Coast"},
    "vizag": {"name": "Visakhapatnam", "latitude": 17.6868, "longitude": 83.2185, "harbor": "Vizag Fishing Harbour", "region": "Andhra Coast"},
    "veraval": {"name": "Veraval", "latitude": 20.9077, "longitude": 70.3678, "harbor": "Veraval Port", "region": "Gujarat Coast"},
    "mumbai": {"name": "Mumbai", "latitude": 18.9220, "longitude": 72.8347, "harbor": "Sassoon Docks", "region": "Maharashtra Coast"},
    "goa": {"name": "Goa", "latitude": 15.2993, "longitude": 74.1240, "harbor": "Malim Jetty", "region": "Goa Coast"},
    "kanyakumari": {"name": "Kanyakumari", "latitude": 8.0883, "longitude": 77.5385, "harbor": "Chinnamuttam Harbor", "region": "Tamil Nadu Coast"},
    "tuticorin": {"name": "Tuticorin", "latitude": 8.7642, "longitude": 78.1348, "harbor": "Thoothukudi Harbor", "region": "Tamil Nadu Coast"},
    "puri": {"name": "Puri", "latitude": 19.8135, "longitude": 85.8312, "harbor": "Puri Coastal Waters", "region": "Odisha Coast"},
    "paradeep": {"name": "Paradeep", "latitude": 20.3160, "longitude": 86.6110, "harbor": "Paradip Port", "region": "Odisha Coast"},
}

TIME_PATTERNS = [
    (r"tomorrow\s+morning", "tomorrow morning"),
    (r"tomorrow\s+afternoon", "tomorrow afternoon"),
    (r"tomorrow\s+evening", "tomorrow evening"),
    (r"tomorrow\s+night", "tomorrow night"),
    (r"tomorrow", "tomorrow"),
    (r"today\s+morning", "today morning"),
    (r"today\s+afternoon", "today afternoon"),
    (r"today\s+evening", "today evening"),
    (r"tonight", "tonight"),
    (r"today", "today"),
    (r"this\s+weekend", "this weekend"),
    (r"next\s+48\s+hours", "next 48 hours"),
    (r"next\s+24\s+hours", "next 24 hours"),
]


async def understand_query_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Parses user query into intent, structured location, and time range.
    Uses modular deterministic extraction with simple LLM hook readiness.
    """
    query = state.get("query", "") or state.get("raw_query", "")
    lower_query = query.lower().strip()

    # --- 1. Intent Detection ---
    intent = MarineIntent.GENERAL_QUERY.value

    if any(k in lower_query for k in ["fish", "fishing", "catch", "tuna", "sardine", "mackerel", "pfz", "where to fish", "good spot"]):
        intent = MarineIntent.FISHING_RECOMMENDATION.value
    elif any(k in lower_query for k in ["cyclone", "storm", "tsunami", "gale", "danger", "emergency", "rough sea"]):
        intent = MarineIntent.HAZARD_ALERT.value
    elif any(k in lower_query for k in ["weather", "wave", "wind", "swell", "sea state", "tide", "rain"]):
        intent = MarineIntent.WEATHER_SAFETY.value
    elif any(k in lower_query for k in ["algae", "algal bloom", "red tide", "water quality", "toxic", "chlorophyll"]):
        intent = MarineIntent.WATER_QUALITY.value
    elif any(k in lower_query for k in ["navigation", "channel", "passage", "route", "harbor entry", "shallow"]):
        intent = MarineIntent.NAVIGATION_ADVISORY.value

    # --- 2. Location Extraction ---
    location: Dict[str, Any] = {}

    # Coordinate pattern check (e.g. 12.86, 74.84 or 12.86N 74.84E)
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
            location = {
                "name": f"Coordinates ({lat:.2f}, {lon:.2f})",
                "latitude": lat,
                "longitude": lon,
                "region": "Offshore Coordinates",
            }
        except ValueError:
            pass

    # Keyword location matching
    if not location:
        for key, loc_data in COASTAL_LOCATIONS.items():
            if key in lower_query:
                location = dict(loc_data)
                break

    # Fallback generic location if unspecified
    if not location:
        location = {
            "name": "Coastal Waters (General)",
            "latitude": None,
            "longitude": None,
            "region": "Indian Coastal Waters",
        }

    # --- 3. Time Range Extraction ---
    time_range = "next 24 hours"
    for pattern, descriptor in TIME_PATTERNS:
        if re.search(pattern, lower_query):
            time_range = descriptor
            break

    return {
        "intent": intent,
        "location": location,
        "time_range": time_range,
    }


# Backwards compatibility alias
understand_query = understand_query_node
