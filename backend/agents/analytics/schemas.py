"""Schemas for P6 Opportunity Scoring Engine.

Defines typed structures for opportunity weights, raw inputs, normalized components,
zone-level opportunity scores, and analysis results.
"""

from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


class OpportunityWeights(BaseModel):
    """
    Configurable weights for multicriteria opportunity heuristic scoring.
    Must sum to 1.0 under complete data conditions.
    """
    pfz: float = Field(
        default=0.40,
        description="Weight for Potential Fishing Zone advisory confidence (0.0 - 1.0)"
    )
    sst_front: float = Field(
        default=0.25,
        description="Weight for Sea Surface Temperature thermal front/gradient (0.0 - 1.0)"
    )
    chlorophyll: float = Field(
        default=0.25,
        description="Weight for Chlorophyll-a concentration biological productivity proxy (0.0 - 1.0)"
    )
    distance: float = Field(
        default=0.10,
        description="Weight for operational distance / proximity from port or vessel (0.0 - 1.0)"
    )

    def to_dict(self) -> Dict[str, float]:
        return {
            "pfz": self.pfz,
            "sst_front": self.sst_front,
            "chlorophyll": self.chlorophyll,
            "distance": self.distance,
        }


class RawOpportunityFeatures(BaseModel):
    """Extracted raw domain parameters for a single candidate zone."""
    zone_id: str = Field(..., description="Unique zone identifier (e.g. 'ZONE_A')")
    pfz_confidence: Optional[float] = Field(
        default=None, description="PFZ advisory confidence score (0.0 - 1.0)"
    )
    sst_celsius: Optional[float] = Field(
        default=None, description="Sea Surface Temperature in degrees Celsius"
    )
    sst_gradient_delta: Optional[float] = Field(
        default=None, description="Thermal gradient temperature delta across front in deg C"
    )
    sst_gradient_c_per_km: Optional[float] = Field(
        default=None, description="Spatial SST gradient in deg C per km"
    )
    chlorophyll_a_mg_m3: Optional[float] = Field(
        default=None, description="Chlorophyll-a ocean color concentration in mg/m^3"
    )
    chlorophyll_density: Optional[str] = Field(
        default=None, description="Qualitative chlorophyll density descriptor"
    )
    distance_nm: Optional[float] = Field(
        default=None, description="Distance from harbor / reference location in nautical miles"
    )
    depth_m: Optional[float] = Field(
        default=None, description="Bathymetric target depth in meters"
    )
    species: Optional[List[str]] = Field(
        default=None, description="Likely target pelagic/demersal species"
    )
    latitude: Optional[float] = Field(
        default=None, description="Centroid latitude in decimal degrees"
    )
    longitude: Optional[float] = Field(
        default=None, description="Centroid longitude in decimal degrees"
    )


class OpportunityComponents(BaseModel):
    """Normalized sub-scores for each feature (0.0 to 100.0)."""
    pfz: Optional[float] = Field(
        default=None, description="Normalized PFZ confidence sub-score (0.0 - 100.0)"
    )
    sst_front: Optional[float] = Field(
        default=None, description="Normalized thermal front gradient sub-score (0.0 - 100.0)"
    )
    chlorophyll: Optional[float] = Field(
        default=None, description="Normalized chlorophyll productivity sub-score (0.0 - 100.0)"
    )
    distance: Optional[float] = Field(
        default=None, description="Normalized proximity sub-score (0.0 - 100.0; closer is higher)"
    )

    def to_dict(self) -> Dict[str, Optional[float]]:
        return {
            "pfz": self.pfz,
            "sst_front": self.sst_front,
            "chlorophyll": self.chlorophyll,
            "distance": self.distance,
        }


class ZoneOpportunityScore(BaseModel):
    """
    Deterministic opportunity evaluation for an individual candidate zone.
    Contains overall score, component breakdown, active weights, missing features,
    and machine-readable explanation factors.
    """
    zone_id: str = Field(..., description="Unique zone identifier")
    opportunity_score: float = Field(
        ..., description="Overall aggregated opportunity score (0.0 - 100.0)"
    )
    convergence_grade: str = Field(
        default="Moderate",
        description="Opportunity classification tier: 'High', 'Moderate-High', 'Moderate', 'Low'"
    )
    components: OpportunityComponents = Field(
        default_factory=OpportunityComponents,
        description="Individual normalized feature sub-scores (0-100)"
    )
    raw_features: RawOpportunityFeatures = Field(
        ..., description="Raw inputs used for this calculation"
    )
    weights_used: Dict[str, float] = Field(
        default_factory=dict,
        description="Effective weights applied after missing-data dynamic renormalization"
    )
    missing_features: List[str] = Field(
        default_factory=list,
        description="List of feature keys that were unavailable or invalid"
    )
    explanation_factors: List[str] = Field(
        default_factory=list,
        description="Machine-readable factor strings for downstream evidence synthesis"
    )
    source: str = Field(
        default="derived",
        description="Provenance origin of score"
    )
    method: str = Field(
        default="heuristic_weighted_multicriteria",
        description="Algorithmic scoring method"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "opportunity_score": self.opportunity_score,
            "convergence_grade": self.convergence_grade,
            "components": self.components.to_dict(),
            "raw_features": self.raw_features.model_dump() if hasattr(self.raw_features, "model_dump") else self.raw_features.__dict__,
            "weights_used": self.weights_used,
            "missing_features": self.missing_features,
            "explanation_factors": self.explanation_factors,
            "source": self.source,
            "method": self.method,
        }


class OpportunityAnalysisResult(BaseModel):
    """Batch opportunity scoring result for multiple candidate zones."""
    status: str = Field(default="success", description="Calculation status")
    zones: List[ZoneOpportunityScore] = Field(
        default_factory=list,
        description="List of scored zones"
    )
    best_opportunity_zone_id: Optional[str] = Field(
        default=None,
        description="Zone ID with highest opportunity score (before risk and regulatory filtering)"
    )
    highest_opportunity_score: Optional[float] = Field(
        default=None,
        description="Highest opportunity score among candidate zones"
    )
    disclaimer: str = Field(
        default="Heuristic fishing opportunity indicator based on oceanographic convergence; not a validated probability of fish presence.",
        description="Mandatory scientific disclaimer"
    )
    source: str = Field(
        default="P6_ANALYTICS_OPPORTUNITY",
        description="Module provenance identifier"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "zones": [z.to_dict() for z in self.zones],
            "best_opportunity_zone_id": self.best_opportunity_zone_id,
            "highest_opportunity_score": self.highest_opportunity_score,
            "disclaimer": self.disclaimer,
            "source": self.source,
        }
