from __future__ import annotations

from datetime import datetime, timezone

from data.models import MarineObservation, Provenance


TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


def observation(variable: str, value: float, unit: str = "1", lat: float = 12.5, lon: float = 74.75):
    return MarineObservation(
        variable, value, unit, lat, lon, TIME, TIME, "unit-test fixture", "controlled-fixture",
        "fixture", Provenance("unit-test fixture", "fixture", variable, unit)
    )


def complete_zone(sst=28.0, wind=3.0, wave=0.7, precipitation=0.0, lat=12.5, lon=74.75):
    return [
        observation("sea_surface_temperature", sst, "degC", lat, lon),
        observation("wind_speed", wind, "m/s", lat, lon),
        observation("air_temperature_2m", 28.0, "degC", lat, lon),
        observation("dewpoint_temperature_2m", 24.0, "degC", lat, lon),
        observation("total_precipitation", precipitation, "m", lat, lon),
        observation("significant_wave_height", wave, "m", lat, lon),
        observation("peak_wave_period", 10.0, "s", lat, lon),
        observation("mean_wave_direction", 180.0, "degree", lat, lon),
    ]
