"""Evidence schemas for structuring and validating multi-source marine observations."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


class EvidenceType(str, Enum):
    """Types of evidence collected across P4 tools and P6 analytics."""
    WEATHER_OBSERVATION = "weather_observation"
    OCEAN_TEMPERATURE_SST = "ocean_temperature_sst"
    CHLOROPHYLL_DENSITY = "chlorophyll_density"
    WAVE_AND_SWELL = "wave_and_swell"
    CURRENT_AND_TIDE = "current_and_tide"
    RISK_INDEX_CALCULATION = "risk_index_calculation"
    PFZ_ZONE_ANALYTICS = "pfz_zone_analytics"
    HAZARD_BULLETIN = "hazard_bulletin"
    BATHYMETRY_DEPTH = "bathymetry_depth"
    GENERAL_OBSERVATION = "general_observation"


class EvidenceItem(BaseModel):
    """A standardized unit of evidence collected during tool execution."""
    evidence_id: str = Field(..., description="Unique evidence identifier.")
    evidence_type: EvidenceType = Field(..., description="Category of marine evidence.")
    source: str = Field(..., description="Provider/Source name (e.g., 'P4:INCOIS_API', 'P6:RiskEngine').")
    summary: str = Field(..., description="Human-readable summary of the finding.")
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured key-value metrics (e.g. wave_height_m, sst_celsius, risk_score)."
    )
    confidence: float = Field(
        default=1.0,
        description="Reliability / confidence score."
    )
    spatial_tag: Optional[str] = Field(None, description="Spatial identifier or coordinates associated with evidence.")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Time evidence was acquired.")
    raw_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw output payload from the tool or analytic model."
    )


class EvidenceBundle(BaseModel):
    """Collection of assembled evidence passed into response synthesis."""
    bundle_id: str = Field(..., description="Unique bundle identifier.")
    query: str = Field(..., description="Original user query.")
    items: List[EvidenceItem] = Field(
        default_factory=list,
        description="List of standardized evidence items."
    )
    data_quality_score: float = Field(
        default=1.0,
        description="Aggregate data quality / completeness index."
    )
    missing_indicators: List[str] = Field(
        default_factory=list,
        description="List of requested data points that could not be retrieved."
    )
    assembled_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of evidence assembly."
    )
