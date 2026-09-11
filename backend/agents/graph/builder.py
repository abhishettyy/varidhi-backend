"""LangGraph StateGraph builder for Marine Intelligence Agent Orchestration."""

from typing import Any, Dict

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    END = "__END__"

from backend.agents.state.marine_state import MarineState
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.nodes.planner import planner_node
from backend.agents.nodes.tool_selection import tool_selection_node
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.evidence_assembly import evidence_assembly_node
from backend.agents.nodes.response_generation import response_generation_node
from backend.agents.nodes.error_handling import error_handling_node


def route_after_tool_selection(state: MarineState) -> str:
    """Conditional router: sends flow to error_handling if validation fails."""
    if state.get("errors") and len(state.get("errors", [])) > 0:
        return "error_handling"
    return "executor"


class LightweightFallbackGraph:
    """
    Lightweight fallback runner mirroring LangGraph's compiled graph interface (ainvoke / invoke).
    Executes understand_query -> planner -> (optional downstream nodes) in state graph order.
    """

    def __init__(self, minimal_only: bool = False):
        self.minimal_only = minimal_only

    async def ainvoke(self, initial_state: MarineState) -> MarineState:
        state = dict(initial_state)

        # 1. Understand Query
        qu_res = await understand_query_node(state)
        state.update(qu_res)

        # 2. Planner
        plan_res = await planner_node(state)
        state.update(plan_res)

        if self.minimal_only:
            return state

        # Downstream execution (if full pipeline is requested)
        ts_res = await tool_selection_node(state)
        state.update(ts_res)

        next_step = route_after_tool_selection(state)
        if next_step == "error_handling":
            err_res = await error_handling_node(state)
            state.update(err_res)
            return state

        exec_res = await executor_node(state)
        state.update(exec_res)

        ea_res = await evidence_assembly_node(state)
        state.update(ea_res)

        rg_res = await response_generation_node(state)
        state.update(rg_res)

        return state

    def invoke(self, initial_state: MarineState) -> MarineState:
        import asyncio
        return asyncio.run(self.ainvoke(initial_state))


def build_minimal_marine_graph():
    """
    Constructs and compiles the minimal LangGraph workflow:
    understand_query -> planner -> END
    """
    if not LANGGRAPH_AVAILABLE:
        return LightweightFallbackGraph(minimal_only=True)

    workflow = StateGraph(MarineState)
    workflow.add_node("understand_query", understand_query_node)
    workflow.add_node("planner", planner_node)

    workflow.set_entry_point("understand_query")
    workflow.add_edge("understand_query", "planner")
    workflow.add_edge("planner", END)

    return workflow.compile()


def build_marine_agent_graph():
    """
    Constructs and compiles the complete LangGraph StateGraph workflow for marine intelligence.
    """
    if not LANGGRAPH_AVAILABLE:
        return LightweightFallbackGraph(minimal_only=False)

    workflow = StateGraph(MarineState)

    # 1. Register all nodes
    workflow.add_node("understand_query", understand_query_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("tool_selection", tool_selection_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("evidence_assembly", evidence_assembly_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("error_handling", error_handling_node)

    # 2. Define edge transitions
    workflow.set_entry_point("understand_query")
    workflow.add_edge("understand_query", "planner")
    workflow.add_edge("planner", "tool_selection")

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

    return workflow.compile()
