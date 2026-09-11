"""Explainable result models produced by P6."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Evidence:
    variable: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    dataset: str
    quality: str | None
    provenance: dict[str, Any]


@dataclass(frozen=True, slots=True)
class OpportunityResult:
    partial_environmental_opportunity_score: float
    confidence: float
    reasons: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    missing_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MarineRiskResult:
    risk_score: float
    classification: str
    confidence: float
    reasons: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    missing_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EnvironmentalContext:
    air_dewpoint_spread_c: float | None
    precipitation_m: float | None
    reasons: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    missing_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ZoneAssessment:
    zone_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    partial_environmental_opportunity_score: float
    risk_score: float
    final_score: float
    confidence: float
    classification: str
    reasons: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    missing_evidence: tuple[str, ...]
