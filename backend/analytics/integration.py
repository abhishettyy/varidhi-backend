"""P5 MarineObservation to P6 zone-assessment integration."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Iterable

from data.models import MarineObservation

from .environment import calculate_environmental_context
from .models import Evidence, ZoneAssessment
from .opportunity import calculate_opportunity_score
from .risk import calculate_marine_risk
from .thresholds import AnalyticsThresholds, DEFAULT_THRESHOLDS


def _evidence(observation: MarineObservation | None) -> Evidence | None:
    if observation is None or not math.isfinite(observation.value):
        return None
    return Evidence(
        observation.variable,
        observation.value,
        observation.unit,
        observation.valid_time,
        observation.source,
        observation.dataset,
        observation.quality,
        asdict(observation.provenance),
    )


def evaluate_zone(
    zone_id: str,
    observations: Iterable[MarineObservation],
    *,
    config: AnalyticsThresholds = DEFAULT_THRESHOLDS,
) -> ZoneAssessment:
    items = list(observations)
    if not items:
        raise ValueError("A zone assessment requires observations")
    timestamps = {item.valid_time for item in items}
    locations = {(round(item.latitude, 6), round(item.longitude, 6)) for item in items}
    if len(timestamps) != 1:
        raise ValueError("Zone observations must have one exact valid timestamp")
    if len(locations) != 1:
        raise ValueError("Zone observations must have one coordinate")
    by_variable = {item.variable: item for item in items if math.isfinite(item.value)}
    get = lambda name: _evidence(by_variable.get(name))
    opportunity = calculate_opportunity_score(
        sea_surface_temperature=get("sea_surface_temperature"),
        chlorophyll_a=get("chlorophyll_a"),
        pfz_score=get("pfz_score"),
        config=config,
    )
    risk = calculate_marine_risk(
        wind_speed=get("wind_speed"),
        significant_wave_height=get("significant_wave_height"),
        peak_wave_period=get("peak_wave_period"),
        total_precipitation=get("total_precipitation"),
        mean_wave_direction=get("mean_wave_direction"),
        config=config,
    )
    context = calculate_environmental_context(
        air_temperature_2m=get("air_temperature_2m"),
        dewpoint_temperature_2m=get("dewpoint_temperature_2m"),
        total_precipitation=get("total_precipitation"),
    )
    raw_final = (
        config.opportunity_weight * opportunity.partial_environmental_opportunity_score
        - config.risk_weight * risk.risk_score
    )
    final_score = max(0.0, min(100.0, raw_final + config.risk_weight * 100.0))
    confidence = 0.4 * opportunity.confidence + 0.6 * risk.confidence
    if risk.classification == "incomplete_safety_evidence":
        classification = "insufficient_evidence"
    elif confidence < config.minimum_complete_confidence:
        classification = "insufficient_evidence"
    elif risk.classification == "high":
        classification = "high_marine_risk"
    elif final_score >= config.higher_rank_score:
        classification = "higher_ranked_environmental_opportunity"
    elif final_score >= config.moderate_rank_score:
        classification = "moderate_environmental_opportunity"
    else:
        classification = "lower_ranked_environmental_opportunity"
    missing = tuple(dict.fromkeys((*opportunity.missing_evidence, *risk.missing_evidence, *context.missing_evidence)))
    reasons = (
        "Scores use provisional configurable thresholds that require domain validation.",
        *opportunity.reasons,
        *risk.reasons,
        *context.reasons,
    )
    evidence = tuple(
        _evidence(item) for item in items if math.isfinite(item.value)
    )
    latitude, longitude = next(iter(locations))
    return ZoneAssessment(
        zone_id,
        latitude,
        longitude,
        next(iter(timestamps)),
        opportunity.partial_environmental_opportunity_score,
        risk.risk_score,
        round(final_score, 3),
        round(confidence, 3),
        classification,
        tuple(reasons),
        tuple(item for item in evidence if item is not None),
        missing,
    )
