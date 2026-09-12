"""Partial environmental-opportunity scoring.

The current real-data path uses SST only. Its result is neither a probability
of fish presence nor a complete fishing-suitability assessment.
"""

from __future__ import annotations

import math

from .models import Evidence, OpportunityResult
from .thresholds import AnalyticsThresholds, DEFAULT_THRESHOLDS


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _sst_score(value: float, config: AnalyticsThresholds) -> float:
    if not math.isfinite(value):
        return 0.0
    if config.sst_preferred_low_c <= value <= config.sst_preferred_high_c:
        return 100.0
    if value < config.sst_preferred_low_c:
        span = config.sst_preferred_low_c - config.sst_floor_c
        return _clamp(100.0 * (value - config.sst_floor_c) / span)
    span = config.sst_ceiling_c - config.sst_preferred_high_c
    return _clamp(100.0 * (config.sst_ceiling_c - value) / span)


def calculate_opportunity_score(
    *,
    sea_surface_temperature: Evidence | None,
    chlorophyll_a: Evidence | None = None,
    pfz_score: Evidence | None = None,
    config: AnalyticsThresholds = DEFAULT_THRESHOLDS,
) -> OpportunityResult:
    reasons: list[str] = []
    evidence = tuple(item for item in (sea_surface_temperature, chlorophyll_a, pfz_score) if item)
    missing: list[str] = []
    weighted_score = 0.0
    available_weight = 0.0
    if sea_surface_temperature and math.isfinite(sea_surface_temperature.value):
        score = _sst_score(sea_surface_temperature.value, config)
        weighted_score += score * config.opportunity_sst_evidence_weight
        available_weight += config.opportunity_sst_evidence_weight
        reasons.append(
            f"SST {sea_surface_temperature.value:.2f} {sea_surface_temperature.unit} produced a provisional SST signal score of {score:.1f}/100."
        )
    else:
        missing.append("sea_surface_temperature")
        reasons.append("SST evidence is unavailable, so no oceanographic opportunity signal could be scored.")
    if chlorophyll_a and math.isfinite(chlorophyll_a.value):
        available_weight += config.opportunity_chlorophyll_evidence_weight
        weighted_score += _clamp(chlorophyll_a.value) * config.opportunity_chlorophyll_evidence_weight
        reasons.append("A supplied chlorophyll score contributed to this extensible result.")
    else:
        missing.append("chlorophyll_a")
    if pfz_score and math.isfinite(pfz_score.value):
        available_weight += config.opportunity_pfz_evidence_weight
        weighted_score += _clamp(pfz_score.value) * config.opportunity_pfz_evidence_weight
        reasons.append("A supplied PFZ score contributed to this extensible result.")
    else:
        missing.append("pfz_score")
    if "chlorophyll_a" in missing or "pfz_score" in missing:
        reasons.append("This partial environmental opportunity score currently uses SST only; missing chlorophyll/PFZ evidence was not fabricated.")
    score = weighted_score / available_weight if available_weight else 0.0
    return OpportunityResult(round(_clamp(score), 3), round(available_weight, 3), tuple(reasons), evidence, tuple(missing))
