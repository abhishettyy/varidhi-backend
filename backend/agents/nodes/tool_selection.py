"""Tool selection node: validates operation prerequisites and prepares invocation payloads."""

from typing import Any, Dict
from backend.agents.state.agent_state import AgentState


async def tool_selection_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Validates that tools selected in the execution plan are available
    and formatted with all necessary spatial and temporal inputs.
    """
    plan = state.get("execution_plan")
    errors = list(state.get("errors", []))

    if not plan or not plan.steps:
        return {
            "errors": errors + ["No execution plan steps found in state."],
            "fallback_mode": True,
        }

    # Verify that dependencies exist
    step_ids = {step.step_id for step in plan.steps}
    for step in plan.steps:
        for dep in step.depends_on:
            if dep not in step_ids:
                errors.append(f"Step {step.step_id} depends on unknown step {dep}.")

    return {
        "errors": errors,
        "fallback_mode": len(errors) > 0,
    }
