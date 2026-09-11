"""Tool selection node: validates operation prerequisites and prepares invocation payloads."""

from typing import Any, Dict, List
from backend.agents.schemas.plan import PlanStep, ToolExecutionTarget
from backend.agents.state.marine_state import MarineState


async def tool_selection_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Validates tools and prepares invocation steps from the plan.
    Supports both list-of-strings plans (e.g. ['PFZ', 'SST', 'weather']) and ExecutionPlan objects.
    """
    plan = state.get("plan")
    exec_plan = state.get("execution_plan")
    location = state.get("location") or {}
    errors = list(state.get("errors", []))

    prepared_steps: List[PlanStep] = []

    if isinstance(plan, list) and len(plan) > 0:
        for item in plan:
            item_str = str(item).upper()
            if "WEATHER" in item_str or "WIND" in item_str:
                prepared_steps.append(
                    PlanStep(
                        step_id="step_weather",
                        title="Fetch Ocean Weather",
                        description="Retrieve wind and surface conditions",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation_name="fetch_ocean_weather",
                        parameters={"location": location},
                    )
                )
            elif "SST" in item_str:
                prepared_steps.append(
                    PlanStep(
                        step_id="step_sst",
                        title="Fetch Sea Surface Temperature",
                        description="Retrieve SST thermal fronts",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation_name="fetch_sst_data",
                        parameters={"location": location},
                    )
                )
            elif "PFZ" in item_str or "CHLOROPHYLL" in item_str:
                prepared_steps.append(
                    PlanStep(
                        step_id="step_chlorophyll",
                        title="Fetch Chlorophyll-a",
                        description="Retrieve phytoplankton density",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation_name="fetch_chlorophyll_data",
                        parameters={"location": location},
                    )
                )
                prepared_steps.append(
                    PlanStep(
                        step_id="step_pfz_calc",
                        title="Compute PFZ Hotspots",
                        description="Calculate biological convergence",
                        target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                        operation_name="compute_pfz_zones",
                        parameters={"spatial_bounds": location},
                    )
                )
            elif "WAVES" in item_str or "RISK" in item_str:
                prepared_steps.append(
                    PlanStep(
                        step_id="step_risk_calc",
                        title="Calculate Sea State Risk",
                        description="Compute vessel safety index",
                        target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                        operation_name="calculate_sea_state_risk",
                        parameters={"vessel_type": "small_motorized_boat"},
                    )
                )
            elif "HAZARD" in item_str:
                prepared_steps.append(
                    PlanStep(
                        step_id="step_hazards",
                        title="Fetch Hazard Bulletins",
                        description="Retrieve meteorological bulletins",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation_name="fetch_hazard_bulletins",
                        parameters={"location": location},
                    )
                )

    elif exec_plan and exec_plan.steps:
        prepared_steps = exec_plan.steps

    # If no specific steps could be resolved, add default baseline observation
    if not prepared_steps:
        prepared_steps.append(
            PlanStep(
                step_id="step_weather",
                title="Fetch Baseline Weather",
                description="Default weather check",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation_name="fetch_ocean_weather",
                parameters={"location": location},
            )
        )

    return {
        "execution_steps": prepared_steps,
        "errors": errors,
    }
