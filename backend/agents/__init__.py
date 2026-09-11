"""Agentic AI Marine Intelligence Platform - Agent Orchestration Module (P3).

This module contains the LangGraph orchestration engine, intent classification,
spatio-temporal extraction, planning, evidence assembly, and response generation.
"""

from .graph.builder import build_marine_agent_graph
from .graph.workflow import (
    get_marine_agent_graph,
    run_marine_agent,
    run_marine_agent_async,
)
from .state.agent_state import AgentState
from .schemas.intent import MarineIntent, IntentClassificationResult
from .schemas.location_time import Coordinates, BoundingBox, SpatialContext, TemporalContext, SpatioTemporalContext
from .schemas.plan import PlanStep, ExecutionPlan, ToolExecutionTarget
from .schemas.evidence import EvidenceItem, EvidenceBundle, EvidenceType
from .schemas.response import RoleType, SafetySeverity, SafetyAlert, VisualPayload, AgentResponse
from .interfaces.p4_tools import (
    P4ToolProvider,
    MockP4ToolProvider,
    get_p4_provider,
    set_p4_provider,
)
from .interfaces.p6_analytics import (
    P6AnalyticsProvider,
    MockP6AnalyticsProvider,
    get_p6_provider,
    set_p6_provider,
)

__all__ = [
    # Graph & Workflow
    "build_marine_agent_graph",
    "get_marine_agent_graph",
    "run_marine_agent",
    "run_marine_agent_async",
    # State
    "AgentState",
    # Schemas
    "MarineIntent",
    "IntentClassificationResult",
    "Coordinates",
    "BoundingBox",
    "SpatialContext",
    "TemporalContext",
    "SpatioTemporalContext",
    "PlanStep",
    "ExecutionPlan",
    "ToolExecutionTarget",
    "EvidenceItem",
    "EvidenceBundle",
    "EvidenceType",
    "RoleType",
    "SafetySeverity",
    "SafetyAlert",
    "VisualPayload",
    "AgentResponse",
    # Interfaces (P4 Tools & P6 Analytics)
    "P4ToolProvider",
    "MockP4ToolProvider",
    "get_p4_provider",
    "set_p4_provider",
    "P6AnalyticsProvider",
    "MockP6AnalyticsProvider",
    "get_p6_provider",
    "set_p6_provider",
]
