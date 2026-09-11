"""LangGraph Agent State definition for the Marine Intelligence Platform."""

import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from backend.agents.schemas.intent import IntentClassificationResult
from backend.agents.schemas.location_time import SpatioTemporalContext
from backend.agents.schemas.plan import ExecutionPlan
from backend.agents.schemas.evidence import EvidenceBundle
from backend.agents.schemas.response import AgentResponse, RoleType


class AgentState(TypedDict, total=False):
    """
    Central state container passed across all nodes in the LangGraph orchestration flow.
    Designed to be lightweight, fully typed, and cleanly serializable.
    """
    # 1. Inputs
    raw_query: str
    user_role: RoleType
    session_id: Optional[str]

    # 2. Query Understanding & Entity Extraction
    intent_result: Optional[IntentClassificationResult]
    spatiotemporal_context: Optional[SpatioTemporalContext]

    # 3. Planning & Routing
    execution_plan: Optional[ExecutionPlan]
    current_step_index: int

    # 4. Raw Tool & Analytics Dispatch (Interfaces with P4 & P6)
    tool_results: List[Dict[str, Any]]
    analytics_results: List[Dict[str, Any]]

    # 5. Evidence Aggregation
    evidence_bundle: Optional[EvidenceBundle]

    # 6. Response Synthesis & Delivery
    final_response: Optional[AgentResponse]

    # 7. Flow Control & Error Tracking
    errors: List[str]
    is_terminal: bool
    fallback_mode: bool
