"""Planning node: constructs an ordered execution plan of P4 tools and P6 calculations."""

import uuid
from typing import Any, Dict, List

from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.plan import ExecutionPlan, PlanStep, ToolExecutionTarget
from backend.agents.state.agent_state import AgentState


async def planning_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the step-by-step data retrieval and calculation plan.
    """
    intent_result = state.get("intent_result")
    spatiotemporal = state.get("spatiotemporal_context")

    intent = intent_result.primary_intent if intent_result else MarineIntent.GENERAL_MARINE_QUERY
    spatial_dict = spatiotemporal.spatial.model_dump() if spatiotemporal else {}
    temporal_dict = spatiotemporal.temporal.model_dump() if spatiotemporal else {}

    steps: List[PlanStep] = []
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"

    if intent == MarineIntent.POTENTIAL_FISHING_ZONE:
        # Step 1: Fetch Weather (P4)
        steps.append(
            PlanStep(
                step_id="step_weather",
                title="Fetch Marine Weather & Sea State",
                description="Retrieve wind speeds, wave heights, and swell conditions.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_ocean_weather",
                parameters={"location": spatial_dict, "forecast_horizon_hours": temporal_dict.get("forecast_horizon_hours", 24)},
                is_required=True,
            )
        )
        # Step 2: Fetch SST (P4)
        steps.append(
            PlanStep(
                step_id="step_sst",
                title="Fetch Sea Surface Temperature (SST)",
                description="Retrieve thermal front and SST gradient data.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_sst_data",
                parameters={"location": spatial_dict, "timeframe": temporal_dict},
                is_required=True,
            )
        )
        # Step 3: Fetch Chlorophyll (P4)
        steps.append(
            PlanStep(
                step_id="step_chlorophyll",
                title="Fetch Chlorophyll-a Ocean Color",
                description="Retrieve phytoplankton density and oceanic productivity layers.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_chlorophyll_data",
                parameters={"location": spatial_dict, "timeframe": temporal_dict},
                is_required=True,
            )
        )
        # Step 4: Calculate Sea State Risk (P6)
        steps.append(
            PlanStep(
                step_id="step_risk_calc",
                title="Calculate Sea State Risk Index",
                description="Deterministic safety validation prior to recommending fishing zones.",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                operation_name="calculate_sea_state_risk",
                parameters={"vessel_type": "small_motorized_boat"},
                depends_on=["step_weather"],
                is_required=True,
            )
        )
        # Step 5: Compute PFZ Hotspots (P6)
        steps.append(
            PlanStep(
                step_id="step_pfz_calc",
                title="Compute Potential Fishing Zone Hotspots",
                description="Identify thermal-chlorophyll convergence zones and target species.",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                operation_name="compute_pfz_zones",
                parameters={"spatial_bounds": spatial_dict},
                depends_on=["step_sst", "step_chlorophyll", "step_risk_calc"],
                is_required=True,
            )
        )

    elif intent in (MarineIntent.OCEAN_WEATHER_SAFETY, MarineIntent.HAZARD_ALERT):
        steps.append(
            PlanStep(
                step_id="step_weather",
                title="Fetch Ocean Weather Conditions",
                description="Retrieve wind speed, wave height, swell period, and visibility.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_ocean_weather",
                parameters={"location": spatial_dict, "forecast_horizon_hours": temporal_dict.get("forecast_horizon_hours", 24)},
                is_required=True,
            )
        )
        steps.append(
            PlanStep(
                step_id="step_hazards",
                title="Fetch Meteorological & Marine Hazard Bulletins",
                description="Retrieve active IMD/INCOIS alert advisories.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_hazard_bulletins",
                parameters={"location": spatial_dict},
                is_required=False,
            )
        )
        steps.append(
            PlanStep(
                step_id="step_risk_calc",
                title="Compute Vessel Hazard Index",
                description="Deterministic safety scoring for coastal and deep-sea vessels.",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                operation_name="calculate_sea_state_risk",
                parameters={"vessel_type": "all_coastal_vessels"},
                depends_on=["step_weather"],
                is_required=True,
            )
        )

    elif intent == MarineIntent.WATER_QUALITY_ALGAL_BLOOM:
        steps.append(
            PlanStep(
                step_id="step_chlorophyll",
                title="Fetch Chlorophyll Data",
                description="Retrieve ocean color anomalies.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_chlorophyll_data",
                parameters={"location": spatial_dict},
                is_required=True,
            )
        )
        steps.append(
            PlanStep(
                step_id="step_hab_risk",
                title="Compute Algal Bloom Risk",
                description="Run Harmful Algal Bloom detection algorithm.",
                target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                operation_name="detect_algal_bloom_risk",
                parameters={"spatial_bounds": spatial_dict},
                depends_on=["step_chlorophyll"],
                is_required=True,
            )
        )

    else:
        # General marine inquiry - minimal observation retrieval
        steps.append(
            PlanStep(
                step_id="step_weather",
                title="Fetch General Sea State",
                description="Provide baseline environmental context.",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_ocean_weather",
                parameters={"location": spatial_dict},
                is_required=False,
            )
        )

    plan = ExecutionPlan(
        plan_id=plan_id,
        summary=f"Execution plan for {intent.value} targeting {len(steps)} operations.",
        steps=steps,
        requires_marine_safety_check=True,
        estimated_complexity="multi_source" if len(steps) > 2 else "simple",
    )

    return {
        "execution_plan": plan,
        "current_step_index": 0,
    }
