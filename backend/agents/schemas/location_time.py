"""Spatio-temporal extraction schemas for marine queries."""

from datetime import datetime
from typing import Optional
from backend.agents.schemas.base import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic point coordinate."""
    latitude: float = Field(0.0, description="Latitude in decimal degrees.")
    longitude: float = Field(0.0, description="Longitude in decimal degrees.")


class BoundingBox(BaseModel):
    """Geographic bounding box for regional marine queries."""
    min_latitude: float = Field(0.0)
    max_latitude: float = Field(0.0)
    min_longitude: float = Field(0.0)
    max_longitude: float = Field(0.0)


class SpatialContext(BaseModel):
    """Extracted spatial context from marine inquiry."""
    place_name: Optional[str] = Field(None, description="Extracted place name, harbor, or coastal region.")
    harbor_or_port: Optional[str] = Field(None, description="Specific harbor or landing center if identified.")
    coordinates: Optional[Coordinates] = Field(None, description="Explicit or resolved center coordinates.")
    bounding_box: Optional[BoundingBox] = Field(None, description="Extracted or resolved bounding box.")
    radius_nautical_miles: Optional[float] = Field(None, description="Radial distance in nautical miles.")
    coastal_state_or_country: Optional[str] = Field(None, description="State, province, or country.")


class TemporalContext(BaseModel):
    """Extracted temporal parameters for forecast or historical lookups."""
    time_descriptor: Optional[str] = Field(
        None,
        description="Raw temporal phrase e.g. 'tomorrow 4 AM', 'this weekend', 'next 48 hours'."
    )
    start_time: Optional[datetime] = Field(None, description="Parsed start timestamp if resolvable.")
    end_time: Optional[datetime] = Field(None, description="Parsed end timestamp if resolvable.")
    forecast_horizon_hours: Optional[int] = Field(
        default=24,
        description="Forecast horizon in hours (default 24h)."
    )
    is_historical: bool = Field(
        default=False,
        description="Whether query is asking for historical marine observations."
    )


class SpatioTemporalContext(BaseModel):
    """Combined spatial and temporal extraction result."""
    spatial: SpatialContext = Field(default_factory=SpatialContext)
    temporal: TemporalContext = Field(default_factory=TemporalContext)
    requires_spatial_clarification: bool = Field(
        default=False,
        description="True if location is mandatory for intent but missing from query."
    )
    requires_temporal_clarification: bool = Field(
        default=False,
        description="True if timeframe is ambiguous or missing."
    )
