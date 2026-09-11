"""MarineState TypedDict definition for the Marine Intelligence Platform LangGraph workflow."""

import sys
from typing import Any, Dict, List, Optional, Union

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
        intent: Detected marine intent (e.g. 'FISHING_RECOMMENDATION', 'WEATHER_QUERY', 'MARINE_SAFETY').
        confidence: Classification confidence score (0.0 to 1.0).
        location: Structured representation of location (e.g. {'name': 'Mangalore', 'latitude': 12.8681, 'longitude': 74.8427}).
                  Latitude and longitude are None if unresolvable.
        time_range: Structured temporal scope (e.g. {'raw': 'tomorrow morning', 'relative_day': 'tomorrow', 'period': 'morning'}).
        variables: Extracted marine environmental variables (e.g. ['SST', 'WAVE', 'WIND', 'PFZ']).
        vessel: Extracted vessel attributes/filters (e.g. {'type': 'trawler', 'id': 'IND-1234'}).
        route: Extracted route context (e.g. {'origin': 'Kochi', 'destination': 'Mangalore', 'waypoints': []}).
        constraints: Operational constraints (e.g. {'max_wave_height_m': 2.0, 'max_wind_speed_knots': 15.0}).
        query_intent: Full normalized QueryIntent dictionary.
        structured_query: Alias for query_intent.
        plan: Ordered list of required data/calculation steps.
        tool_results: Outputs collected from P4 external tools / MCP integrations.
        analytics_results: Outputs collected from P6 marine analytics & risk calculations.
        decision: Orchestration decision / validation outcome.
        evidence: Standardized evidence items synthesized from tool and analytics results.
        response: Final formatted response payload and markdown content.
        errors: List of error messages or fallback notices collected during execution.

        # Internal graph & schema preservation fields
        raw_query: Optional[str]
        session_id: Optional[str]
        intent_result: Optional[Any]
        spatiotemporal_context: Optional[Any]
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
    intent: Optional[str]
    confidence: Optional[float]
    location: Optional[Dict[str, Any]]
    time_range: Optional[Union[str, Dict[str, Any]]]
    variables: Optional[List[str]]
    vessel: Optional[Dict[str, Any]]
    route: Optional[Dict[str, Any]]
    constraints: Optional[Dict[str, Any]]
    query_intent: Optional[Dict[str, Any]]
    structured_query: Optional[Dict[str, Any]]
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
    intent_result: Optional[Any]
    spatiotemporal_context: Optional[Any]
    execution_steps: Optional[List[Any]]
    execution_plan: Optional[Any]
    evidence_bundle: Optional[Any]
    final_response: Optional[Any]
    fallback_mode: Optional[bool]
    is_terminal: Optional[bool]


# Alias AgentState for backwards compatibility
AgentState = MarineState
