"""Schemas for P6 Marine Analytics Engines (Opportunity, Marine Risk & Regulatory Compliance).

Defines typed structures for weights, raw inputs, normalized components,
zone-level evaluations, vessel sensitivity profiles, spatial restrictions, and batch analysis results.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


# =====================================================================
# 1. OPPORTUNITY SCORING SCHEMAS
# =====================================================================

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


# =====================================================================
# 2. MARINE RISK SCHEMAS
# =====================================================================

class RiskSeverity(str, Enum):
    """Deterministic marine condition risk severity classifications."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class RiskSeverityThresholds(BaseModel):
    """Configurable boundaries for risk severity tiers."""
    low_max: float = Field(default=30.0, description="Upper threshold for LOW risk (inclusive)")
    moderate_max: float = Field(default=60.0, description="Upper threshold for MODERATE risk (inclusive)")
    high_max: float = Field(default=80.0, description="Upper threshold for HIGH risk (inclusive)")


class RiskWeights(BaseModel):
    """
    Configurable multicriteria weights for marine risk calculation.
    Defaults represent engineering heuristics:
    - wave: 0.35 (Significant wave height is primary craft capsizing/slamming hazard)
    - wind: 0.25 (Sustained wind speed impacts maneuverability and drift)
    - gust: 0.15 (Wind gusts generate sudden roll/pitch instability)
    - swell: 0.15 (Underlying long-wavelength ocean swell adds heave energy)
    """
    wave: float = Field(default=0.35, description="Weight for significant wave height (0.0 - 1.0)")
    wind: float = Field(default=0.25, description="Weight for sustained wind speed (0.0 - 1.0)")
    gust: float = Field(default=0.15, description="Weight for wind gust speed (0.0 - 1.0)")
    swell: float = Field(default=0.15, description="Weight for swell height (0.0 - 1.0)")

    def to_dict(self) -> Dict[str, float]:
        return {
            "wave": self.wave,
            "wind": self.wind,
            "gust": self.gust,
            "swell": self.swell,
        }


class VesselProfile(BaseModel):
    """
    Vessel sensitivity profile modifying craft-specific risk thresholds.
    """
    name: str = Field(default="default", description="Vessel profile identifier")
    sensitivity_multiplier: float = Field(
        default=1.0,
        description="Multiplier applied to base risk score (>1.0 = more vulnerable, <1.0 = more seaworthy)"
    )
    max_safe_wave_m: float = Field(default=2.0, description="Heuristic operational wave threshold in meters")
    max_safe_wind_kts: float = Field(default=20.0, description="Heuristic operational wind threshold in knots")
    description: str = Field(default="Standard coastal motorized fishing vessel", description="Profile description")


class RawRiskFeatures(BaseModel):
    """Extracted raw marine meteorological and sea-state parameters for a zone."""
    zone_id: str = Field(..., description="Unique zone identifier")
    wave_height_m: Optional[float] = Field(default=None, description="Significant wave height in meters")
    wave_period_sec: Optional[float] = Field(default=None, description="Peak / mean wave period in seconds")
    wave_direction_deg: Optional[float] = Field(default=None, description="Wave propagation direction in degrees")
    wind_speed_knots: Optional[float] = Field(default=None, description="Sustained surface wind speed in knots")
    wind_gust_knots: Optional[float] = Field(default=None, description="Wind gust speed in knots")
    wind_direction_deg: Optional[float] = Field(default=None, description="Wind direction in degrees")
    wind_direction_cardinal: Optional[str] = Field(default=None, description="Cardinal wind direction (e.g. 'WSW')")
    swell_height_m: Optional[float] = Field(default=None, description="Primary swell height in meters")
    swell_period_sec: Optional[float] = Field(default=None, description="Primary swell period in seconds")
    swell_direction_deg: Optional[float] = Field(default=None, description="Primary swell direction in degrees")
    tide_height_m: Optional[float] = Field(default=None, description="Tidal elevation in meters")
    current_speed_knots: Optional[float] = Field(default=None, description="Surface current speed in knots")
    latitude: Optional[float] = Field(default=None, description="Centroid latitude")
    longitude: Optional[float] = Field(default=None, description="Centroid longitude")


