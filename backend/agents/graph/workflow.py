"""High-level workflow entrypoints and execution helpers for the Marine Agent."""

import asyncio
from typing import Any, Dict, Optional

from backend.agents.graph.builder import (
    build_marine_agent_graph,
    build_minimal_marine_graph,
)
from backend.agents.schemas.response import AgentResponse, RoleType
from backend.agents.state.marine_state import MarineState

# Lazy-loaded singletons
_COMPILED_FULL_GRAPH = None
_COMPILED_MINIMAL_GRAPH = None


def get_marine_agent_graph():
    """Retrieve full compiled LangGraph singleton."""
    global _COMPILED_FULL_GRAPH
    if _COMPILED_FULL_GRAPH is None:
        _COMPILED_FULL_GRAPH = build_marine_agent_graph()
    return _COMPILED_FULL_GRAPH


def get_minimal_marine_graph():
    """Retrieve minimal compiled LangGraph singleton (understand_query -> planner -> END)."""
    global _COMPILED_MINIMAL_GRAPH
    if _COMPILED_MINIMAL_GRAPH is None:
        _COMPILED_MINIMAL_GRAPH = build_minimal_marine_graph()
    return _COMPILED_MINIMAL_GRAPH


async def run_minimal_marine_graph_async(
    query: str,
    user_type: str = "fisherman"
) -> MarineState:
    """
    Execute minimal workflow (understand_query -> planner) asynchronously.
    Returns the resulting MarineState containing intent, structured location, time_range, and plan.
    """
    graph = get_minimal_marine_graph()

    initial_state: MarineState = {
        "query": query,
        "user_type": user_type,
        "tool_results": [],
        "analytics_results": [],
        "errors": [],
    }

    final_state = await graph.ainvoke(initial_state)
    return final_state


def run_minimal_marine_graph(
    query: str,
    user_type: str = "fisherman"
) -> MarineState:
    """
    Synchronous wrapper for minimal workflow execution.
    """
    return asyncio.run(run_minimal_marine_graph_async(query, user_type=user_type))


async def run_marine_agent_state_async(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> MarineState:
    """
    Execute full marine intelligence agent graph asynchronously and return the complete resulting MarineState.
    """
    graph = get_marine_agent_graph()

    user_type = role.value if hasattr(role, "value") else str(role)
    initial_state: MarineState = {
        "query": query,
        "user_type": user_type,
        "errors": [],
        "tool_results": [],
        "analytics_results": [],
    }

    final_state = await graph.ainvoke(initial_state)
    return final_state


def run_marine_agent_state(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> MarineState:
    """
    Synchronous wrapper to execute full marine intelligence agent graph and return complete MarineState.
    """
    return asyncio.run(run_marine_agent_state_async(query, role=role, session_id=session_id))


async def run_marine_agent_async(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> Optional[AgentResponse]:
    """
    Execute full marine intelligence agent graph asynchronously for a given query.
    """
    final_state = await run_marine_agent_state_async(query, role=role, session_id=session_id)
    resp = final_state.get("final_response")
    if resp is None and final_state.get("response"):
        resp_data = final_state.get("response")
        if isinstance(resp_data, dict):
            resp = AgentResponse(**resp_data)
        elif isinstance(resp_data, AgentResponse):
            resp = resp_data
    return resp


def run_marine_agent(
    query: str,
    role: RoleType = RoleType.GENERAL,
    session_id: Optional[str] = None
) -> Optional[AgentResponse]:
    """
    Synchronous wrapper for full marine agent workflow.
    """
    return asyncio.run(run_marine_agent_async(query, role=role, session_id=session_id))

