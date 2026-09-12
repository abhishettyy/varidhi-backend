from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analytics.integration import evaluate_zone
from analytics.tests.fixtures import complete_zone
from data.loaders.grib_environment import GribEnvironmentLoader
from data.loaders.waves import WaveLoader
from data.normalization import group_by_time_and_location


ROOT = Path(__file__).resolve().parents[3]
TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


class IntegrationTests(unittest.TestCase):
    def test_mixed_timestamps_are_rejected(self):
        observations = complete_zone()
        item = observations[-1]
        observations[-1] = type(item)(
            item.variable, item.value, item.unit, item.latitude, item.longitude,
            item.observation_time + timedelta(hours=1), item.valid_time + timedelta(hours=1),
            item.source, item.dataset, item.quality, item.provenance,
        )
        with self.assertRaises(ValueError):
            evaluate_zone("mixed", observations)

    def test_real_p5_to_p6_integration(self):
        grib = GribEnvironmentLoader(ROOT / "data/raw/grib/data.grib")
        waves = WaveLoader(ROOT / "data/raw/waves/waves_mangalore_20230101.nc")
        environment = grib.load(
            start_time=TIME,
            variables=["sea_surface_temperature", "wind_speed", "air_temperature_2m", "dewpoint_temperature_2m", "total_precipitation"],
            latitude_range=(11.5, 11.5), longitude_range=(73.0, 73.0),
        )
        wave_data = waves.load(
            start_time=TIME,
            variables=["significant_wave_height", "peak_wave_period", "mean_wave_direction"],
            latitude_range=(11.5, 11.5), longitude_range=(73.0, 73.0),
        )
        grouped = group_by_time_and_location([*environment, *wave_data])
        result = evaluate_zone("real", next(iter(grouped.values())))
        self.assertEqual(result.timestamp, TIME)
        self.assertGreaterEqual(len(result.evidence), 8)
        self.assertTrue(result.reasons)
