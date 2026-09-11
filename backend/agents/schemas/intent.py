"""Intent definitions and classification models for marine domain queries."""

from enum import Enum
from typing import List, Optional
from backend.agents.schemas.base import BaseModel, Field


class MarineIntent(str, Enum):
    """Supported marine intelligence intents."""
    POTENTIAL_FISHING_ZONE = "potential_fishing_zone"
    OCEAN_WEATHER_SAFETY = "ocean_weather_safety"
    HAZARD_ALERT = "hazard_alert"
    WATER_QUALITY_ALGAL_BLOOM = "water_quality_algal_bloom"
    NAVIGATION_ADVISORY = "navigation_advisory"
    GENERAL_MARINE_QUERY = "general_marine_query"
    OUT_OF_SCOPE = "out_of_scope"


class IntentClassificationResult(BaseModel):
    """Structured output of intent detection."""
    primary_intent: MarineIntent = Field(
        ...,
        description="The primary identified marine intent."
    )
    secondary_intents: List[MarineIntent] = Field(
        default_factory=list,
        description="Secondary or supplementary intents detected in the query."
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the primary classification (0.0 - 1.0)."
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Brief justification for the chosen intent."
    )
    is_urgent_safety_risk: bool = Field(
        default=False,
        description="Flag indicating if the query signals an immediate emergency or hazardous condition."
    )
