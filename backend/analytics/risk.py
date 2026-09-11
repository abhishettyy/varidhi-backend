"""Deterministic, explainable marine-risk scoring."""

from __future__ import annotations

import math

from .models import Evidence, MarineRiskResult
from .thresholds import AnalyticsThresholds, DEFAULT_THRESHOLDS


def _scaled(value: float, low: float, high: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(100.0, 100.0 * (value - low) / (high - low)))


def calculate_marine_risk(
    *,
    wind_speed: Evidence | None,
    significant_wave_height: Evidence | None,
    peak_wave_period: Evidence | None,
    total_precipitation: Evidence | None,
    mean_wave_direction: Evidence | None = None,
    config: AnalyticsThresholds = DEFAULT_THRESHOLDS,
) -> MarineRiskResult:
    evidence = tuple(
        item for item in (wind_speed, significant_wave_height, peak_wave_period, total_precipitation, mean_wave_direction) if item
    )
    missing: list[str] = []
    reasons: list[str] = []
    weighted = 0.0
    available_weight = 0.0
    if wind_speed and math.isfinite(wind_speed.value):
        component = _scaled(wind_speed.value, config.wind_low_mps, config.wind_high_mps)
        weighted += component * config.risk_wind_weight
        available_weight += config.risk_wind_weight
        reasons.append(f"Wind speed contributed {component:.1f}/100 to the provisional risk components.")
    else:
        missing.append("wind_speed")
        reasons.append("Wind evidence is missing; the result cannot be treated as confirmed safe.")
    if significant_wave_height and math.isfinite(significant_wave_height.value):
        component = _scaled(significant_wave_height.value, config.wave_low_m, config.wave_high_m)
        weighted += component * config.risk_wave_weight
        available_weight += config.risk_wave_weight
        reasons.append(f"Significant wave height contributed {component:.1f}/100 to the provisional risk components.")
    else:
        missing.append("significant_wave_height")
        reasons.append("Wave-height evidence is missing; the result cannot be treated as confirmed safe.")
    if total_precipitation and math.isfinite(total_precipitation.value):
        component = _scaled(total_precipitation.value, config.precipitation_low_m, config.precipitation_high_m)
        weighted += component * config.risk_precipitation_weight
        available_weight += config.risk_precipitation_weight
        reasons.append(f"Accumulated precipitation contributed {component:.1f}/100 to the provisional risk components.")
    else:
        missing.append("total_precipitation")
    if not peak_wave_period or not math.isfinite(peak_wave_period.value):
        missing.append("peak_wave_period")
    if not mean_wave_direction or not math.isfinite(mean_wave_direction.value):
        missing.append("mean_wave_direction")
    score = weighted / available_weight if available_weight else 0.0
    if "wind_speed" in missing or "significant_wave_height" in missing:
        classification = "incomplete_safety_evidence"
    elif score >= config.high_risk_score:
        classification = "high"
    elif score >= config.elevated_risk_score:
        classification = "elevated"
    else:
        classification = "low"
    if not reasons:
        reasons.append("No finite marine-risk evidence was available.")
    return MarineRiskResult(round(score, 3), classification, round(available_weight, 3), tuple(reasons), evidence, tuple(missing))
