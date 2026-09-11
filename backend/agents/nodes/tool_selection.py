"""Tool selection node: validates operation prerequisites and prepares invocation payloads."""

from typing import Any, Dict, List
from backend.agents.schemas.plan import PlanStep, ToolExecutionTarget
from backend.agents.state.marine_state import MarineState


async def tool_selection_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Validates tools and prepares invocation steps from the plan.
    Canonical execution flow uses ExecutionPlan.steps directly as the single source of truth.
    Legacy list-of-strings plans are supported solely as a backward-compatibility fallback.
    """
    exec_plan = state.get("execution_plan")
    plan = state.get("plan")
    location = state.get("location") or {}
    errors = list(state.get("errors", []))

    prepared_steps: List[PlanStep] = []

    # 1. Canonical source of truth: ExecutionPlan
    if exec_plan and getattr(exec_plan, "steps", None):
        # Direct pass-through preserving id, step_id, type, operation, depends_on, input_policy, required, parameters, target
        prepared_steps = list(exec_plan.steps)

    # 2. Backward compatibility fallback: translate legacy plan string tokens only if execution_plan is absent
    elif isinstance(plan, list) and len(plan) > 0:
        seen_ids = set()
        for item in plan:
            item_str = str(item).upper()
            if ("WEATHER" in item_str or "WIND" in item_str) and "step_weather" not in seen_ids:
                seen_ids.add("step_weather")
                prepared_steps.append(
                    PlanStep(
                        id="step_weather",
                        step_id="step_weather",
                        title="Fetch Ocean Weather",
                        description="Retrieve wind and surface conditions",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation="fetch_ocean_weather",
                        operation_name="fetch_ocean_weather",
                        parameters={"location": location},
                    )
                )
            elif "SST" in item_str and "step_sst" not in seen_ids:
                seen_ids.add("step_sst")
                prepared_steps.append(
                    PlanStep(
                        id="step_sst",
                        step_id="step_sst",
                        title="Fetch Sea Surface Temperature",
                        description="Retrieve SST thermal fronts",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation="fetch_sst_data",
                        operation_name="fetch_sst_data",
                        parameters={"location": location},
                    )
                )
            elif ("PFZ" in item_str or "CHLOROPHYLL" in item_str):
                if "step_chlorophyll" not in seen_ids:
                    seen_ids.add("step_chlorophyll")
                    prepared_steps.append(
                        PlanStep(
                            id="step_chlorophyll",
                            step_id="step_chlorophyll",
                            title="Fetch Chlorophyll-a",
                            description="Retrieve phytoplankton density",
                            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                            operation="fetch_chlorophyll_data",
                            operation_name="fetch_chlorophyll_data",
                            parameters={"location": location},
                        )
                    )
                if "step_pfz_calc" not in seen_ids:
                    seen_ids.add("step_pfz_calc")
                    prepared_steps.append(
                        PlanStep(
                            id="step_pfz_calc",
                            step_id="step_pfz_calc",
                            title="Compute PFZ Hotspots",
                            description="Calculate biological convergence",
                            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                            operation="compute_pfz_zones",
                            operation_name="compute_pfz_zones",
                            parameters={"spatial_bounds": location},
                        )
                    )
            elif ("WAVES" in item_str or "RISK" in item_str) and "step_risk_calc" not in seen_ids:
                seen_ids.add("step_risk_calc")
                prepared_steps.append(
                    PlanStep(
                        id="step_risk_calc",
                        step_id="step_risk_calc",
                        title="Calculate Sea State Risk",
                        description="Compute vessel safety index",
                        target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
                        operation="calculate_sea_state_risk",
                        operation_name="calculate_sea_state_risk",
                        parameters={"vessel_type": "small_motorized_boat"},
                    )
                )
            elif "HAZARD" in item_str and "step_hazards" not in seen_ids:
                seen_ids.add("step_hazards")
                prepared_steps.append(
                    PlanStep(
                        id="step_hazards",
                        step_id="step_hazards",
                        title="Fetch Hazard Bulletins",
                        description="Retrieve meteorological bulletins",
                        target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                        operation="fetch_hazard_bulletins",
                        operation_name="fetch_hazard_bulletins",
                        parameters={"location": location},
                    )
                )

        if not prepared_steps:
            prepared_steps.append(
                PlanStep(
                    id="step_weather",
                    step_id="step_weather",
                    title="Fetch Baseline Weather",
                    description="Default weather check",
                    target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                    operation="fetch_ocean_weather",
                    operation_name="fetch_ocean_weather",
                    parameters={"location": location},
                )
            )

    # If genuinely no execution_plan AND no legacy plan was provided
    elif not exec_plan:
        prepared_steps.append(
            PlanStep(
                id="step_weather",
                step_id="step_weather",
                title="Fetch Baseline Weather",
                description="Default weather check",
                target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
                operation="fetch_ocean_weather",
                operation_name="fetch_ocean_weather",
                parameters={"location": location},
            )
        )

    return {
        "execution_steps": prepared_steps,
        "errors": errors,
    }