class RiskComponents(BaseModel):
    """Normalized sub-scores for each hazard feature (0.0 to 100.0; higher is more dangerous)."""
    wave: Optional[float] = Field(default=None, description="Normalized wave height risk sub-score (0.0 - 100.0)")
    wind: Optional[float] = Field(default=None, description="Normalized wind speed risk sub-score (0.0 - 100.0)")
    gust: Optional[float] = Field(default=None, description="Normalized wind gust risk sub-score (0.0 - 100.0)")
    swell: Optional[float] = Field(default=None, description="Normalized swell height risk sub-score (0.0 - 100.0)")
    period_context: Optional[str] = Field(
        default=None,
        description="Contextual physical sea-state diagnosis (steepness/shoaling character)"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wave": self.wave,
            "wind": self.wind,
            "gust": self.gust,
            "swell": self.swell,
            "period_context": self.period_context,
        }


class ZoneRiskScore(BaseModel):
    """
    Deterministic marine condition risk evaluation for an individual candidate zone.
    """
    zone_id: str = Field(..., description="Unique zone identifier")
    risk_score: float = Field(..., description="Aggregated marine condition risk score (0.0 - 100.0)")
    severity: str = Field(default="LOW", description="Risk severity tier: 'LOW', 'MODERATE', 'HIGH', 'SEVERE'")
    is_safe_heuristic: bool = Field(
        default=True,
        description="True if risk score is within heuristic safe operational threshold (<50.0)"
    )
    components: RiskComponents = Field(
        default_factory=RiskComponents,
        description="Normalized sub-score breakdown"
    )
    raw_features: RawRiskFeatures = Field(..., description="Raw physical inputs used for calculation")
    vessel_profile_applied: str = Field(default="default", description="Vessel profile applied to calculation")
    weights_used: Dict[str, float] = Field(
        default_factory=dict,
        description="Effective weights applied after dynamic missing-data renormalization"
    )
    missing_features: List[str] = Field(
        default_factory=list,
        description="List of physical variables that were unavailable"
    )
    factors: List[str] = Field(
        default_factory=list,
        description="Machine-readable physical factor tokens"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Specific operational warnings triggered by threshold breaches"
    )
    source: str = Field(default="derived", description="Provenance origin")
    method: str = Field(
        default="heuristic_weighted_multicriteria",
        description="Algorithmic scoring method"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "risk_score": self.risk_score,
            "severity": self.severity,
            "is_safe_heuristic": self.is_safe_heuristic,
            "components": self.components.to_dict(),
            "raw_features": self.raw_features.model_dump() if hasattr(self.raw_features, "model_dump") else self.raw_features.__dict__,
            "vessel_profile_applied": self.vessel_profile_applied,
            "weights_used": self.weights_used,
            "missing_features": self.missing_features,
            "factors": self.factors,
            "warnings": self.warnings,
            "source": self.source,
            "method": self.method,
        }


class RiskAnalysisResult(BaseModel):
    """Batch marine condition risk evaluation across multiple candidate zones."""
    status: str = Field(default="success", description="Calculation status: 'success', 'partial', 'insufficient_data'")
    zones: List[ZoneRiskScore] = Field(default_factory=list, description="List of evaluated zones")
    lowest_risk_zone_id: Optional[str] = Field(
        default=None,
        description="Zone ID with lowest marine risk score"
    )
    lowest_risk_score: Optional[float] = Field(
        default=None,
        description="Lowest marine risk score among evaluated zones"
    )
    vessel_profile: str = Field(default="default", description="Vessel profile utilized")
    disclaimer: str = Field(
        default="Heuristic marine-condition risk indicator based on coastal meteorological and wave observations; not an official maritime safety clearance or statutory navigation certificate.",
        description="Mandatory marine safety disclaimer"
    )
    source: str = Field(
        default="P6_ANALYTICS_RISK",
        description="Module provenance identifier"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "zones": [z.to_dict() for z in self.zones],
            "lowest_risk_zone_id": self.lowest_risk_zone_id,
            "lowest_risk_score": self.lowest_risk_score,
            "vessel_profile": self.vessel_profile,
            "disclaimer": self.disclaimer,
            "source": self.source,
        }


