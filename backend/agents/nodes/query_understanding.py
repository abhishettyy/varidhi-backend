"""Query understanding node compatibility wrapper."""

from typing import Any, Dict
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.state.marine_state import MarineState


async def query_understanding_node(state: MarineState) -> Dict[str, Any]:
    """
    Standard query understanding node wrapper invoking understand_query_node.
    """
    return await understand_query_node(state)
