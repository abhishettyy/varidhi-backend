"""High-level workflow entrypoint and execution helpers for the Marine Agent."""

import asyncio
from typing import Optional

from backend.agents.graph.builder import build_marine_agent_graph
from backend.agents.schemas.response import AgentResponse, RoleType
from backend.agents.state.agent_state import AgentState

# Lazy-loaded compiled graph singleton
_COMPILED_GRAPH = None


def get_marine_agent_graph():
    """Retrieve compiled LangGraph singleton."""
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_marine_agent_graph()
    return _COMPILED_GRAPH


async def run_marine_agent_async(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> AgentResponse:
    """
    Execute the marine intelligence agent graph asynchronously for a given query.
    """
    graph = get_marine_agent_graph()

    initial_state: AgentState = {
        "raw_query": query,
        "user_role": role,
        "session_id": session_id,
        "errors": [],
        "fallback_mode": False,
        "is_terminal": False,
        "tool_results": [],
        "analytics_results": [],
    }

    final_state = await graph.ainvoke(initial_state)
    return final_state.get("final_response")


def run_marine_agent(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> AgentResponse:
    """
    Synchronous wrapper to execute the marine intelligence agent graph.
    """
    return asyncio.run(run_marine_agent_async(query, role=role, session_id=session_id))
