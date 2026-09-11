"""Planner node: produces a list of required marine data feeds and calculations."""

from typing import Any, Dict, List
from backend.agents.schemas.intent import MarineIntent
from backend.agents.state.marine_state import MarineState

# Standard required data/calculation plans per marine intent
INTENT_PLAN_MAPPINGS: Dict[str, List[str]] = {
    MarineIntent.FISHING_RECOMMENDATION.value: [
        "PFZ",            # Potential Fishing Zone data & convergence fronts
        "SST",            # Sea Surface Temperature gradients
        "weather",        # Wind speed and surface meteorology
        "waves",          # Significant wave height and swell conditions
        "tide",           # Tidal currents and water levels
        "restrictions",   # Marine protected zones, international maritime boundaries, small craft bans
    ],
    MarineIntent.WEATHER_SAFETY.value: [
        "weather",
        "waves",
        "wind",
        "swell",
        "hazard_bulletins",
        "risk_score",
    ],
    MarineIntent.HAZARD_ALERT.value: [
        "hazard_bulletins",
        "cyclone_track",
        "high_swell_warnings",
        "wind_gusts",
        "evacuation_advisories",
    ],
    MarineIntent.WATER_QUALITY.value: [
        "chlorophyll",
        "SST",
        "algal_bloom_risk",
        "dissolved_oxygen",
        "water_health_index",
    ],
    MarineIntent.NAVIGATION_ADVISORY.value: [
        "weather",
        "waves",
        "bathymetry_depth",
        "currents",
        "harbor_ingress_conditions",
    ],
    MarineIntent.GENERAL_QUERY.value: [
        "weather",
        "general_marine_context",
    ],
}


async def planner_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the plan of required information and analytics without calling external APIs.
    """
    intent = state.get("intent") or MarineIntent.GENERAL_QUERY.value

    # Retrieve required information plan
    plan_steps = INTENT_PLAN_MAPPINGS.get(
        intent,
        ["weather", "general_marine_context"]
    )

    return {
        "plan": plan_steps,
    }


# Backwards compatibility alias
planner = planner_node
