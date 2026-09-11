"""Non-dominant environmental context calculations."""

from __future__ import annotations

import math

from .models import EnvironmentalContext, Evidence


def calculate_environmental_context(
    *, air_temperature_2m: Evidence | None,
    dewpoint_temperature_2m: Evidence | None,
    total_precipitation: Evidence | None,
) -> EnvironmentalContext:
    evidence = tuple(item for item in (air_temperature_2m, dewpoint_temperature_2m, total_precipitation) if item)
    missing: list[str] = []
    reasons: list[str] = []
    spread = None
    if air_temperature_2m and dewpoint_temperature_2m and all(
        math.isfinite(item.value) for item in (air_temperature_2m, dewpoint_temperature_2m)
    ):
        spread = air_temperature_2m.value - dewpoint_temperature_2m.value
        reasons.append(f"Air-dewpoint spread is {spread:.2f} degC.")
    else:
        if not air_temperature_2m:
            missing.append("air_temperature_2m")
        if not dewpoint_temperature_2m:
            missing.append("dewpoint_temperature_2m")
    precipitation = None
    if total_precipitation and math.isfinite(total_precipitation.value):
        precipitation = total_precipitation.value
        reasons.append(f"Accumulated precipitation is {precipitation:.6f} {total_precipitation.unit}.")
    else:
        missing.append("total_precipitation")
    if not reasons:
        reasons.append("Environmental context evidence is incomplete.")
    return EnvironmentalContext(spread, precipitation, tuple(reasons), evidence, tuple(missing))
