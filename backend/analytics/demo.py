"""Historical 2023 P5-to-P6 zone-ranking demonstration."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from data.loaders.grib_environment import GribEnvironmentLoader
from data.loaders.waves import WaveLoader
from data.normalization import group_by_time_and_location

from .integration import evaluate_zone
from .ranking import rank_zones


ROOT = Path(__file__).resolve().parents[2]
TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


def main() -> None:
    grib = GribEnvironmentLoader(ROOT / "data/raw/grib/data.grib")
    waves = WaveLoader(ROOT / "data/raw/waves/waves_mangalore_20230101.nc")
    environment = grib.load(
        start_time=TIME,
        variables=["sea_surface_temperature", "wind_speed", "air_temperature_2m", "dewpoint_temperature_2m", "total_precipitation"],
        latitude_range=(11.5, 14.5), longitude_range=(73.0, 76.0),
    )
    wave_data = waves.load(
        start_time=TIME,
        variables=["significant_wave_height", "peak_wave_period", "mean_wave_direction"],
        latitude_range=(11.5, 14.5), longitude_range=(73.0, 76.0),
    )
    grouped = group_by_time_and_location([*environment, *wave_data])
    required = {
        "sea_surface_temperature", "wind_speed", "air_temperature_2m",
        "dewpoint_temperature_2m", "total_precipitation", "significant_wave_height",
        "peak_wave_period", "mean_wave_direction",
    }
    assessments = []
    for (timestamp, latitude, longitude), observations in sorted(grouped.items()):
        if required <= {item.variable for item in observations}:
            assessments.append(evaluate_zone(f"zone-{latitude:.3f}-{longitude:.3f}", observations))
        if len(assessments) == 5:
            break
    ranked = rank_zones(assessments)
    print("Historical 2023 partial environmental opportunity and marine risk evaluation")
    print("Opportunity currently uses SST only; chlorophyll and PFZ are unavailable.")
    print("All threshold values are provisional, configurable, and require domain validation.")
    print("The opportunity score is not a probability of fish presence.")
    print("This is not a PFZ or fishing-suitability prediction.\n")
    for rank, zone in enumerate(ranked, 1):
        print(f"Rank {rank}: {zone.zone_id}")
        print(f"Location: {zone.latitude:.3f}, {zone.longitude:.3f}")
        print(f"Timestamp: {zone.timestamp.isoformat()}")
        print(
            "Partial environmental opportunity score: "
            f"{zone.partial_environmental_opportunity_score:.3f}"
        )
        print(f"Risk score: {zone.risk_score:.3f}")
        print(f"Final score: {zone.final_score:.3f}")
        print(f"Confidence: {zone.confidence:.3f}")
        print(f"Classification: {zone.classification}")
        print(f"Missing evidence: {list(zone.missing_evidence)}")
        print(f"Reasons: {list(zone.reasons)}")
        print(f"Evidence: {[asdict(item) for item in zone.evidence]}\n")


if __name__ == "__main__":
    main()
