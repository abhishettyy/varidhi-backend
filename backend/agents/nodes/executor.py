"""Executor node: executes planned steps by invoking P4 tools and P6 marine analytics."""

from typing import Any, Dict, List

from backend.agents.interfaces.p4_tools import get_p4_provider
from backend.agents.interfaces.p6_analytics import get_p6_provider
from backend.agents.schemas.plan import ToolExecutionTarget
from backend.agents.state.agent_state import AgentState


async def executor_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Safely dispatches plan steps to P4 tool integrations and P6 analytics modules.
    Maintains isolation by delegating via the abstract interface protocols.
    """
    plan = state.get("execution_plan")
    errors = list(state.get("errors", []))
    tool_results: List[Dict[str, Any]] = list(state.get("tool_results", []))
    analytics_results: List[Dict[str, Any]] = list(state.get("analytics_results", []))

    if not plan or not plan.steps:
        return {"tool_results": tool_results, "analytics_results": analytics_results}

    p4_provider = get_p4_provider()
    p6_provider = get_p6_provider()

    # Step-by-step intermediate cache
    step_outputs: Dict[str, Any] = {}

    for step in plan.steps:
        try:
            if step.target == ToolExecutionTarget.P4_EXTERNAL_TOOL:
                op = step.operation_name
                params = step.parameters

                if op == "fetch_ocean_weather":
                    res = await p4_provider.fetch_ocean_weather(
                        location=params.get("location", {}),
                        forecast_horizon_hours=params.get("forecast_horizon_hours", 24)
                    )
                elif op == "fetch_sst_data":
                    res = await p4_provider.fetch_sst_data(
                        location=params.get("location", {}),
                        timeframe=params.get("timeframe")
                    )
                elif op == "fetch_chlorophyll_data":
                    res = await p4_provider.fetch_chlorophyll_data(
                        location=params.get("location", {}),
                        timeframe=params.get("timeframe")
                    )
                elif op == "fetch_hazard_bulletins":
                    res = await p4_provider.fetch_hazard_bulletins(
                        location=params.get("location", {})
                    )
                else:
                    res = {"status": "warning", "message": f"Unknown P4 operation {op}"}

                step_outputs[step.step_id] = res
                tool_results.append({
                    "step_id": step.step_id,
                    "operation": op,
                    "result": res,
                })

            elif step.target == ToolExecutionTarget.P6_MARINE_ANALYTICS:
                op = step.operation_name
                params = step.parameters

                if op == "calculate_sea_state_risk":
                    # Inject weather data output from prerequisite step if available
                    weather_data = step_outputs.get("step_weather", {})
                    res = await p6_provider.calculate_sea_state_risk(
                        weather_data=weather_data,
                        vessel_type=params.get("vessel_type", "small_motorized_boat")
                    )
                elif op == "compute_pfz_zones":
                    sst_data = step_outputs.get("step_sst", {})
                    chlorophyll_data = step_outputs.get("step_chlorophyll", {})
                    res = await p6_provider.compute_pfz_zones(
                        sst_data=sst_data,
                        chlorophyll_data=chlorophyll_data,
                        spatial_bounds=params.get("spatial_bounds")
                    )
                elif op == "detect_algal_bloom_risk":
                    water_data = step_outputs.get("step_chlorophyll", {})
                    res = await p6_provider.detect_algal_bloom_risk(
                        water_quality_data=water_data,
                        spatial_bounds=params.get("spatial_bounds")
                    )
                else:
                    res = {"status": "warning", "message": f"Unknown P6 operation {op}"}

                step_outputs[step.step_id] = res
                analytics_results.append({
                    "step_id": step.step_id,
                    "operation": op,
                    "result": res,
                })

        except Exception as e:
            err_msg = f"Execution error in {step.step_id} ({step.operation_name}): {str(e)}"
            errors.append(err_msg)
            if step.is_required:
                # Continue loop to collect whatever else succeeds or allow fallback
                pass

    return {
        "tool_results": tool_results,
        "analytics_results": analytics_results,
        "errors": errors,
    }
