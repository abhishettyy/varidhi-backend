"""Query understanding node: extracts marine intent, spatial entities, and temporal scope."""

import re
from datetime import datetime
from typing import Any, Dict

from backend.agents.schemas.intent import MarineIntent, IntentClassificationResult
from backend.agents.schemas.location_time import (
    Coordinates,
    SpatialContext,
    TemporalContext,
    SpatioTemporalContext,
)
from backend.agents.state.agent_state import AgentState


# Known coastal ports / regions for fast local entity matching
KNOWN_COASTAL_LOCATIONS = {
    "kochi": {"lat": 9.9312, "lon": 76.2673, "harbor": "Cochin Fisheries Harbour", "region": "Kerala Coast"},
    "cochin": {"lat": 9.9312, "lon": 76.2673, "harbor": "Cochin Fisheries Harbour", "region": "Kerala Coast"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "harbor": "Kasimedu Fishing Harbour", "region": "Tamil Nadu Coast"},
    "kasimedu": {"lat": 13.1250, "lon": 80.2980, "harbor": "Kasimedu Fishing Harbour", "region": "Tamil Nadu Coast"},
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "harbor": "Vizag Fishing Harbour", "region": "Andhra Coast"},
    "vizag": {"lat": 17.6868, "lon": 83.2185, "harbor": "Vizag Fishing Harbour", "region": "Andhra Coast"},
    "veraval": {"lat": 20.9077, "lon": 70.3678, "harbor": "Veraval Port", "region": "Gujarat Coast"},
    "mumbai": {"lat": 18.9220, "lon": 72.8347, "harbor": "Sassoon Docks", "region": "Maharashtra Coast"},
    "goa": {"lat": 15.2993, "lon": 74.1240, "harbor": "Malim Jetty", "region": "Goa Coast"},
    "mangalore": {"lat": 12.8681, "lon": 74.8427, "harbor": "Mangalore Old Port", "region": "Karnataka Coast"},
    "kanyakumari": {"lat": 8.0883, "lon": 77.5385, "harbor": "Chinnamuttam Harbor", "region": "Tamil Nadu Coast"},
    "tuticorin": {"lat": 8.7642, "lon": 78.1348, "harbor": "Thoothukudi Harbor", "region": "Tamil Nadu Coast"},
    "puri": {"lat": 19.8135, "lon": 85.8312, "harbor": "Puri Coastal Waters", "region": "Odisha Coast"},
    "paradeep": {"lat": 20.3160, "lon": 86.6110, "harbor": "Paradip Port", "region": "Odisha Coast"},
}


async def query_understanding_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Analyzes the raw query to identify intent, location, and timeframe.
    """
    raw_query = state.get("raw_query", "").strip()
    lower_query = raw_query.lower()

    # --- 1. Intent Detection ---
    primary_intent = MarineIntent.GENERAL_MARINE_QUERY
    secondary_intents = []
    confidence = 0.9
    is_urgent = False

    if any(k in lower_query for k in ["cyclone", "storm", "tsunami", "high swell", "gale", "emergency", "danger"]):
        primary_intent = MarineIntent.HAZARD_ALERT
        is_urgent = True
    elif any(k in lower_query for k in ["fishing zone", "pfz", "fish", "tuna", "catch", "sardine", "mackerel", "shoal"]):
        primary_intent = MarineIntent.POTENTIAL_FISHING_ZONE
        secondary_intents.append(MarineIntent.OCEAN_WEATHER_SAFETY)
    elif any(k in lower_query for k in ["weather", "wave", "wind", "swell", "sea state", "rough", "rain", "tide"]):
        primary_intent = MarineIntent.OCEAN_WEATHER_SAFETY
    elif any(k in lower_query for k in ["algal bloom", "red tide", "chlorophyll", "water quality", "toxic", "salinity"]):
        primary_intent = MarineIntent.WATER_QUALITY_ALGAL_BLOOM
    elif any(k in lower_query for k in ["route", "navigation", "channel", "shallow", "harbor entry", "passage"]):
        primary_intent = MarineIntent.NAVIGATION_ADVISORY

    intent_result = IntentClassificationResult(
        primary_intent=primary_intent,
        secondary_intents=secondary_intents,
        confidence=confidence,
        reasoning=f"Query classified as {primary_intent.value} based on domain keywords.",
        is_urgent_safety_risk=is_urgent,
    )

    # --- 2. Location Extraction ---
    spatial = SpatialContext()
    # Check regex coordinates (e.g. 9.93, 76.26 or 9.93N 76.26E)
    coord_match = re.search(r"(-?\d{1,2}\.?\d*)\s*°?\s*([NS])?[\s,]+(-?\d{1,3}\.?\d*)\s*°?\s*([EW])?", raw_query, re.IGNORECASE)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(3))
            if coord_match.group(2) and coord_match.group(2).upper() == "S":
                lat = -lat
            if coord_match.group(4) and coord_match.group(4).upper() == "W":
                lon = -lon
            spatial.coordinates = Coordinates(latitude=lat, longitude=lon)
            spatial.place_name = f"Coordinates ({lat:.2f}, {lon:.2f})"
        except ValueError:
            pass

    # Check known coastal locations
    if not spatial.coordinates:
        for loc_name, data in KNOWN_COASTAL_LOCATIONS.items():
            if loc_name in lower_query:
                spatial.place_name = loc_name.title()
                spatial.harbor_or_port = data["harbor"]
                spatial.coastal_state_or_country = data["region"]
                spatial.coordinates = Coordinates(latitude=data["lat"], longitude=data["lon"])
                break

    # If still no location detected, default to Coastal Zone
    if not spatial.place_name:
        spatial.place_name = "Coastal Waters (General)"

    # --- 3. Timeframe Extraction ---
    temporal = TemporalContext()
    if "tomorrow" in lower_query:
        temporal.time_descriptor = "tomorrow"
        temporal.forecast_horizon_hours = 36
    elif "today" in lower_query or "tonight" in lower_query:
        temporal.time_descriptor = "today"
        temporal.forecast_horizon_hours = 12
    elif "weekend" in lower_query:
        temporal.time_descriptor = "this weekend"
        temporal.forecast_horizon_hours = 72
    elif "next 48 hours" in lower_query or "2 days" in lower_query:
        temporal.time_descriptor = "next 48 hours"
        temporal.forecast_horizon_hours = 48
    else:
        temporal.time_descriptor = "next 24 hours"
        temporal.forecast_horizon_hours = 24

    spatiotemporal = SpatioTemporalContext(
        spatial=spatial,
        temporal=temporal,
        requires_spatial_clarification=spatial.coordinates is None,
        requires_temporal_clarification=False,
    )

    return {
        "intent_result": intent_result,
        "spatiotemporal_context": spatiotemporal,
    }
