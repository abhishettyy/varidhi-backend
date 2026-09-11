"""Error handling and fallback node: ensures graceful degradation and safety warnings on failure."""

import uuid
from typing import Any, Dict

from backend.agents.schemas.response import (
    AgentResponse,
    RoleType,
    SafetyAlert,
    SafetySeverity,
)
from backend.agents.state.agent_state import AgentState


async def error_handling_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Generates safety-first fallback responses when data sources fail or queries are ambiguous.
    """
    errors = state.get("errors", [])
    user_role = state.get("user_role", RoleType.GENERAL)
    raw_query = state.get("raw_query", "Unknown query")

    err_summary = "; ".join(errors) if errors else "Required marine observation stream temporarily unreachable."

    safety_alert = SafetyAlert(
        severity=SafetySeverity.CAUTION_YELLOW,
        title="ADVISORY: Marine Data Stream Partially Unavailable",
        description=f"Could not retrieve complete live sensor telemetry for query: '{raw_query}'.",
        action_advice="Please verify with local port authorities or the nearest coast guard station before venturing into open waters.",
    )

    markdown = (
        f"### ⚠️ Marine Advisory (Fallback Mode)\n\n"
        f"**Safety Caution:** {safety_alert.title}\n\n"
        f"{safety_alert.description}\n\n"
        f"> **Safety Directive:** {safety_alert.action_advice}\n\n"
        f"**Technical Details:** `{err_summary}`\n"
    )

    response = AgentResponse(
        response_id=f"fallback_{uuid.uuid4().hex[:8]}",
        role=user_role,
        markdown_content=markdown,
        safety_alert=safety_alert,
        key_recommendations=[safety_alert.action_advice],
        evidence_summary=["Fallback response generated due to upstream pipeline exception."],
        status="partial_fallback",
    )

    return {
        "final_response": response,
        "is_terminal": True,
        "fallback_mode": True,
    }
