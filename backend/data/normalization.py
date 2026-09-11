"""Grouping, exact alignment, and small-output utilities."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import MarineObservation


def group_by_timestamp(
    observations: Iterable[MarineObservation],
) -> dict[datetime, list[MarineObservation]]:
    grouped: dict[datetime, list[MarineObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.valid_time].append(observation)
    return dict(grouped)


def group_by_location(
    observations: Iterable[MarineObservation], precision: int = 6
) -> dict[tuple[float, float], list[MarineObservation]]:
    grouped: dict[tuple[float, float], list[MarineObservation]] = defaultdict(list)
    for observation in observations:
        key = (round(observation.latitude, precision), round(observation.longitude, precision))
        grouped[key].append(observation)
    return dict(grouped)


def group_by_time_and_location(
    observations: Iterable[MarineObservation], precision: int = 6
) -> dict[tuple[datetime, float, float], list[MarineObservation]]:
    grouped: dict[tuple[datetime, float, float], list[MarineObservation]] = defaultdict(list)
    for observation in observations:
        key = (
            observation.valid_time,
            round(observation.latitude, precision),
            round(observation.longitude, precision),
        )
        grouped[key].append(observation)
    return dict(grouped)


def exact_shared_timestamps(*groups: Iterable[MarineObservation]) -> list[datetime]:
    """Return timestamps present in every input; never performs interpolation."""
    timestamp_sets = [{item.valid_time for item in group} for group in groups]
    return sorted(set.intersection(*timestamp_sets)) if timestamp_sets else []


def export_observations(
    observations: Iterable[MarineObservation], output_path: str | Path
) -> Path:
    """Export a deliberately selected observation subset as JSON or CSV."""
    path = Path(output_path).resolve()
    processed_root = (Path(__file__).resolve().parents[2] / "data" / "processed").resolve()
    if processed_root not in path.parents:
        raise ValueError(f"Output must be below {processed_root}")
    rows = [observation.to_dict() for observation in observations]
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    elif path.suffix.lower() == ".csv":
        flat_rows = []
        for row in rows:
            provenance = row.pop("provenance")
            flat_rows.append({**row, **{f"provenance_{k}": v for k, v in provenance.items()}})
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0]) if flat_rows else [])
            if flat_rows:
                writer.writeheader()
                writer.writerows(flat_rows)
    else:
        raise ValueError("Only .json and .csv exports are supported")
    return path
