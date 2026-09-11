"""Time metadata helpers for observations."""

from __future__ import annotations

from datetime import datetime

from .models import MarineObservation


def age_at(observation: MarineObservation, reference_time: datetime) -> float:
    """Return observation age in seconds at an explicit reference time."""
    return (reference_time - observation.valid_time).total_seconds()
