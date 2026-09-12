from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from data.loaders.waves import WaveLoader


ROOT = Path(__file__).resolve().parents[3]
WAVES = ROOT / "data" / "raw" / "waves" / "waves_mangalore_20230101.nc"
TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


class WaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = WaveLoader(WAVES)

    def test_timestamps_and_coordinates(self):
        self.assertEqual(len(self.loader.available_times), 8)
        self.assertEqual(self.loader.available_times[0].hour, 0)
        self.assertEqual(self.loader.available_times[-1].hour, 21)
        self.assertEqual((self.loader.latitudes[0], self.loader.latitudes[-1]), (11.5, 14.5))
        self.assertEqual((self.loader.longitudes[0], self.loader.longitudes[-1]), (73.0, 76.0))

    def test_required_wave_mappings_and_provenance(self):
        values = self.loader.load(
            start_time=TIME,
            variables=["significant_wave_height", "peak_wave_period", "mean_wave_direction"],
            latitude_range=(12.5, 12.5),
            longitude_range=(74.75, 74.75),
        )
        by_variable = {item.variable: item for item in values}
        self.assertEqual(
            set(by_variable),
            {"significant_wave_height", "peak_wave_period", "mean_wave_direction"},
        )
        self.assertEqual(by_variable["significant_wave_height"].provenance.raw_variable, "VHM0")
        self.assertEqual(by_variable["peak_wave_period"].provenance.raw_variable, "VTPK")
        self.assertEqual(by_variable["mean_wave_direction"].provenance.raw_variable, "VMDR")
        self.assertTrue(all(item.valid_time == TIME for item in values))
