"""API Request and Response schemas for Varidhi HTTP service (Phase 8).

Defines stable, strongly-typed contracts for frontend consumption (P1 Fisherman UI / P2 Researcher GIS UI).
Structured data fields (decision, zones, evidence, visual_payload) are authoritative and derived directly from state.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

from backend.agents.schemas.base import BaseModel, Field
from backend.agents.schemas.response import RoleType, SafetyAlert, SafetySeverity


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_SYNTHETIC_DISCLAIMER: str = (
    "This assessment uses synthetic marine demonstration data for the current prototype. "
    "It is a deterministic demonstration heuristic and does not constitute official maritime "
    "safety certification, port clearance, or statutory navigation advice."
)


# =============================================================================
# 1. REQUEST SCHEMAS
# =============================================================================

class ChatRequest(BaseModel):
    """Incoming natural language marine query request."""
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language query from user (e.g., 'Where should I fish tomorrow morning near Mangalore?').",
        examples=["I'm near Mangalore. Where should I fish tomorrow morning?"]
    )
    role: RoleType = Field(
        default=RoleType.GENERAL,
        description="User persona/role ('fisherman', 'researcher', 'maritime_operator', 'general')."
    )
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional client-provided geospatial reference (e.g. {'name': 'Mangalore', 'latitude': 12.8681, 'longitude': 74.8427})."
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional client session identifier for request correlation."
    )
    context_zone_id: Optional[str] = Field(
        default=None,
        description="Optional focused zone identifier from frontend map selection."
    )


# =============================================================================
# 2. STRUCTURED RESPONSE SUB-SCHEMAS
# =============================================================================

class DecisionSummary(BaseModel):
    """Authoritative P6 decision synthesis result for the recommended zone."""
    selected_zone_id: Optional[str] = Field(
        default=None,
        description="Identifier of the recommended optimal safe fishing zone (e.g. 'ZONE_B')."
    )
    status: str = Field(
        default="NO_RECOMMENDATION",
        description="Decision status: 'SELECTED', 'NO_SAFE_ZONE', 'PROHIBITED'."
    )
    opportunity_score: Optional[float] = Field(
        default=None,
        description="Deterministic biological opportunity score (0.0 to 100.0)."
    )
    risk_score: Optional[float] = Field(
        default=None,
        description="Deterministic marine condition risk score (0.0 to 100.0; lower is safer)."
    )
    regulatory_status: Optional[str] = Field(
        default=None,
        description="Regulatory compliance status: 'ELIGIBLE', 'BLOCKED', 'CONDITIONAL'."
    )
    ranking_score: Optional[float] = Field(
        default=None,
        description="Overall multi-criteria ranking score (0.0 to 100.0)."
    )
    distance_nm: Optional[float] = Field(
        default=None,
        description="Operational distance in nautical miles from base harbor / user location."
    )
    bearing: Optional[str] = Field(
        default=None,
        description="Compass bearing from port (e.g. 'SSW', '245°')."
    )
    species: List[str] = Field(
        default_factory=list,
        description="Target fish species associated with the biological convergence."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Zone centroid latitude (None if not provided in scenario fixture)."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Zone centroid longitude (None if not provided in scenario fixture)."
    )
    reasons: List[str] = Field(
        default_factory=list,
        description="Machine-readable decision factors and selection rationale."
    )
    safety_level: Optional[str] = Field(
        default=None,
        description="Safety alert level (e.g. 'safe_green', 'caution_yellow', 'warning_orange', 'danger_red')."
    )
    action_advice: Optional[str] = Field(
        default=None,
        description="Operational directive (e.g. 'Safe for mechanized boats; maintain standard vigilance.')."
    )


class ZoneSummary(BaseModel):
    """Detailed evaluation record for an individual candidate fishing zone."""
    zone_id: str = Field(..., description="Unique zone identifier (e.g. 'ZONE_A', 'ZONE_B', 'ZONE_C').")
    status: str = Field(..., description="Zone evaluation status: 'SELECTED', 'ELIGIBLE', 'REJECTED_RISK', 'REJECTED_LEGAL'.")
    opportunity_score: Optional[float] = Field(default=None, description="P6 Opportunity Engine score (0-100).")
    risk_score: Optional[float] = Field(default=None, description="P6 Marine Risk Engine score (0-100).")
    regulatory_status: Optional[str] = Field(default=None, description="P6 Regulatory Engine clearance: 'ELIGIBLE', 'BLOCKED'.")
    ranking_score: Optional[float] = Field(default=None, description="Final decision synthesis ranking score.")
    distance_nm: Optional[float] = Field(default=None, description="Distance from harbor in nautical miles.")
    bearing: Optional[str] = Field(default=None, description="Compass bearing from harbor.")
    species: List[str] = Field(default_factory=list, description="Target species.")
    latitude: Optional[float] = Field(default=None, description="Latitude centroid if available.")
    longitude: Optional[float] = Field(default=None, description="Longitude centroid if available.")
    reasons: List[str] = Field(default_factory=list, description="Selection or disqualification reasons.")


class EvidenceItemResponse(BaseModel):
    """Standardized unit of provenance-preserving evidence collected from tools & analytics."""
    evidence_id: str = Field(..., description="Unique evidence item identifier.")
    evidence_type: str = Field(..., description="Evidence category (e.g. 'weather_observation', 'pfz_zone_analytics').")
    source: str = Field(..., description="Data provider / tool source (e.g. 'P4_TOOL_INTEGRATION', 'P6_MARINE_ANALYTICS').")
    summary: str = Field(..., description="Human-readable summary of observation.")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Numerical metric values.")
    confidence: float = Field(default=1.0, description="Data confidence score.")
    spatial_tag: Optional[str] = Field(default=None, description="Geographic or zone association.")
    timestamp: Optional[str] = Field(default=None, description="ISO-8601 acquisition timestamp.")
    raw_payload: Optional[Dict[str, Any]] = Field(default=None, description="Raw underlying tool payload.")


class VisualPayloadResponse(BaseModel):
    """Structured geospatial and visual data ready for MapLibre / chart rendering."""
    map_features_geojson: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON FeatureCollection with evaluated zones, coordinates, and properties."
    )
    charts_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Forecast timeseries (wave height, wind speed vs time)."
    )
    metric_badges: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key-value summary badges (e.g. {'SST': '28.4°C', 'Wave Height': '1.5m', 'Safety': 'caution_yellow'})."
    )
    focus_zone_id: Optional[str] = Field(
        default=None,
        description="Primary zone ID for map auto-centering."
    )
    highlight_layer: Optional[str] = Field(
        default=None,
        description="Suggested active map layer ('zones', 'weather', 'restrictions', 'pfz')."
    )


class QueryContextResponse(BaseModel):
    """Structured understanding of the user query extracted during execution."""
    intent: Optional[str] = Field(default=None, description="Normalized marine intent.")
    confidence: float = Field(default=1.0, description="Intent classification confidence.")
    location: Optional[Dict[str, Any]] = Field(default=None, description="Extracted geographic location entity.")
    time_range: Optional[Dict[str, Any]] = Field(default=None, description="Extracted temporal scope.")
    variables: List[str] = Field(default_factory=list, description="Target oceanographic variables requested.")
    vessel: Optional[Dict[str, Any]] = Field(default=None, description="Vessel parameters if specified.")
    route: Optional[Dict[str, Any]] = Field(default=None, description="Origin/destination route if specified.")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Extracted physical/operational constraints.")


class TelemetryResponse(BaseModel):
    """Pipeline performance and execution telemetry."""
    total_pipeline_ms: float = Field(default=0.0, description="Total wall-clock pipeline duration in milliseconds.")
    understand_query_ms: Optional[float] = Field(default=None, description="Duration of query understanding node.")
    planner_ms: Optional[float] = Field(default=None, description="Duration of planner node.")
    tool_selection_ms: Optional[float] = Field(default=None, description="Duration of tool selection node.")
    executor_ms: Optional[float] = Field(default=None, description="Duration of parallel DAG tool executor node.")
    evidence_assembly_ms: Optional[float] = Field(default=None, description="Duration of evidence assembly node.")
    response_generation_ms: Optional[float] = Field(default=None, description="Duration of response generation node.")
    tool_timings_ms: Dict[str, float] = Field(default_factory=dict, description="Granular per-tool execution times.")
    llm_used: bool = Field(default=False, description="Whether LLM structured generation succeeded.")
    llm_fallback: bool = Field(default=False, description="Whether deterministic fallback was triggered.")
    llm_fallback_reason: Optional[str] = Field(default=None, description="Categorical fallback code (e.g. 'NETWORK_UNREACHABLE').")
    llm_provider: Optional[str] = Field(default=None, description="Active LLM provider ('gemini', 'openai', 'mock').")
    llm_model: Optional[str] = Field(default=None, description="Active LLM model name.")


# =============================================================================
# 3. ROOT API RESPONSE SCHEMA
# =============================================================================

class ChatResponse(BaseModel):
    """
    Standardized HTTP API response for all marine queries.
    Combines persona-tailored presentation prose with authoritative structured analytics.
    """
    message: str = Field(
        ...,
        description="Synthesized markdown advisory tailored to the requested persona."
    )
    decision: Optional[DecisionSummary] = Field(
        default=None,
        description="Authoritative decision synthesis outcome."
    )
    zones: List[ZoneSummary] = Field(
        default_factory=list,
        description="Complete list of candidate zones evaluated with scores and rejection reasons."
    )
    evidence: List[EvidenceItemResponse] = Field(
        default_factory=list,
        description="Provenance-preserving structured evidence items."
    )
    visual_payload: Optional[VisualPayloadResponse] = Field(
        default=None,
        description="GeoJSON features, chart timeseries, and metric badges for frontend UI."
    )
    query_context: QueryContextResponse = Field(
        ...,
        description="Structured extraction of intent, location, time range, and constraints."
    )
    telemetry: TelemetryResponse = Field(
        ...,
        description="Execution timing and LLM status telemetry."
    )
    disclaimer: str = Field(
        default=DEFAULT_SYNTHETIC_DISCLAIMER,
        description="Notice regarding prototype synthetic demonstration data."
    )

    # -------------------------------------------------------------------------
    # Backwards-compatibility fields for existing frontend chat components
    # -------------------------------------------------------------------------
    response_id: str = Field(..., description="Unique response identifier.")
    role: RoleType = Field(default=RoleType.GENERAL, description="Persona style used.")
    markdown_content: str = Field(..., description="Mirror of message for legacy chat cards.")
    safety_alert: Optional[SafetyAlert] = Field(default=None, description="Safety alert header object.")
    key_recommendations: List[str] = Field(default_factory=list, description="Key bullet recommendations.")
    evidence_summary: List[str] = Field(default_factory=list, description="Text summaries of evidence.")
    status: str = Field(default="success", description="'success', 'partial_fallback', or 'error'.")
    execution_time_seconds: Optional[float] = Field(default=None, description="Total execution time in seconds.")


class HealthResponse(BaseModel):
    """Health check endpoint response."""
    status: str = Field(default="ok", description="Service health status.")
    service: str = Field(default="Varidhi Marine Intelligence Platform", description="Service name.")
    version: str = Field(default="1.0.0", description="API version.")
    llm_provider: Optional[str] = Field(default=None, description="Active LLM provider name.")
    llm_model: Optional[str] = Field(default=None, description="Active LLM model name.")
