"""Central provisional configuration for P6.

These values are configurable MVP heuristics and require domain validation.
They are not presented as scientifically validated fishing or safety limits.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnalyticsThresholds:
    # SST values anywhere in this provisional preferred band receive the same
    # maximum SST-only signal score. This intentionally does not imply a
    # probability of fish presence or a validated suitability relationship.
    sst_floor_c: float = 20.0
    sst_preferred_low_c: float = 26.0
    sst_preferred_high_c: float = 30.0
    sst_ceiling_c: float = 34.0
    opportunity_sst_evidence_weight: float = 0.4
    opportunity_chlorophyll_evidence_weight: float = 0.3
    opportunity_pfz_evidence_weight: float = 0.3
    wind_low_mps: float = 5.0
    wind_high_mps: float = 15.0
    wave_low_m: float = 1.0
    wave_high_m: float = 4.0
    precipitation_low_m: float = 0.001
    precipitation_high_m: float = 0.02
    risk_wind_weight: float = 0.4
    risk_wave_weight: float = 0.4
    risk_precipitation_weight: float = 0.2
    opportunity_weight: float = 0.6
    risk_weight: float = 0.4
    high_risk_score: float = 70.0
    elevated_risk_score: float = 40.0
    higher_rank_score: float = 65.0
    moderate_rank_score: float = 45.0
    minimum_complete_confidence: float = 0.5


DEFAULT_THRESHOLDS = AnalyticsThresholds()