# =====================================================================
# 3. REGULATORY & MARINE SPATIAL RESTRICTIONS SCHEMAS
# =====================================================================

class RestrictionType(str, Enum):
    """Categories of marine spatial and regulatory restrictions."""
    MPA = "MPA"
    NAVAL_ZONE = "NAVAL_ZONE"
    SHIPPING_LANE = "SHIPPING_LANE"
    MARITIME_BOUNDARY = "MARITIME_BOUNDARY"
    TEMPORARY_CLOSURE = "TEMPORARY_CLOSURE"
    FISHING_RESTRICTED_ZONE = "FISHING_RESTRICTED_ZONE"
    UNKNOWN = "UNKNOWN"


class ComplianceStatus(str, Enum):
    """Hard filter compliance classifications."""
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class Restriction(BaseModel):
    """
    Typed definition for an individual marine spatial or temporal restriction.
    """
    restriction_id: str = Field(..., description="Unique restriction identifier (e.g. 'MPA_NETRAVATI_01')")
    restriction_type: str = Field(
        default=RestrictionType.FISHING_RESTRICTED_ZONE.value,
        description="Category: MPA, NAVAL_ZONE, SHIPPING_LANE, MARITIME_BOUNDARY, TEMPORARY_CLOSURE, FISHING_RESTRICTED_ZONE, UNKNOWN"
    )
    name: str = Field(..., description="Descriptive name of the restricted area or regulation")
    status: str = Field(default="active", description="Regulatory status: 'active', 'inactive', 'expired', 'scheduled'")
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON geometry (Polygon, MultiPolygon, Point + radius_km/nm) or None for zone reference"
    )
    zone_id: Optional[str] = Field(
        default=None,
        description="Direct candidate zone ID binding if designated by zone key (e.g. 'ZONE_C')"
    )
    reason: str = Field(..., description="Legal rationale or conservation objective (e.g. 'Coral sanctuary & naval exercise zone')")
    source: str = Field(default="synthetic", description="Issuing authority or provenance tag")
    valid_from: Optional[str] = Field(
        default=None,
        description="ISO 8601 start timestamp of restriction validity window (None for permanent)"
    )
    valid_to: Optional[str] = Field(
        default=None,
        description="ISO 8601 end timestamp of restriction validity window (None for permanent)"
    )
    severity: str = Field(
        default="HARD_BLOCK",
        description="Constraint severity: 'HARD_BLOCK' (prohibits fishing) or 'WARNING' (navigational advisory)"
    )
    is_hard_block: bool = Field(
        default=True,
        description="If True, any active intersection will immediately disqualify the candidate zone"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional gazette notification numbers, jurisdictional coordinates, or buffer widths"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "restriction_id": self.restriction_id,
            "restriction_type": self.restriction_type,
            "name": self.name,
            "status": self.status,
            "geometry": self.geometry,
            "zone_id": self.zone_id,
            "reason": self.reason,
            "source": self.source,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "severity": self.severity,
            "is_hard_block": self.is_hard_block,
            "metadata": self.metadata,
        }


class RegulatoryCheck(BaseModel):
    """
    Deterministic compliance evaluation result for an individual candidate zone.
    """
    zone_id: str = Field(..., description="Unique zone identifier")
    status: str = Field(
        default=ComplianceStatus.ELIGIBLE.value,
        description="Compliance status: ELIGIBLE, BLOCKED, UNKNOWN, INSUFFICIENT_DATA"
    )
    eligible: bool = Field(
        default=True,
        description="True only if zone is legally clear for fishing operations (not blocked and known)"
    )
    hard_block: bool = Field(
        default=False,
        description="True if an active hard restriction prohibits consideration"
    )
    restrictions_found: List[Restriction] = Field(
        default_factory=list,
        description="All restrictions intersecting this zone"
    )
    blocking_restrictions: List[Restriction] = Field(
        default_factory=list,
        description="Active hard restrictions causing the block"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Advisory warnings (e.g. shipping lane traffic, caution corridors)"
    )
    reasons: List[str] = Field(
        default_factory=list,
        description="Human- and machine-readable explanations for decision"
    )
    checked_at: Optional[str] = Field(
        default=None,
        description="Reference timestamp used for temporal validation"
    )
    provenance: str = Field(
        default="synthetic_regulatory_fixture",
        description="Provenance dataset tag"
    )
    method: str = Field(
        default="deterministic_spatial_regulatory_check",
        description="Evaluation method identifier"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "status": self.status,
            "eligible": self.eligible,
            "hard_block": self.hard_block,
            "restrictions_found": [r.to_dict() for r in self.restrictions_found],
            "blocking_restrictions": [r.to_dict() for r in self.blocking_restrictions],
            "warnings": self.warnings,
            "reasons": self.reasons,
            "checked_at": self.checked_at,
            "provenance": self.provenance,
            "method": self.method,
        }


