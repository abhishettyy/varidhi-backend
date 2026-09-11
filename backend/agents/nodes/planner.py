"""Planner node: produces a structured list of required marine data feeds and calculations."""

from typing import Any, Dict, List
from backend.agents.schemas.intent import MarineIntent
from backend.agents.state.marine_state import MarineState

# Standard required data/calculation plans per marine intent category
INTENT_PLAN_MAPPINGS: Dict[str, List[str]] = {
    MarineIntent.FISHING_RECOMMENDATION.value: [
        "PFZ",            # Potential Fishing Zone data & convergence fronts
        "SST",            # Sea Surface Temperature gradients
        "weather",        # Wind speed and surface meteorology
        "waves",          # Significant wave height and swell conditions
        "tide",           # Tidal currents and water levels
        "restrictions",   # Marine protected zones, international maritime boundaries
    ],
    MarineIntent.PFZ_SEARCH.value: [
        "PFZ",
        "SST",
        "chlorophyll",
        "ocean_color_fronts",
        "weather",
    ],
    MarineIntent.MARINE_SAFETY.value: [
        "weather",
        "waves",
        "wind",
        "swell",
        "hazard_bulletins",
        "risk_score",
    ],
    MarineIntent.WEATHER_QUERY.value: [
        "weather",
        "waves",
        "wind",
        "swell",
        "tide",
        "surface_meteorology",
    ],
    MarineIntent.HAZARD_QUERY.value: [
        "hazard_bulletins",
        "cyclone_track",
        "high_swell_warnings",
        "wind_gusts",
        "evacuation_advisories",
    ],
    MarineIntent.GEOFENCE_QUERY.value: [
        "geofence_boundaries",
        "mpa_zones",
        "international_maritime_boundary",
        "exclusion_zones",
    ],
    MarineIntent.ROUTE_QUERY.value: [
        "route_weather",
        "waves_along_track",
        "bathymetry_depth",
        "navigation_hazards",
        "currents",
    ],
    MarineIntent.VESSEL_QUERY.value: [
        "vessel_tracking",
        "ais_positions",
        "speed_heading",
        "collision_risk",
    ],
    MarineIntent.HISTORICAL_ANALYSIS.value: [
        "historical_observations",
        "climatology_baseline",
        "trend_analysis",
        "seasonal_anomalies",
    ],
    MarineIntent.GENERAL_MARINE_QUERY.value: [
        "weather",
        "general_marine_context",
    ],
}


async def planner_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the plan of required information and analytics.
    Maps intent and extracted variables into an ordered plan.
    """
    intent = state.get("intent") or MarineIntent.GENERAL_MARINE_QUERY.value
    variables = state.get("variables", []) or []

    # Retrieve baseline required information plan for the classified intent
    base_plan = INTENT_PLAN_MAPPINGS.get(
        intent,
        INTENT_PLAN_MAPPINGS[MarineIntent.GENERAL_MARINE_QUERY.value]
    )
    plan_steps = list(base_plan)

    # Dynamically augment plan with specific user-requested variables
    for var in variables:
        var_lower = str(var).lower()
        if var_lower in ("chlorophyll", "chla") and "chlorophyll" not in plan_steps:
            plan_steps.append("chlorophyll")
        elif var_lower in ("tide",) and "tide" not in plan_steps:
            plan_steps.append("tide")
        elif var_lower in ("current",) and "currents" not in plan_steps and "current" not in plan_steps:
            plan_steps.append("currents")
        elif var_lower in ("vessel_activity", "ais") and "vessel_tracking" not in plan_steps:
            plan_steps.append("vessel_tracking")

    return {
        "plan": plan_steps,
    }


# Backwards compatibility alias
planner = planner_node
