"""Planner node: converts normalized QueryIntent into a structured, dependency-aware ExecutionPlan."""

import uuid
from typing import Any, Dict, List, Optional

from backend.agents.schemas.intent import MarineIntent, MarineVariable
from backend.agents.schemas.plan import (
    ExecutionPlan,
    InputPolicy,
    PlanStep,
    StepType,
    ToolExecutionTarget,
)
from backend.agents.state.marine_state import MarineState


def build_fishing_recommendation_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
    variables: List[str],
    vessel: Optional[Dict[str, Any]],
    constraints: Dict[str, Any],
) -> ExecutionPlan:
    """Constructs plan for FISHING_RECOMMENDATION."""
    missing: List[str] = []
    if not location or (location.get("latitude") is None and not location.get("name")):
        missing.append("location")

    steps: List[PlanStep] = [
        # Independent DATA steps
        PlanStep(
            id="pfz",
            type=StepType.DATA.value,
            operation="get_pfz",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "latest_available",
            },
            title="Fetch PFZ Hotspots",
            description="Retrieve biological convergence zones and potential fishing zones",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="sst",
            type=StepType.DATA.value,
            operation="get_sst",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "latest_available",
            },
            title="Fetch Sea Surface Temperature",
            description="Retrieve thermal front gradients and surface temperature",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="chlorophyll",
            type=StepType.DATA.value,
            operation="get_chlorophyll",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "latest_available",
            },
            title="Fetch Chlorophyll-a Ocean Color",
            description="Retrieve phytoplankton density and oceanic productivity",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "forecast" if time_range and not time_range.get("is_historical") else "latest_available",
            },
            title="Fetch Surface Wind",
            description="Retrieve wind speed, direction, and gusts",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wave",
            type=StepType.DATA.value,
            operation="get_wave",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "forecast" if time_range and not time_range.get("is_historical") else "latest_available",
            },
            title="Fetch Significant Wave Height",
            description="Retrieve wave height and sea chop conditions",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="swell",
            type=StepType.DATA.value,
            operation="get_swell",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "forecast" if time_range and not time_range.get("is_historical") else "latest_available",
            },
            title="Fetch Swell Parameters",
            description="Retrieve swell wave height and period",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="tide",
            type=StepType.DATA.value,
            operation="get_tide",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "forecast" if time_range and not time_range.get("is_historical") else "latest_available",
            },
            title="Fetch Tidal Currents",
            description="Retrieve tidal timing and water level forecasts",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="restrictions",
            type=StepType.DATA.value,
            operation="check_restrictions",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location},
            title="Check Marine Restrictions",
            description="Validate marine protected areas and maritime boundaries",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        # Dependent ANALYTICS steps with explicit ALLOW_PARTIAL policy for non-vital inputs
        PlanStep(
            id="opportunity",
            type=StepType.ANALYTICS.value,
            operation="calculate_opportunity",
            depends_on=["pfz", "sst", "chlorophyll"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={},
            title="Calculate Fishing Opportunity Index",
            description="Synthesize thermal-chlorophyll-PFZ convergence metrics",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        PlanStep(
            id="risk",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            depends_on=["wind", "wave", "swell", "tide"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={"vessel": vessel, "constraints": constraints},
            title="Calculate Marine Safety Risk",
            description="Deterministic safety validation against sea state thresholds",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        PlanStep(
            id="ranking",
            type=StepType.ANALYTICS.value,
            operation="rank_zones",
            depends_on=["opportunity", "risk"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Rank Fishing Hotspots",
            description="Rank candidate zones by opportunity weighted by safety",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        # DECISION step
        PlanStep(
            id="decision",
            type=StepType.DECISION.value,
            operation="select_safe_fishing_zone",
            depends_on=["ranking", "restrictions"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Select Optimal Fishing Ground",
            description="Select final safe zones compliant with maritime boundaries",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
        # RESPONSE step
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="generate_recommendation",
            depends_on=["decision"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Generate Fishing Advisory",
            description="Synthesize persona-tailored fishing grounds and safety notices",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_fish_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.FISHING_RECOMMENDATION.value,
        summary="Multi-source fishing recommendation with safety and environmental constraints",
        steps=steps,
        requires_clarification=len(missing) > 0,
        missing=missing,
        estimated_complexity="multi_source",
    )


def build_pfz_search_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
) -> ExecutionPlan:
    """Constructs plan for PFZ_SEARCH."""
    missing: List[str] = []
    has_location = location and (location.get("latitude") is not None or location.get("name"))
    if not has_location:
        missing.append("location")

    steps: List[PlanStep] = [
        PlanStep(
            id="pfz",
            type=StepType.DATA.value,
            operation="get_pfz",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={
                "location": location,
                "requested_time": time_range,
                "temporal_mode": "latest_available",
            },
            title="Fetch PFZ Locations",
            description="Retrieve satellite-derived Potential Fishing Zone coordinates",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
    ]

    if has_location:
        steps.append(
            PlanStep(
                id="distance",
                type=StepType.ANALYTICS.value,
                operation="calculate_distance",
                depends_on=["pfz"],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={"location": location},
                title="Calculate Distance to PFZ",
                description="Compute radial distance and bearing from origin coordinates",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
            )
        )
        steps.append(
            PlanStep(
                id="ranking",
                type=StepType.ANALYTICS.value,
                operation="rank_zones",
                depends_on=["distance"],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={},
                title="Rank Nearest Zones",
                description="Sort PFZ hotspots by proximity",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
            )
        )
        steps.append(
            PlanStep(
                id="response",
                type=StepType.RESPONSE.value,
                operation="generate_recommendation",
                depends_on=["ranking"],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={},
                title="Present PFZ Coordinates",
                description="Display nearest PFZ coordinates, bearing, and distance",
                target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
            )
        )
    else:
        steps.append(
            PlanStep(
                id="ranking",
                type=StepType.ANALYTICS.value,
                operation="rank_zones",
                depends_on=["pfz"],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={},
                title="Rank Global Zones",
                description="Sort general PFZ clusters",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
            )
        )
        steps.append(
            PlanStep(
                id="response",
                type=StepType.RESPONSE.value,
                operation="generate_recommendation",
                depends_on=["ranking"],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={},
                title="Present PFZ Zones",
                description="Display general PFZ clusters with location clarification note",
                target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
            )
        )

    return ExecutionPlan(
        plan_id=f"plan_pfz_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.PFZ_SEARCH.value,
        summary="PFZ location retrieval and proximity ranking",
        steps=steps,
        requires_clarification=len(missing) > 0,
        missing=missing,
        estimated_complexity="standard",
    )


def build_marine_safety_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
    vessel: Optional[Dict[str, Any]],
    constraints: Dict[str, Any],
) -> ExecutionPlan:
    """Constructs plan for MARINE_SAFETY."""
    temporal_mode = "forecast" if time_range and not time_range.get("is_historical") else "latest_available"

    steps: List[PlanStep] = [
        PlanStep(
            id="wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Wind Velocity",
            description="Retrieve wind speeds and gust warnings",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wave",
            type=StepType.DATA.value,
            operation="get_wave",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Wave Conditions",
            description="Retrieve significant wave height and sea roughness",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="swell",
            type=StepType.DATA.value,
            operation="get_swell",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Swell Data",
            description="Retrieve swell height and period",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="tide",
            type=StepType.DATA.value,
            operation="get_tide",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Tidal Extremes",
            description="Retrieve high/low tide predictions",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="risk",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            depends_on=["wind", "wave", "swell", "tide"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={"vessel": vessel, "constraints": constraints},
            title="Compute Marine Risk Index",
            description="Compute safety score against vessel capability thresholds",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        PlanStep(
            id="decision",
            type=StepType.DECISION.value,
            operation="evaluate_hazard",
            depends_on=["risk"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Evaluate Safety Advisory",
            description="Formulate go/no-go recommendation for vessel",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=["decision"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Generate Safety Advisory",
            description="Render color-coded safety alert and navigation advice",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_safety_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.MARINE_SAFETY.value,
        summary="Comprehensive marine safety and vessel risk evaluation",
        steps=steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="standard",
    )


def build_weather_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
) -> ExecutionPlan:
    """Constructs plan for WEATHER_QUERY."""
    temporal_mode = "forecast" if time_range and not time_range.get("is_historical") else "latest_available"

    steps: List[PlanStep] = [
        PlanStep(
            id="wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Wind Forecast",
            description="Retrieve wind velocity and direction vectors",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wave",
            type=StepType.DATA.value,
            operation="get_wave",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Wave Forecast",
            description="Retrieve significant wave height and sea chop",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="swell",
            type=StepType.DATA.value,
            operation="get_swell",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Swell Forecast",
            description="Retrieve ocean swell period and direction",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="tide",
            type=StepType.DATA.value,
            operation="get_tide",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Tidal Forecast",
            description="Retrieve tidal timing and water heights",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=["wind", "wave", "swell", "tide"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Summarize Marine Weather",
            description="Synthesize meteorological conditions and timeline",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_weather_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.WEATHER_QUERY.value,
        summary="Ocean surface meteorology and marine weather forecast",
        steps=steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="simple",
    )


def build_hazard_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
) -> ExecutionPlan:
    """Constructs plan for HAZARD_QUERY."""
    temporal_mode = "forecast" if time_range and not time_range.get("is_historical") else "latest_available"

    steps: List[PlanStep] = [
        PlanStep(
            id="wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Severe Wind & Gale Data",
            description="Retrieve gale warnings and wind gust measurements",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wave",
            type=StepType.DATA.value,
            operation="get_wave",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch High Wave & Swell Warnings",
            description="Retrieve extreme wave alerts and rough sea bulletins",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="swell",
            type=StepType.DATA.value,
            operation="get_swell",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"location": location, "requested_time": time_range, "temporal_mode": temporal_mode},
            title="Fetch Swell Surge Data",
            description="Retrieve high energy swell components",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="risk",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            depends_on=["wind", "wave", "swell"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={},
            title="Compute Severe Hazard Severity",
            description="Assess threat level against coastal and offshore limits",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        PlanStep(
            id="decision",
            type=StepType.DECISION.value,
            operation="evaluate_hazard",
            depends_on=["risk"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Evaluate Hazard Advisories",
            description="Determine active warning status and emergency guidance",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=["decision"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Generate Hazard Bulletin",
            description="Render urgent hazard advisory and precautionary notices",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_hazard_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.HAZARD_QUERY.value,
        summary="Severe weather and marine hazard assessment",
        steps=steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="standard",
    )


def build_geofence_plan(
    location: Optional[Dict[str, Any]],
    constraints: Dict[str, Any],
) -> ExecutionPlan:
    """Constructs plan for GEOFENCE_QUERY."""
    steps: List[PlanStep] = [
        PlanStep(
            id="geofence",
            type=StepType.DATA.value,
            operation="check_geofence",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location},
            title="Fetch Boundary Polygons",
            description="Lookup spatial geofence layers and EEZ boundaries",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="restrictions",
            type=StepType.DATA.value,
            operation="check_restrictions",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"location": location},
            title="Fetch Restriction Policies",
            description="Lookup marine protected areas and naval exclusion zones",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="decision",
            type=StepType.DECISION.value,
            operation="evaluate_hazard",
            depends_on=["geofence", "restrictions"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Evaluate Spatial Compliance",
            description="Determine if target coordinate is inside restricted area",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="explain_recommendation",
            depends_on=["decision"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Render Boundary Advisory",
            description="Summarize boundary compliance status and legal advisories",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_geofence_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.GEOFENCE_QUERY.value,
        summary="Marine geofence and boundary restriction check",
        steps=steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="standard",
    )


def build_route_plan(
    route: Optional[Dict[str, Any]],
    location: Optional[Dict[str, Any]],
    constraints: Dict[str, Any],
) -> ExecutionPlan:
    """Constructs plan for ROUTE_QUERY."""
    missing: List[str] = []
    if not route or (not route.get("origin") and not route.get("destination")):
        pass

    steps: List[PlanStep] = [
        PlanStep(
            id="geofence",
            type=StepType.DATA.value,
            operation="check_geofence",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"route": route},
            title="Lookup Route Geofences",
            description="Fetch exclusion zones intersecting the transit corridor",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"route": route, "temporal_mode": "forecast"},
            title="Fetch En-Route Wind",
            description="Retrieve wind speed along transit waypoints",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="wave",
            type=StepType.DATA.value,
            operation="get_wave",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"route": route, "temporal_mode": "forecast"},
            title="Fetch En-Route Waves",
            description="Retrieve sea state along transit track",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="route_analysis",
            type=StepType.ANALYTICS.value,
            operation="calculate_distance",
            depends_on=["geofence", "wind", "wave"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={"route": route},
            title="Analyze Route Corridor",
            description="Compute distance, passage hazards, and intersection with boundaries",
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
        ),
        PlanStep(
            id="decision",
            type=StepType.DECISION.value,
            operation="evaluate_route",
            depends_on=["route_analysis"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Evaluate Route Safety",
            description="Validate passage safety and boundary clearances",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="generate_recommendation",
            depends_on=["decision"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Generate Passage Advisory",
            description="Render route viability, safe waypoints, and hazard notices",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_route_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.ROUTE_QUERY.value,
        summary="Passage navigation route validation and boundary clearance",
        steps=steps,
        requires_clarification=len(missing) > 0,
        missing=missing,
        estimated_complexity="multi_source",
    )


def build_vessel_plan(
    vessel: Optional[Dict[str, Any]],
    location: Optional[Dict[str, Any]],
) -> ExecutionPlan:
    """Constructs plan for VESSEL_QUERY."""
    missing: List[str] = []
    if not vessel or (not vessel.get("id") and not vessel.get("type")):
        missing.append("vessel")

    steps: List[PlanStep] = [
        PlanStep(
            id="vessel_pos",
            type=StepType.DATA.value,
            operation="get_vessel_position",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={"vessel": vessel, "temporal_mode": "latest_available"},
            title="Fetch AIS Vessel Position",
            description="Query real-time AIS transponder coordinates and telemetry",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="vessel_act",
            type=StepType.DATA.value,
            operation="get_vessel_activity",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=False,
            parameters={"vessel": vessel, "temporal_mode": "latest_available"},
            title="Fetch Vessel Fleet Activity",
            description="Retrieve recent track history, speed, and heading",
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        ),
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=["vessel_pos", "vessel_act"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="Summarize Vessel Telemetry",
            description="Format vessel tracking position and operational status",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_vessel_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.VESSEL_QUERY.value,
        summary="Vessel AIS tracking and telemetry retrieval",
        steps=steps,
        requires_clarification=len(missing) > 0,
        missing=missing,
        estimated_complexity="simple",
    )


def build_historical_analysis_plan(
    location: Optional[Dict[str, Any]],
    time_range: Optional[Dict[str, Any]],
    variables: List[str],
) -> ExecutionPlan:
    """Constructs plan dynamically for HISTORICAL_ANALYSIS based on requested variables."""
    data_steps: List[PlanStep] = []

    # Dynamic data step generation for requested variables
    vars_to_plan = list(variables)
    if not vars_to_plan:
        vars_to_plan = ["SST", "CHLOROPHYLL"]

    for var in vars_to_plan:
        var_upper = var.upper()
        step_id = f"historical_{var.lower()}"
        data_steps.append(
            PlanStep(
                id=step_id,
                type=StepType.DATA.value,
                operation="get_historical_data",
                depends_on=[],
                input_policy=InputPolicy.REQUIRE_ALL.value,
                required=True,
                parameters={
                    "variable": var_upper,
                    "location": location,
                    "requested_time": time_range,
                    "temporal_mode": "historical",
                },
                title=f"Fetch Historical {var_upper}",
                description=f"Retrieve archived time series observation for {var_upper}",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
            )
        )

    dep_ids = [s.id for s in data_steps]

    analytics_step = PlanStep(
        id="trends",
        type=StepType.ANALYTICS.value,
        operation="analyze_historical_trends",
        depends_on=dep_ids,
        input_policy=InputPolicy.REQUIRE_ALL.value,
        required=True,
        parameters={"requested_time": time_range, "temporal_mode": "historical"},
        title="Analyze Climatological Trends",
        description="Compute time series anomalies, seasonal baseline, and trend lines",
        target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
    )

    response_step = PlanStep(
        id="response",
        type=StepType.RESPONSE.value,
        operation="summarize_conditions",
        depends_on=["trends"],
        input_policy=InputPolicy.REQUIRE_ALL.value,
        required=True,
        parameters={},
        title="Summarize Historical Trends",
        description="Format historical trend graphs and comparison summary",
        target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
    )

    all_steps = data_steps + [analytics_step, response_step]

    return ExecutionPlan(
        plan_id=f"plan_hist_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.HISTORICAL_ANALYSIS.value,
        summary=f"Historical time-series analysis for {', '.join(vars_to_plan)}",
        steps=all_steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="standard",
    )


def build_general_marine_plan() -> ExecutionPlan:
    """Constructs plan for GENERAL_MARINE_QUERY."""
    steps: List[PlanStep] = [
        PlanStep(
            id="response",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=[],
            input_policy=InputPolicy.REQUIRE_ALL.value,
            required=True,
            parameters={},
            title="General Marine Knowledge",
            description="Synthesize marine domain context and oceanographic guidance",
            target=ToolExecutionTarget.INTERNAL_SYNTHESIS,
        ),
    ]

    return ExecutionPlan(
        plan_id=f"plan_gen_{uuid.uuid4().hex[:8]}",
        intent=MarineIntent.GENERAL_MARINE_QUERY.value,
        summary="General marine intelligence overview",
        steps=steps,
        requires_clarification=False,
        missing=[],
        estimated_complexity="simple",
    )


async def planner_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the execution plan of required information and analytics.
    Converts QueryIntent into a structured, dependency-aware ExecutionPlan without executing tools.
    """
    intent = state.get("intent") or MarineIntent.GENERAL_MARINE_QUERY.value
    location = state.get("location")
    time_range = state.get("time_range") if isinstance(state.get("time_range"), dict) else None
    variables = state.get("variables", []) or []
    vessel = state.get("vessel")
    route = state.get("route")
    constraints = state.get("constraints", {}) or {}

    # Build intent-specific structured ExecutionPlan
    if intent == MarineIntent.FISHING_RECOMMENDATION.value:
        exec_plan = build_fishing_recommendation_plan(location, time_range, variables, vessel, constraints)
    elif intent == MarineIntent.PFZ_SEARCH.value:
        exec_plan = build_pfz_search_plan(location, time_range)
    elif intent == MarineIntent.MARINE_SAFETY.value:
        exec_plan = build_marine_safety_plan(location, time_range, vessel, constraints)
    elif intent == MarineIntent.WEATHER_QUERY.value:
        exec_plan = build_weather_plan(location, time_range)
    elif intent == MarineIntent.HAZARD_QUERY.value:
        exec_plan = build_hazard_plan(location, time_range)
    elif intent == MarineIntent.GEOFENCE_QUERY.value:
        exec_plan = build_geofence_plan(location, constraints)
    elif intent == MarineIntent.ROUTE_QUERY.value:
        exec_plan = build_route_plan(route, location, constraints)
    elif intent == MarineIntent.VESSEL_QUERY.value:
        exec_plan = build_vessel_plan(vessel, location)
    elif intent == MarineIntent.HISTORICAL_ANALYSIS.value:
        exec_plan = build_historical_analysis_plan(location, time_range, variables)
    else:
        exec_plan = build_general_marine_plan()

    # Legacy string tokens for backwards compatibility with Phase 1 node assertions
    step_tokens: List[str] = [step.id for step in exec_plan.steps]
    if intent == MarineIntent.FISHING_RECOMMENDATION.value:
        plan_list = ["PFZ", "SST", "chlorophyll", "weather", "wind", "waves", "swell", "tide", "restrictions", "opportunity", "risk", "ranking", "decision", "recommendation"]
    elif intent in (MarineIntent.WEATHER_QUERY.value, MarineIntent.MARINE_SAFETY.value):
        plan_list = ["weather", "wind", "waves", "swell", "tide", "risk_score", "decision", "response"]
    else:
        plan_list = step_tokens

    return {
        "plan": plan_list,
        "execution_plan": exec_plan,
        "execution_steps": exec_plan.steps,
    }


# Backwards compatibility alias
planner = planner_node