class RegulatoryDecision(BaseModel):
    """
    Decision record summarizing regulatory clearance for single-zone or multi-zone decision nodes.
    """
    status: str = Field(..., description="Compliance status: ELIGIBLE, BLOCKED, UNKNOWN, INSUFFICIENT_DATA")
    eligible: bool = Field(..., description="True if usable")
    hard_block: bool = Field(..., description="True if prohibited")
    reasons: List[str] = Field(default_factory=list, description="Explanatory reasons")
    warnings: List[str] = Field(default_factory=list, description="Advisory warnings")
    restrictions: List[Restriction] = Field(default_factory=list, description="Encountered restrictions")
    provenance: str = Field(default="synthetic_regulatory_fixture", description="Provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "eligible": self.eligible,
            "hard_block": self.hard_block,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "restrictions": [r.to_dict() for r in self.restrictions],
            "provenance": self.provenance,
        }


class RegulatoryAnalysisResult(BaseModel):
    """Batch regulatory compliance evaluation across multiple candidate zones."""
    status: str = Field(default="success", description="Execution status: 'success', 'partial', 'insufficient_data'")
    zones: List[RegulatoryCheck] = Field(default_factory=list, description="List of evaluated zone checks")
    eligible_zone_ids: List[str] = Field(default_factory=list, description="List of zone IDs cleared for fishing")
    blocked_zone_ids: List[str] = Field(default_factory=list, description="List of prohibited zone IDs")
    unknown_zone_ids: List[str] = Field(default_factory=list, description="List of unresolved / unknown zone IDs")
    disclaimer: str = Field(
        default="Synthetic regulatory fixture — not an official legal boundary or government navigation advisory.",
        description="Mandatory legal disclaimer"
    )
    source: str = Field(default="P6_ANALYTICS_REGULATORY", description="Module provenance identifier")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "zones": [z.to_dict() for z in self.zones],
            "eligible_zone_ids": self.eligible_zone_ids,
            "blocked_zone_ids": self.blocked_zone_ids,
            "unknown_zone_ids": self.unknown_zone_ids,
            "disclaimer": self.disclaimer,
            "source": self.source,
        }


# =====================================================================
# 4. ZONE RANKING & DECISION SYNTHESIS SCHEMAS (PHASE 6D)
# =====================================================================

class RejectionCode(str, Enum):
    """Machine-readable constraint violation and rejection classification codes."""
    REJECTED_LEGAL = "REJECTED_LEGAL"
    REJECTED_RISK = "REJECTED_RISK"
    REJECTED_DISTANCE = "REJECTED_DISTANCE"
    REJECTED_LOW_OPPORTUNITY = "REJECTED_LOW_OPPORTUNITY"
    REJECTED_INSUFFICIENT_DATA = "REJECTED_INSUFFICIENT_DATA"
    REJECTED_UNKNOWN_REGULATORY_STATUS = "REJECTED_UNKNOWN_REGULATORY_STATUS"


