"""Deterministically enrich real P5 observations with synthetic missing fields.

The input is long-form (one variable per row). The output is wide-form: one
complete zone observation per time/location group. Real values are preserved
inside ``data`` and generated values are explicitly marked in provenance.

Usage from the repository root::

    python -m backend.data.enrich_p5
    python -m backend.data.enrich_p5 --input data/processed/p5_demo.json \
        --output data/processed/p5_data.json --seed 20260917
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data" / "processed" / "p5_demo.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "processed" / "p5_data.json"
DEFAULT_SEED = 20260917

# Numeric fields that the flat MarineObservation export can represent safely.
SYNTHETIC_FIELDS: dict[str, tuple[str, float, float, int]] = {
    "chlorophyll_a_mg_m3": ("mg/m3", 0.25, 3.5, 3),
    "swell_height_m": ("m", 0.2, 2.2, 2),
    "swell_period_s": ("s", 5.0, 14.0, 1),
    "swell_direction_deg": ("degrees_true", 0.0, 360.0, 1),
    "water_level_m": ("m above chart datum", -1.0, 2.5, 2),
    "current_speed_knots": ("kn", 0.1, 1.8, 2),
    "current_direction_deg": ("degrees_true", 0.0, 360.0, 1),
}


def _group_key(row: dict[str, Any]) -> tuple[str, float, float]:
    return (row["valid_time"], float(row["latitude"]), float(row["longitude"]))


def _rng(seed: int, key: tuple[str, float, float], variable: str) -> random.Random:
    return random.Random(f"{seed}:{key[0]}:{key[1]:.6f}:{key[2]:.6f}:{variable}")


def _real_values(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, float, float], dict[str, float]]:
    values: dict[tuple[str, float, float], dict[str, float]] = defaultdict(dict)
    for row in rows:
        if row.get("source", "").startswith("synthetic"):
            continue
        value = row.get("value")
        if isinstance(value, (int, float)):
            values[_group_key(row)][row["variable"]] = float(value)
    return values


def _field_entry(row: dict[str, Any], *, synthetic: bool = False, seed: int | None = None) -> dict[str, Any]:
    provenance = dict(row.get("provenance") or {})
    if synthetic:
        provenance = {
            "provider": "Varidhi synthetic enrichment",
            "source_file": "generated",
            "raw_variable": row["variable"],
            "original_unit": row["unit"],
            "details": {
                "synthetic": True,
                "seed": seed,
                "method": "deterministic bounded enrichment",
                "derived_from": "real observations in the same time/location group",
            },
        }
    return {"value": row["value"], "unit": row["unit"], "source": row["source"],
            "quality": row.get("quality"), "provenance": provenance}


def _generate_value(variable: str, key: tuple[str, float, float], real: dict[str, float], seed: int) -> float:
    rng = _rng(seed, key, variable)
    sst = real.get("sea_surface_temperature", 28.0)
    wind = real.get("wind_speed", 8.0)
    wave = real.get("significant_wave_height", 1.0)
    wind_u = real.get("wind_u", 0.0)
    wind_v = real.get("wind_v", 0.0)

    if variable == "chlorophyll_a_mg_m3":
        return round(max(0.25, min(3.5, 1.2 + (29.0 - sst) * 0.45 + rng.uniform(-0.15, 0.15))), 3)
    if variable == "swell_height_m":
        return round(max(0.2, min(2.2, wave * 0.65 + rng.uniform(0.05, 0.35))), 2)
    if variable == "swell_period_s":
        return round(max(5.0, min(14.0, 7.0 + wave * 1.4 + rng.uniform(-0.5, 0.5))), 1)
    if variable == "swell_direction_deg":
        wind_direction = math.degrees(math.atan2(wind_u, wind_v)) % 360
        return round((wind_direction + 25.0 + rng.uniform(-12.0, 12.0)) % 360, 1)
    if variable == "water_level_m":
        return round(max(-1.0, min(2.5, 0.7 + 0.35 * math.sin(rng.random() * math.tau))), 2)
    if variable == "current_speed_knots":
        return round(max(0.1, min(1.8, 0.35 + wind * 0.025 + rng.uniform(-0.1, 0.1))), 2)
    if variable == "current_direction_deg":
        wind_direction = math.degrees(math.atan2(wind_u, wind_v)) % 360
        return round((wind_direction + 180.0 + rng.uniform(-20.0, 20.0)) % 360, 1)
    raise ValueError(f"Unsupported synthetic field: {variable}")


def enrich_rows(rows: list[dict[str, Any]], seed: int = DEFAULT_SEED) -> list[dict[str, Any]]:
    """Return one complete wide observation for each real time/location group."""
    if not rows:
        return []
    real_by_group = _real_values(rows)
    groups: dict[tuple[str, float, float], dict[str, Any]] = {}
    fields_by_group: dict[tuple[str, float, float], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        groups.setdefault(_group_key(row), row)
        fields_by_group[_group_key(row)][row["variable"]] = _field_entry(row)

    complete: list[dict[str, Any]] = []
    for key, source_row in sorted(groups.items()):
        real = real_by_group[key]
        for variable, (unit, low, high, _digits) in SYNTHETIC_FIELDS.items():
            if variable in fields_by_group[key]:
                continue
            value = _generate_value(variable, key, real, seed)
            if not low <= value <= high:
                raise AssertionError(f"generated {variable} outside bounds: {value}")
            synthetic_row = {"variable": variable, "value": value, "unit": unit,
                             "source": "synthetic-enrichment", "quality": "synthetic"}
            fields_by_group[key][variable] = _field_entry(synthetic_row, synthetic=True, seed=seed)

        data = {variable: entry["value"] for variable, entry in fields_by_group[key].items()}
        units = {variable: entry["unit"] for variable, entry in fields_by_group[key].items()}
        field_provenance = {variable: {"source": entry["source"], "quality": entry["quality"],
                                       "provenance": entry["provenance"]}
                            for variable, entry in fields_by_group[key].items()}
        complete.append({
            "zone_id": f"ZONE_{len(complete) + 1:03d}",
            "latitude": source_row["latitude"],
            "longitude": source_row["longitude"],
            "observation_time": source_row["observation_time"],
            "valid_time": source_row["valid_time"],
            "data": data,
            "units": units,
            "field_provenance": field_provenance,
            "real_field_count": sum(entry["source"] != "synthetic-enrichment" for entry in fields_by_group[key].values()),
            "synthetic_field_count": sum(entry["source"] == "synthetic-enrichment" for entry in fields_by_group[key].values()),
        })
    return complete


def enrich_file(input_path: Path | str = DEFAULT_INPUT, output_path: Path | str = DEFAULT_OUTPUT, seed: int = DEFAULT_SEED) -> Path:
    source = Path(input_path)
    destination = Path(output_path)
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Input must be a JSON array of observation objects")
    output = enrich_rows(rows, seed=seed)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    destination = enrich_file(args.input, args.output, args.seed)
    print(f"Wrote enriched observations to {destination}")


if __name__ == "__main__":
    main()
