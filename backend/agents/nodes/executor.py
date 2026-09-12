"""Generic dependency-aware executor node backed by mock tool registry and P4/P6 interface bridges."""

import asyncio
from typing import Any, Dict, List, Optional, Set

from backend.agents.mocks.tool_registry import get_tool_registry
from backend.agents.schemas.plan import (
    InputPolicy,
    PlanStep,
    StepType,
    ToolExecutionTarget,
)
from backend.agents.state.marine_state import MarineState


def detect_cycles(steps: List[PlanStep]) -> Optional[List[str]]:
    """
    Detects if there are any dependency cycles in the execution plan.
    Returns the list of cyclic node IDs if a cycle is detected, else None.
    """
    adj: Dict[str, List[str]] = {s.id: list(s.depends_on) for s in steps}
    visited: Dict[str, int] = {}  # 0: visiting, 1: visited
    cycle_nodes: List[str] = []

    def dfs(node: str, path: List[str]) -> bool:
        visited[node] = 0
        for neighbor in adj.get(node, []):
            if neighbor not in adj:
                continue
            if visited.get(neighbor) == 0:
                cycle_nodes.extend(path + [neighbor])
                return True
            if neighbor not in visited:
                if dfs(neighbor, path + [neighbor]):
                    return True
        visited[node] = 1
        return False

    for step in steps:
        if step.id not in visited:
            if dfs(step.id, [step.id]):
                return cycle_nodes
    return None


async def execute_single_step(
    step: PlanStep,
    step_outputs: Dict[str, Any],
    registry: Any,
) -> Dict[str, Any]:
    """
    Executes a single step given intermediate outputs of its declared dependencies,
    enforcing InputPolicy (REQUIRE_ALL, ALLOW_PARTIAL, OPTIONAL).
    """
    op = step.operation or step.operation_name or "unknown_operation"
    params = step.parameters or {}
    depends_on = step.depends_on or []

    # Gather available outputs of declared dependencies
    dep_outputs = {dep_id: step_outputs[dep_id] for dep_id in depends_on if dep_id in step_outputs}

    # Identify failed, blocked, or missing dependencies
    failed_deps = [
        dep_id for dep_id in depends_on
        if dep_id not in step_outputs or step_outputs[dep_id].get("status") in ("failed", "blocked")
    ]

    policy = step.input_policy or InputPolicy.REQUIRE_ALL.value

    # 1. Enforce REQUIRE_ALL
    if failed_deps and policy == InputPolicy.REQUIRE_ALL.value:
        return {
            "status": "blocked",
            "source": "mock",
            "operation": op,
            "error": f"Required dependency failed/missing: {failed_deps}",
            "data": {},
            "dependencies": depends_on,
            "partial": False,
        }

    # 2. Enforce ALLOW_PARTIAL or OPTIONAL
    is_partial = False
    if failed_deps and policy in (InputPolicy.ALLOW_PARTIAL.value, InputPolicy.OPTIONAL.value):
        is_partial = True

    # Execute via generic tool registry
    res = await registry.execute(
        operation=op,
        parameters=params,
        dependencies=dep_outputs,
    )

    if is_partial:
        res["partial"] = True
        res["missing_dependencies"] = failed_deps

    return res


import time

