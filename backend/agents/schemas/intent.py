"""Intent definitions, entity models, and structured QueryIntent schemas for marine queries."""

from enum import Enum
from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


class MarineIntent(str, Enum):
    """Supported marine intelligence intents (Phase 2 Standardized Categories)."""
    FISHING_RECOMMENDATION = "FISHING_RECOMMENDATION"
    PFZ_SEARCH = "PFZ_SEARCH"
    MARINE_SAFETY = "MARINE_SAFETY"
    WEATHER_QUERY = "WEATHER_QUERY"
    HAZARD_QUERY = "HAZARD_QUERY"
    GEOFENCE_QUERY = "GEOFENCE_QUERY"
    ROUTE_QUERY = "ROUTE_QUERY"
    VESSEL_QUERY = "VESSEL_QUERY"
    HISTORICAL_ANALYSIS = "HISTORICAL_ANALYSIS"
    GENERAL_MARINE_QUERY = "GENERAL_MARINE_QUERY"

    # Compatibility aliases for Phase 1 / external callers
    WEATHER_SAFETY = "WEATHER_QUERY"
    HAZARD_ALERT = "HAZARD_QUERY"
    WATER_QUALITY = "GENERAL_MARINE_QUERY"
    NAVIGATION_ADVISORY = "ROUTE_QUERY"
    GENERAL_QUERY = "GENERAL_MARINE_QUERY"
    POTENTIAL_FISHING_ZONE = "PFZ_SEARCH"
    OCEAN_WEATHER_SAFETY = "WEATHER_QUERY"
    WATER_QUALITY_ALGAL_BLOOM = "GENERAL_MARINE_QUERY"


class MarineVariable(str, Enum):
    """Recognized marine domain variables and observational layers."""
    SST = "SST"
    CHLOROPHYLL = "CHLOROPHYLL"
    PFZ = "PFZ"
    WIND = "WIND"
    WAVE = "WAVE"
    SWELL = "SWELL"
    TIDE = "TIDE"
    CURRENT = "CURRENT"
    VESSEL_ACTIVITY = "VESSEL_ACTIVITY"
    BATHYMETRY = "BATHYMETRY"
    SALINITY = "SALINITY"


class StructuredLocation(BaseModel):
    """Structured location entity. Latitude/Longitude remain None if unresolvable."""
    name: Optional[str] = Field(None, description="Location, harbor, or coastal place name.")
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees (None if unresolved).")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees (None if unresolved).")
    harbor: Optional[str] = Field(None, description="Identified fishing harbor or landing center.")
    region: Optional[str] = Field(None, description="Coastal state or oceanographic sector.")


class StructuredTimeRange(BaseModel):
    """Structured temporal range entity."""
    raw: str = Field("next 24 hours", description="Raw temporal phrase e.g. 'tomorrow morning'.")
    relative_day: Optional[str] = Field(None, description="Relative day e.g. 'today', 'tomorrow', 'this weekend'.")
    period: Optional[str] = Field(None, description="Period of day e.g. 'morning', 'afternoon', 'evening', 'night'.")
    start_time: Optional[str] = Field(None, description="Parsed ISO start timestamp if applicable.")
    end_time: Optional[str] = Field(None, description="Parsed ISO end timestamp if applicable.")
    is_historical: bool = Field(False, description="Whether query requests historical marine observations.")
    forecast_horizon_hours: Optional[int] = Field(24, description="Forecast horizon in hours.")


class StructuredVessel(BaseModel):
    """Extracted vessel context and vessel attributes."""
    type: Optional[str] = Field(None, description="Vessel type e.g. motorized boat, trawler, cargo, artisanal.")
    id: Optional[str] = Field(None, description="Vessel identifier, callsign, or MMSI.")
    name: Optional[str] = Field(None, description="Vessel name.")
    length_m: Optional[float] = Field(None, description="Vessel length in meters.")


class StructuredRoute(BaseModel):
    """Extracted route and transit navigation parameters."""
    origin: Optional[str] = Field(None, description="Origin port or starting coordinates.")
    destination: Optional[str] = Field(None, description="Destination port or target coordinates.")
    waypoints: List[str] = Field(default_factory=list, description="Waypoints or intermediate passages.")


class QueryIntent(BaseModel):
    """Normalized structured QueryIntent representation."""
    intent: str = Field(
        MarineIntent.GENERAL_MARINE_QUERY.value,
        description="The primary identified marine intent category."
    )
    confidence: float = Field(
        default=0.9,
        description="Confidence score of the primary intent classification (0.0 - 1.0)."
    )
    location: Optional[StructuredLocation] = Field(
        default=None,
        description="Structured spatial entity. Lat/lon are null if unresolvable."
    )
    time_range: Optional[StructuredTimeRange] = Field(
        default=None,
        description="Structured temporal scope."
    )
    variables: List[str] = Field(
        default_factory=list,
        description="Identified marine environmental and oceanographic variables."
    )
    vessel: Optional[StructuredVessel] = Field(
        default=None,
        description="Extracted vessel specifications or filters."
    )
    route: Optional[StructuredRoute] = Field(
        default=None,
        description="Extracted origin, destination, and passage route."
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Operational constraints (e.g. max_wave_height, max_wind_speed, depth)."
    )
    raw_query: Optional[str] = Field(
        default=None,
        description="Original query string submitted by the user."
    )


class IntentClassificationResult(BaseModel):
    """Legacy structured output of intent detection for backwards compatibility."""
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
