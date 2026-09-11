"""LangGraph StateGraph builder for Marine Intelligence Agent Orchestration."""

from typing import Any, Callable, Dict, Optional

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    END = "__END__"

from backend.agents.state.agent_state import AgentState
from backend.agents.nodes.query_understanding import query_understanding_node
from backend.agents.nodes.planning import planning_node
from backend.agents.nodes.tool_selection import tool_selection_node
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.evidence_assembly import evidence_assembly_node
from backend.agents.nodes.response_generation import response_generation_node
from backend.agents.nodes.error_handling import error_handling_node


def route_after_tool_selection(state: AgentState) -> str:
    """Conditional router: sends flow to error_handling if validation fails."""
    if state.get("fallback_mode", False):
        return "error_handling"
    return "executor"


class LightweightFallbackGraph:
    """
    Lightweight fallback runner mirroring LangGraph's compiled graph interface (ainvoke / invoke).
    Used when langgraph package is not yet installed in the local environment.
    """

    async def ainvoke(self, initial_state: AgentState) -> AgentState:
        state = dict(initial_state)

        # 1. Query Understanding
        qu_res = await query_understanding_node(state)
        state.update(qu_res)

        # 2. Planning
        plan_res = await planning_node(state)
        state.update(plan_res)

        # 3. Tool Selection
        ts_res = await tool_selection_node(state)
        state.update(ts_res)

        # 4. Conditional Edge
        next_step = route_after_tool_selection(state)
        if next_step == "error_handling":
            err_res = await error_handling_node(state)
            state.update(err_res)
            return state

        # 5. Executor
        exec_res = await executor_node(state)
        state.update(exec_res)

        # 6. Evidence Assembly
        ea_res = await evidence_assembly_node(state)
        state.update(ea_res)

        # 7. Response Generation
        rg_res = await response_generation_node(state)
        state.update(rg_res)

        return state

    def invoke(self, initial_state: AgentState) -> AgentState:
        import asyncio
        return asyncio.run(self.ainvoke(initial_state))


def build_marine_agent_graph():
    """
    Constructs and compiles the complete LangGraph StateGraph workflow for marine intelligence.
    Falls back gracefully to LightweightFallbackGraph if langgraph is not yet installed.
    """
    if not LANGGRAPH_AVAILABLE:
        return LightweightFallbackGraph()

    workflow = StateGraph(AgentState)

    # 1. Register all nodes
    workflow.add_node("query_understanding", query_understanding_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("tool_selection", tool_selection_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("evidence_assembly", evidence_assembly_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("error_handling", error_handling_node)

    # 2. Define edge transitions
    workflow.set_entry_point("query_understanding")
    workflow.add_edge("query_understanding", "planning")
    workflow.add_edge("planning", "tool_selection")

    # Conditional routing after tool selection
    workflow.add_conditional_edges(
        "tool_selection",
        route_after_tool_selection,
        {
            "executor": "executor",
            "error_handling": "error_handling",
        }
    )

    workflow.add_edge("executor", "evidence_assembly")
    workflow.add_edge("evidence_assembly", "response_generation")
    workflow.add_edge("response_generation", END)
    workflow.add_edge("error_handling", END)

    # Compile the graph
    app = workflow.compile()
    return app
