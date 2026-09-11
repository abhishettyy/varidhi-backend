"""MarineState TypedDict definition for the Marine Intelligence Platform LangGraph workflow."""

import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class MarineState(TypedDict, total=False):
    """
    Lightweight state container passed across all nodes in the LangGraph orchestration flow.

    Fields:
        query: Raw input string from the user.
        user_type: Role/persona of the user (e.g. 'fisherman', 'researcher', 'general').
        location: Structured representation of location (e.g. {'name': 'Mangalore', 'latitude': 12.8681, 'longitude': 74.8427}).
        time_range: Extracted temporal scope (e.g. 'tomorrow morning', 'next 24 hours').
        intent: Detected marine intent (e.g. 'FISHING_RECOMMENDATION', 'WEATHER_SAFETY').
        plan: Ordered list of required data/calculation steps (e.g. ['PFZ', 'SST', 'weather', 'waves', 'tide', 'restrictions']).
        tool_results: Outputs collected from P4 external tools / MCP integrations.
        analytics_results: Outputs collected from P6 marine analytics & risk calculations.
        decision: Orchestration decision / validation outcome.
        evidence: Standardized evidence items synthesized from tool and analytics results.
        response: Final formatted response payload and markdown content.
        errors: List of error messages or fallback notices collected during execution.

        # Internal graph & schema preservation fields
        raw_query: Optional[str]
        session_id: Optional[str]
        execution_steps: Optional[List[Any]]
        execution_plan: Optional[Any]
        evidence_bundle: Optional[Any]
        final_response: Optional[Any]
        fallback_mode: Optional[bool]
        is_terminal: Optional[bool]
    """
    # Core state fields
    query: str
    user_type: str
    location: Optional[Dict[str, Any]]
    time_range: Optional[str]
    intent: Optional[str]
    plan: Optional[List[Any]]
    tool_results: List[Dict[str, Any]]
    analytics_results: List[Dict[str, Any]]
    decision: Optional[Dict[str, Any]]
    evidence: Optional[List[Dict[str, Any]]]
    response: Optional[Dict[str, Any]]
    errors: List[str]

    # LangGraph orchestration and model objects
    raw_query: Optional[str]
    session_id: Optional[str]
    execution_steps: Optional[List[Any]]
    execution_plan: Optional[Any]
    evidence_bundle: Optional[Any]
    final_response: Optional[Any]
    fallback_mode: Optional[bool]
    is_terminal: Optional[bool]


# Alias AgentState for backwards compatibility
AgentState = MarineState