async def executor_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Generic, dependency-aware DAG executor.
    - Resolves execution order dynamically based on step.depends_on.
    - Detects dependency cycles without getting stuck.
    - Dispatches execution to the ToolRegistry.
    - Explicitly passes dependency outputs to downstream steps.
    - Enforces InputPolicy (REQUIRE_ALL, ALLOW_PARTIAL, OPTIONAL).
    - Maintains state compatibility for downstream evidence assembly & response generation.
    - Measures individual tool execution latencies and parallel DAG duration.
    """
    t0 = time.perf_counter()
    plan = state.get("execution_plan")
    steps: List[PlanStep] = state.get("execution_steps") or (plan.steps if plan else [])
    errors: List[str] = list(state.get("errors") or [])
    tool_results: List[Dict[str, Any]] = list(state.get("tool_results") or [])
    analytics_results: List[Dict[str, Any]] = list(state.get("analytics_results") or [])
    tool_timings_ms: Dict[str, float] = {}

    if not steps:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        latency_telemetry = dict(state.get("latency_telemetry") or {})
        latency_telemetry["executor_ms"] = latency_ms
        latency_telemetry["tool_timings_ms"] = tool_timings_ms
        return {
            "tool_results": tool_results,
            "analytics_results": analytics_results,
            "errors": errors,
            "latency_telemetry": latency_telemetry,
        }

    # 1. Check for dependency cycles
    cycle = detect_cycles(steps)
    if cycle:
        err_msg = f"Dependency cycle detected in execution plan: {' -> '.join(cycle)}"
        errors.append(err_msg)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        latency_telemetry = dict(state.get("latency_telemetry") or {})
        latency_telemetry["executor_ms"] = latency_ms
        latency_telemetry["tool_timings_ms"] = tool_timings_ms
        return {
            "tool_results": tool_results,
            "analytics_results": analytics_results,
            "errors": errors,
            "latency_telemetry": latency_telemetry,
        }

    registry = get_tool_registry()

    # Intermediate output cache keyed by step ID
    step_outputs: Dict[str, Any] = {}
    completed_steps: Set[str] = set()
    steps_map: Dict[str, PlanStep] = {s.id: s for s in steps}

    # 2. Dynamic DAG scheduling loop
    while len(completed_steps) < len(steps):
        # Find all steps whose declared dependencies have been fulfilled
        ready_steps = [
            s for s in steps
            if s.id not in completed_steps
            and all(dep in step_outputs for dep in s.depends_on if dep in steps_map)
        ]

        if not ready_steps:
            # Stalled due to unresolvable or missing dependencies
            unresolved = [s for s in steps if s.id not in completed_steps]
            for s in unresolved:
                step_id_key = s.id or s.step_id or "step"
                op = s.operation or s.operation_name or "unknown"
                blocked_res = {
                    "status": "blocked",
                    "source": "mock",
                    "operation": op,
                    "error": f"Step stalled due to unsatisfied upstream dependencies: {s.depends_on}",
                    "data": {},
                }
                step_outputs[step_id_key] = blocked_res
                completed_steps.add(s.id)
                tool_timings_ms[step_id_key] = 0.0
                errors.append(f"Execution error in {step_id_key}: blocked by upstream dependencies.")
            break

        # Execute all currently ready steps concurrently
        async def run_step(st: PlanStep):
            st_t0 = time.perf_counter()
            res = await execute_single_step(st, step_outputs, registry)
            st_duration = round((time.perf_counter() - st_t0) * 1000, 2)
            return st, res, st_duration

        batch_results = await asyncio.gather(*(run_step(s) for s in ready_steps))

        for step, res, st_duration in batch_results:
            step_id_key = step.id or step.step_id or "step"
            op = step.operation or step.operation_name or "unknown"
            tool_timings_ms[step_id_key] = st_duration

            # Cache under canonical id and aliases
            step_outputs[step_id_key] = res
            if step.id:
                step_outputs[step.id] = res
            if step.step_id:
                step_outputs[step.step_id] = res

            completed_steps.add(step.id)

            if res.get("status") == "failed":
                errors.append(f"Execution error in {step_id_key} ({op}): {res.get('error', 'unknown error')}")

            # Structured result entry
            result_entry = {
                "step_id": step_id_key,
                "operation": op,
                "result": res,
                "status": res.get("status", "success"),
                "partial": res.get("partial", False),
                "duration_ms": st_duration,
            }

            # Map to tool_results / analytics_results for downstream evidence assembly
            is_data_step = (
                step.target == ToolExecutionTarget.P4_EXTERNAL_TOOL
                or step.type == StepType.DATA.value
            )
            if is_data_step:
                tool_results.append(result_entry)
            else:
                analytics_results.append(result_entry)

    # Extract decision output if available
    decision_obj: Optional[Dict[str, Any]] = state.get("decision")
    for entry in analytics_results:
        op = entry.get("operation")
        res = entry.get("result", {})
        data = res.get("data", {})
        if op in ("select_safe_fishing_zone", "select_best_zone"):
            decision_obj = data
            break
        elif op in ("rank_zones", "calculate_zone_ranking") and not decision_obj:
            decision_obj = data

    executor_total_ms = round((time.perf_counter() - t0) * 1000, 2)
    latency_telemetry = dict(state.get("latency_telemetry") or {})
    latency_telemetry["executor_ms"] = executor_total_ms
    latency_telemetry["tool_timings_ms"] = tool_timings_ms

    return_state: Dict[str, Any] = {
        "tool_results": tool_results,
        "analytics_results": analytics_results,
        "errors": errors,
        "latency_telemetry": latency_telemetry,
    }

    if decision_obj:
        return_state["decision"] = decision_obj
        if "selected_zone" in decision_obj:
            return_state["selected_zone"] = decision_obj.get("selected_zone")
        if "rejected_zones" in decision_obj:
            return_state["rejected_zones"] = decision_obj.get("rejected_zones")
        if "ranked_zones" in decision_obj:
            return_state["ranked_zones"] = decision_obj.get("ranked_zones")
        if "all_evaluations" in decision_obj:
            return_state["all_evaluations"] = decision_obj.get("all_evaluations")
        if "decision_policy" in decision_obj:
            return_state["decision_policy"] = decision_obj.get("decision_policy")

    return return_state
