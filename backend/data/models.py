"""Common normalized observation model used by P5 loaders."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Provenance:
    provider: str
    source_file: str
    raw_variable: str
    original_unit: str
    details: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class MarineObservation:
    variable: str
    value: float
    unit: str
    latitude: float
    longitude: float
    observation_time: datetime
    valid_time: datetime
    source: str
    dataset: str
    quality: str | None
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["observation_time"] = self.observation_time.isoformat()
        result["valid_time"] = self.valid_time.isoformat()
        return result
