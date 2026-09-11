"""Executor node: executes planned steps by invoking P4 tools and P6 marine analytics."""

from typing import Any, Dict, List

from backend.agents.interfaces.p4_tools import get_p4_provider
from backend.agents.interfaces.p6_analytics import get_p6_provider
from backend.agents.schemas.plan import ToolExecutionTarget
from backend.agents.state.marine_state import MarineState


async def executor_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Safely dispatches plan steps to P4 tool integrations, P6 analytics modules,
    and internal synthesis steps.
    Resolves dependency outputs dynamically via step.depends_on rather than hardcoded step IDs.
    """
    plan = state.get("execution_plan")
    steps = state.get("execution_steps") or (plan.steps if plan else [])
    errors = list(state.get("errors", []))
    tool_results: List[Dict[str, Any]] = list(state.get("tool_results", []))
    analytics_results: List[Dict[str, Any]] = list(state.get("analytics_results", []))

    if not steps:
        return {"tool_results": tool_results, "analytics_results": analytics_results}

    p4_provider = get_p4_provider()
    p6_provider = get_p6_provider()

    # Dynamic step-by-step intermediate cache keyed by step ID
    step_outputs: Dict[str, Any] = {}

    for step in steps:
        step_id_key = step.id or step.step_id or "step"
        op = step.operation or step.operation_name or "unknown_op"
        params = step.parameters or {}
        depends_on = step.depends_on or []

        # Resolve declared dependency outputs dynamically
        dep_outputs = {dep_id: step_outputs.get(dep_id, {}) for dep_id in depends_on}

        try:
            if step.target == ToolExecutionTarget.P4_EXTERNAL_TOOL:
                loc = params.get("location") or params.get("route") or {}

                if op in ("fetch_ocean_weather", "get_wind", "get_wave", "get_swell", "get_tide"):
                    res = await p4_provider.fetch_ocean_weather(
                        location=loc,
                        forecast_horizon_hours=params.get("forecast_horizon_hours", 24),
                    )
                elif op in ("fetch_sst_data", "get_sst"):
                    res = await p4_provider.fetch_sst_data(
                        location=loc,
                        timeframe=params.get("requested_time") or params.get("timeframe"),
                    )
                elif op in ("fetch_chlorophyll_data", "get_chlorophyll"):
                    res = await p4_provider.fetch_chlorophyll_data(
                        location=loc,
                        timeframe=params.get("requested_time") or params.get("timeframe"),
                    )
                elif op in ("fetch_hazard_bulletins", "check_restrictions", "check_geofence"):
                    res = await p4_provider.fetch_hazard_bulletins(
                        location=loc,
                    )
                elif op in ("get_pfz", "fetch_pfz"):
                    res = {
                        "status": "success",
                        "source": "P4_MOCK_PFZ_SERVICE",
                        "data": {
                            "location": loc.get("name") if isinstance(loc, dict) else "Coastal Waters",
                            "pfz_active": True,
                        },
                    }
                elif op in ("get_vessel_position", "get_vessel_activity"):
                    res = {
                        "status": "success",
                        "source": "P4_MOCK_AIS_SERVICE",
                        "data": {
                            "vessel": params.get("vessel", {}),
                            "telemetry": {"status": "underway", "speed_knots": 10.2},
                        },
                    }
                elif op == "get_historical_data":
                    res = {
                        "status": "success",
                        "source": "P4_MOCK_HISTORICAL_ARCHIVE",
                        "data": {
                            "variable": params.get("variable", "SST"),
                            "location": loc.get("name") if isinstance(loc, dict) else "Coastal Waters",
                            "time_series_points": 30,
                        },
                    }
                else:
                    res = {
                        "status": "success",
                        "source": "P4_EXTERNAL_TOOL",
                        "operation": op,
                        "data": {"status": "completed", "parameters": params},
                    }

                step_outputs[step_id_key] = res
                if step.id:
                    step_outputs[step.id] = res
                if step.step_id:
                    step_outputs[step.step_id] = res

                tool_results.append({
                    "step_id": step_id_key,
                    "operation": op,
                    "result": res,
                })

            elif step.target == ToolExecutionTarget.P6_MARINE_ANALYTICS:
                if op in ("calculate_sea_state_risk", "calculate_marine_risk"):
                    # Aggregate weather/wave data from declared dependencies
                    weather_data = {}
                    for dep_res in dep_outputs.values():
                        if isinstance(dep_res, dict) and "data" in dep_res:
                            if not weather_data:
                                weather_data = {"status": "success", "source": "P6_AGGREGATED", "data": dict(dep_res["data"])}
                            else:
                                weather_data["data"].update(dep_res["data"])

                    if not weather_data and "step_weather" in step_outputs:
                        weather_data = step_outputs["step_weather"]

                    vessel_type = (
                        (params.get("vessel") or {}).get("type")
                        if isinstance(params.get("vessel"), dict)
                        else params.get("vessel_type", "small_motorized_boat")
                    )
                    res = await p6_provider.calculate_sea_state_risk(
                        weather_data=weather_data or {"data": {}},
                        vessel_type=vessel_type or "small_motorized_boat",
                    )
                elif op in ("compute_pfz_zones", "calculate_opportunity", "rank_zones", "calculate_distance"):
                    sst_data = {}
                    chlorophyll_data = {}
                    for dep_id, dep_res in dep_outputs.items():
                        d_lower = dep_id.lower()
                        if "sst" in d_lower or "temp" in d_lower:
                            sst_data = dep_res
                        elif "chlorophyll" in d_lower or "chla" in d_lower or "bio" in d_lower:
                            chlorophyll_data = dep_res
                        elif not sst_data:
                            sst_data = dep_res
                        elif not chlorophyll_data:
                            chlorophyll_data = dep_res

                    if not sst_data and "step_sst" in step_outputs:
                        sst_data = step_outputs["step_sst"]
                    if not chlorophyll_data and "step_chlorophyll" in step_outputs:
                        chlorophyll_data = step_outputs["step_chlorophyll"]

                    res = await p6_provider.compute_pfz_zones(
                        sst_data=sst_data or {},
                        chlorophyll_data=chlorophyll_data or {},
                        spatial_bounds=params.get("spatial_bounds") or params.get("location"),
                    )
                elif op == "detect_algal_bloom_risk":
                    water_data = {}
                    for dep_res in dep_outputs.values():
                        if dep_res:
                            water_data = dep_res
                            break
                    if not water_data and "step_chlorophyll" in step_outputs:
                        water_data = step_outputs["step_chlorophyll"]

                    res = await p6_provider.detect_algal_bloom_risk(
                        water_quality_data=water_data,
                        spatial_bounds=params.get("spatial_bounds"),
                    )
                elif op == "analyze_historical_trends":
                    res = {
                        "status": "success",
                        "source": "P6_MOCK_TREND_ENGINE",
                        "data": {
                            "trend": "stable",
                            "anomaly_detected": False,
                            "summary": "Historical variables within seasonal baseline envelope.",
                        },
                    }
                else:
                    res = {
                        "status": "success",
                        "source": "P6_MARINE_ANALYTICS",
                        "operation": op,
                        "data": {"status": "computed", "dependencies": list(dep_outputs.keys())},
                    }

                step_outputs[step_id_key] = res
                if step.id:
                    step_outputs[step.id] = res
                if step.step_id:
                    step_outputs[step.step_id] = res

                analytics_results.append({
                    "step_id": step_id_key,
                    "operation": op,
                    "result": res,
                })

            else:
                # Internal synthesis / DECISION / RESPONSE steps
                res = {
                    "status": "success",
                    "source": "P3_INTERNAL_SYNTHESIS",
                    "operation": op,
                    "data": {
                        "status": "completed",
                        "inputs": list(dep_outputs.keys()),
                    },
                }
                step_outputs[step_id_key] = res
                if step.id:
                    step_outputs[step.id] = res
                if step.step_id:
                    step_outputs[step.step_id] = res

        except Exception as e:
            err_msg = f"Execution error in {step_id_key} ({op}): {str(e)}"
            errors.append(err_msg)

    return {
        "tool_results": tool_results,
        "analytics_results": analytics_results,
        "errors": errors,
    }