class RankingWeights(BaseModel):
    """
    Configurable multicriteria weights for eligible candidate zone ranking.
    Defaults represent project decision heuristics:
    - opportunity: 0.60 (Primary objective to maximize potential fishing catch)
    - risk: 0.25 (Safety penalty based on physical marine condition hazards)
    - distance: 0.15 (Fuel / operational proximity efficiency)
    """
    opportunity: float = Field(
        default=0.60,
        description="Weight for oceanographic fishing opportunity score (0.0 - 1.0)"
    )
    risk: float = Field(
        default=0.25,
        description="Weight for physical marine risk penalty component (0.0 - 1.0)"
    )
    distance: float = Field(
        default=0.15,
        description="Weight for harbor/vessel proximity component (0.0 - 1.0)"
    )

    def to_dict(self) -> Dict[str, float]:
        return {
            "opportunity": self.opportunity,
            "risk": self.risk,
            "distance": self.distance,
        }


class DecisionPolicy(BaseModel):
    """
    Configurable project decision policy thresholds and constraint rules.
    
    NOTE: These thresholds represent heuristic project decision policies,
    NOT official statutory maritime safety certifications or government navigation mandates.
    """
    max_risk_score: float = Field(
        default=50.0,
        description="Maximum permissible marine condition risk score (inclusive threshold; > max is rejected)"
    )
    min_opportunity_score: float = Field(
        default=0.0,
        description="Minimum acceptable opportunity score for recommendation eligibility (0.0 - 100.0)"
    )
    max_distance_nm: float = Field(
        default=30.0,
        description="Maximum operational range cutoff distance in nautical miles"
    )
    require_regulatory_eligibility: bool = Field(
        default=True,
        description="Strictly require confirmed regulatory clearance before zone ranking"
    )
    unknown_regulatory_action: str = Field(
        default="exclude",
        description="Action for UNKNOWN regulatory status: 'exclude' (reject) or 'hold'"
    )
    insufficient_data_action: str = Field(
        default="reject",
        description="Action when mandatory analytics inputs are missing: 'reject' or 'warn'"
    )
    policy_description: str = Field(
        default="Project heuristic decision threshold policy",
        description="Human-readable decision policy descriptor"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_risk_score": self.max_risk_score,
            "min_opportunity_score": self.min_opportunity_score,
            "max_distance_nm": self.max_distance_nm,
            "require_regulatory_eligibility": self.require_regulatory_eligibility,
            "unknown_regulatory_action": self.unknown_regulatory_action,
            "insufficient_data_action": self.insufficient_data_action,
            "policy_description": self.policy_description,
        }


class RankingComponents(BaseModel):
    """Sub-components contributing to the deterministic ranking score (each 0.0 - 100.0)."""
    opportunity: float = Field(
        ...,
        description="Direct opportunity score component (0.0 - 100.0)"
    )
    risk_inverse: float = Field(
        ...,
        description="Inverted risk safety component (100.0 - risk_score)"
    )
    distance: float = Field(
        ...,
        description="Normalized proximity component: max(0, 100 * (1 - dist / max_dist))"
    )

    def to_dict(self) -> Dict[str, float]:
        return {
            "opportunity": round(self.opportunity, 2),
            "risk_inverse": round(self.risk_inverse, 2),
            "distance": round(self.distance, 2),
        }


