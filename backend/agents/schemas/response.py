"""Response schemas tailored for Marine Intelligence personas and frontend consumers."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoleType(str, Enum):
    """Target persona / user role receiving the agent response."""
    FISHERMAN = "fisherman"                  # Clear, actionable, simple, safety-first (P1 UI)
    RESEARCHER = "researcher"                # Detailed data tables, scientific metrics, methodology (P2 UI)
    MARITIME_OPERATOR = "maritime_operator"  # Navigation, logistics, hazard thresholds
    GENERAL = "general"                      # Balanced marine overview


class SafetySeverity(str, Enum):
    """Marine safety tier classification."""
    SAFE_GREEN = "safe_green"                # Ideal conditions, low risk
    CAUTION_YELLOW = "caution_yellow"        # Moderate swell/wind, vigilance advised
    WARNING_ORANGE = "warning_orange"        # High swell, strong currents, small craft advisory
    DANGER_RED = "danger_red"                # Cyclonic storm, rough sea, severe gale, do not venture


class SafetyAlert(BaseModel):
    """Safety alert banner and advisory."""
    severity: SafetySeverity = Field(
        default=SafetySeverity.SAFE_GREEN,
        description="Overall safety level for the queried sea area."
    )
    title: str = Field(..., description="Short advisory title.")
    description: str = Field(..., description="Explanation of sea conditions and hazards.")
    action_advice: str = Field(
        ...,
        description="Actionable directive (e.g., 'Safe for small crafts', 'Avoid venturing past 15 NM')."
    )
    issued_at: datetime = Field(default_factory=_utc_now)


class VisualPayload(BaseModel):
    """Structured data artifacts for P1 (Fisherman UI) and P2 (Researcher/GIS UI)."""
    map_features_geojson: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON points/polygons for PFZ coordinates, risk zones, or hazard buffers."
    )
    charts_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Timeseries or comparative chart data (e.g. wave height vs time, SST gradient)."
    )
    metric_badges: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Quick-glance metric badges (e.g. {'SST': '28.5°C', 'Wave': '1.2m', 'Wind': '12 kts'})."
    )


class AgentResponse(BaseModel):
    """Complete structured output produced by the LangGraph response generation node."""
    response_id: str = Field(..., description="Unique response identifier.")
    role: RoleType = Field(default=RoleType.GENERAL, description="Persona tailored for.")
    markdown_content: str = Field(
        ...,
        description="User-facing synthesized natural language response."
    )
    safety_alert: Optional[SafetyAlert] = Field(
        default=None,
        description="Safety alert details if applicable."
    )
    key_recommendations: List[str] = Field(
        default_factory=list,
        description="Bullet-point actionable insights."
    )
    evidence_summary: List[str] = Field(
        default_factory=list,
        description="Transparent list of evidence points supporting the advisory."
    )
    visual_payload: Optional[VisualPayload] = Field(
        default=None,
        description="Structured data payloads for map & UI rendering."
    )
    status: str = Field(
        default="success",
        description="Status code: 'success', 'partial_fallback', 'error'."
    )
    execution_time_seconds: Optional[float] = Field(None, description="Time taken to process.")
