"""End-to-end P5 demonstration using a small, exact-time real-data subset."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .loaders.grib_environment import GribEnvironmentLoader
from .loaders.waves import WaveLoader
from .normalization import exact_shared_timestamps, export_observations, group_by_time_and_location


ROOT = Path(__file__).resolve().parents[2]
GRIB_PATH = ROOT / "data" / "raw" / "grib" / "data.grib"
WAVE_PATH = ROOT / "data" / "raw" / "waves" / "waves_mangalore_20230101.nc"
DEMO_TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


def main() -> None:
    grib = GribEnvironmentLoader(GRIB_PATH)
    waves = WaveLoader(WAVE_PATH)
    if DEMO_TIME not in set(grib.available_times) & set(waves.available_times):
        raise RuntimeError(f"No exact shared timestamp at {DEMO_TIME.isoformat()}")
    variables = [
        "sea_surface_temperature", "wind_u", "wind_v", "wind_speed",
        "air_temperature_2m", "dewpoint_temperature_2m", "total_precipitation",
    ]
    wave_variables = ["significant_wave_height", "peak_wave_period", "mean_wave_direction"]
    bounds = (11.5, 14.5), (73.0, 76.0)
    environment = grib.load(
        start_time=DEMO_TIME, variables=variables,
        latitude_range=bounds[0], longitude_range=bounds[1],
    )
    wave_observations = waves.load(
        start_time=DEMO_TIME, variables=wave_variables,
        latitude_range=bounds[0], longitude_range=bounds[1],
    )
    shared = exact_shared_timestamps(environment, wave_observations)
    if shared != [DEMO_TIME]:
        raise RuntimeError("The loaders did not preserve the exact shared timestamp")
    grouped = group_by_time_and_location([*environment, *wave_observations])
    complete = []
    required = set(variables + wave_variables)
    for key, observations in sorted(grouped.items()):
        by_variable = {item.variable: item for item in observations}
        if required <= by_variable.keys():
            complete.append((key, by_variable))
        if len(complete) == 3:
            break
    if not complete:
        raise RuntimeError("No shared valid ocean locations were found")
    selected = [item for _, group in complete for item in group.values()]
    export_path = export_observations(selected, ROOT / "data" / "processed" / "p5_demo.json")
    labels = {
        "sea_surface_temperature": "SST", "wind_u": "Wind U", "wind_v": "Wind V",
        "wind_speed": "Wind speed", "air_temperature_2m": "Air temperature",
        "dewpoint_temperature_2m": "Dewpoint", "total_precipitation": "Precipitation",
        "significant_wave_height": "Wave height", "peak_wave_period": "Wave period",
        "mean_wave_direction": "Wave direction",
    }
    for (timestamp, latitude, longitude), values in complete:
        print(f"Location: {latitude:.3f}, {longitude:.3f}")
        print(f"Timestamp: {timestamp.isoformat()}")
        for variable in variables + wave_variables:
            item = values[variable]
            print(f"{labels[variable]}: {item.value:.4f} {item.unit}")
        print(f"Providers: {sorted({item.provenance.provider for item in values.values()})}")
        print()
    print(f"Exported {len(selected)} observations to {export_path}")


if __name__ == "__main__":
    main()