class CandidateZoneEvaluation(BaseModel):
    """
    Comprehensive multi-engine evaluation and ranking record for a single candidate zone.
    """
    zone_id: str = Field(..., description="Unique zone identifier (e.g. 'ZONE_A')")
    opportunity_score: Optional[float] = Field(
        default=None,
        description="Opportunity score from Phase 6A (0.0 - 100.0)"
    )
    risk_score: Optional[float] = Field(
        default=None,
        description="Physical condition risk score from Phase 6B (0.0 - 100.0)"
    )
    risk_severity: Optional[str] = Field(
        default=None,
        description="Risk severity classification ('LOW', 'MODERATE', 'HIGH', 'SEVERE')"
    )
    regulatory_status: str = Field(
        default="UNKNOWN",
        description="Regulatory clearance status ('ELIGIBLE', 'BLOCKED', 'UNKNOWN', 'INSUFFICIENT_DATA')"
    )
    distance_nm: Optional[float] = Field(
        default=None,
        description="Distance from reference port or vessel in nautical miles"
    )
    eligible: bool = Field(
        default=False,
        description="True if zone passed all hard policy constraints (legal, risk threshold, distance)"
    )
    status: str = Field(
        default="PENDING",
        description="Final status: 'SELECTED', 'ELIGIBLE', or a RejectionCode string"
    )
    rejection_codes: List[str] = Field(
        default_factory=list,
        description="Machine-readable rejection codes if disqualified"
    )
    reasons: List[str] = Field(
        default_factory=list,
        description="Explanatory rationales for selection or rejection"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Operational or navigation advisory warnings"
    )
    ranking_score: Optional[float] = Field(
        default=None,
        description="Final deterministic ranking score (0.0 - 100.0; populated only for eligible zones)"
    )
    components: Optional[RankingComponents] = Field(
        default=None,
        description="Ranking sub-component breakdown"
    )
    weights_used: Optional[Dict[str, float]] = Field(
        default=None,
        description="Ranking weights applied to this calculation"
    )
    raw_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Auxiliary spatial coordinates, species, or oceanographic metadata"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "opportunity_score": self.opportunity_score,
            "risk_score": self.risk_score,
            "risk_severity": self.risk_severity,
            "regulatory_status": self.regulatory_status,
            "distance_nm": self.distance_nm,
            "eligible": self.eligible,
            "status": self.status,
            "is_legal": self.regulatory_status == ComplianceStatus.ELIGIBLE.value,
            "is_safe": self.risk_score is not None and self.risk_score <= 50.0,
            "rejection_codes": self.rejection_codes,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "ranking_score": self.ranking_score,
            "components": self.components.to_dict() if self.components else None,
            "weights_used": self.weights_used,
            "raw_metadata": self.raw_metadata,
        }


class DecisionResult(BaseModel):
    """
    Final synthesized decision output containing ranked eligible zones,
    rejected candidates with explicit codes, top selection, and complete provenance.
    """
    status: str = Field(
        default="success",
        description="Execution status: 'success', 'no_eligible_zones', 'insufficient_data'"
    )
    selected_zone: Optional[CandidateZoneEvaluation] = Field(
        default=None,
        description="Top recommended zone meeting all hard constraints and highest ranking score"
    )
    ranked_zones: List[CandidateZoneEvaluation] = Field(
        default_factory=list,
        description="Surviving eligible zones sorted in descending order of ranking score"
    )
    rejected_zones: List[CandidateZoneEvaluation] = Field(
        default_factory=list,
        description="Candidate zones disqualified by legal, risk, distance, or data constraints"
    )
    all_evaluations: List[CandidateZoneEvaluation] = Field(
        default_factory=list,
        description="Complete list of all candidate evaluations preserved for full transparency"
    )
    decision_policy: DecisionPolicy = Field(
        default_factory=DecisionPolicy,
        description="Active decision policy parameters and thresholds"
    )
    ranking_weights: RankingWeights = Field(
        default_factory=RankingWeights,
        description="Active ranking component weights"
    )
    rationale: List[str] = Field(
        default_factory=list,
        description="High-level machine-readable decision rationale summary statements"
    )
    provenance: Dict[str, Any] = Field(
        default_factory=dict,
        description="Lineage tracking sources for opportunity, risk, regulatory, and distance"
    )
    disclaimer: str = Field(
        default="Decision output is a deterministic demonstration heuristic using synthetic data and does not constitute official fishing, navigation, or maritime safety advice.",
        description="Mandatory scientific and legal disclaimer"
    )
    source: str = Field(
        default="P6_ANALYTICS_DECISION",
        description="Module provenance identifier"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "selected_zone": self.selected_zone.to_dict() if self.selected_zone else None,
            "ranked_zones": [z.to_dict() for z in self.ranked_zones],
            "rejected_zones": [z.to_dict() for z in self.rejected_zones],
            "all_evaluations": [z.to_dict() for z in self.all_evaluations],
            "decision_policy": self.decision_policy.to_dict(),
            "ranking_weights": self.ranking_weights.to_dict(),
            "rationale": self.rationale,
            "provenance": self.provenance,
            "disclaimer": self.disclaimer,
            "source": self.source,
        }

