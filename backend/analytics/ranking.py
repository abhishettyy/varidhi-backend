"""Deterministic zone ranking."""

from __future__ import annotations

from collections.abc import Iterable

from .models import ZoneAssessment


def rank_zones(zones: Iterable[ZoneAssessment]) -> list[ZoneAssessment]:
    return sorted(
        zones,
        key=lambda zone: (-zone.final_score, -zone.confidence, zone.risk_score, zone.zone_id),
    )
