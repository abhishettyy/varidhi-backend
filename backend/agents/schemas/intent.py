"""Intent definitions and classification models for marine domain queries."""

from enum import Enum
from typing import List, Optional
from backend.agents.schemas.base import BaseModel, Field


class MarineIntent(str, Enum):
    """Supported marine intelligence intents."""
    # Standard uppercase values
    FISHING_RECOMMENDATION = "FISHING_RECOMMENDATION"
    WEATHER_SAFETY = "WEATHER_SAFETY"
    HAZARD_ALERT = "HAZARD_ALERT"
    WATER_QUALITY = "WATER_QUALITY"
    NAVIGATION_ADVISORY = "NAVIGATION_ADVISORY"
    GENERAL_QUERY = "GENERAL_QUERY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

    # Aliases for compatibility
    POTENTIAL_FISHING_ZONE = "FISHING_RECOMMENDATION"
    OCEAN_WEATHER_SAFETY = "WEATHER_SAFETY"
    WATER_QUALITY_ALGAL_BLOOM = "WATER_QUALITY"
    GENERAL_MARINE_QUERY = "GENERAL_QUERY"


class IntentClassificationResult(BaseModel):
    """Structured output of intent detection."""
    primary_intent: str = Field(
        MarineIntent.FISHING_RECOMMENDATION.value,
        description="The primary identified marine intent."
    )
    secondary_intents: List[str] = Field(
        default_factory=list,
        description="Secondary or supplementary intents detected in the query."
    )
    confidence: float = Field(
        default=1.0,
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
