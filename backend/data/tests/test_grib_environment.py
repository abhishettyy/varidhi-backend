from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone
from pathlib import Path

from data.loaders.grib_environment import GribEnvironmentLoader


ROOT = Path(__file__).resolve().parents[3]
GRIB = ROOT / "data" / "raw" / "grib" / "data.grib"
TIME = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)


class GribEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = GribEnvironmentLoader(GRIB)

    def load(self, variables):
        return self.loader.load(
            start_time=TIME,
            variables=variables,
            latitude_range=(12.5, 12.5),
            longitude_range=(74.75, 74.75),
        )

    def test_sst_extraction_kelvin_conversion_and_provenance(self):
        values = self.load(["sea_surface_temperature"])
        self.assertEqual(len(values), 1)
        value = values[0]
        self.assertEqual(value.unit, "degC")
        self.assertEqual(value.provenance.raw_variable, "sst")
        self.assertEqual(value.provenance.original_unit, "K")
        self.assertGreater(value.value, 0)
        self.assertLess(value.value, 40)

    def test_missing_sst_is_not_materialized(self):
        values = self.loader.load(
            start_time=TIME,
            variables=["sea_surface_temperature"],
            latitude_range=(11.5, 14.5),
            longitude_range=(73, 76),
        )
        self.assertEqual(len(values), 102)

    def test_environment_variables_and_derived_wind_speed(self):
        values = self.load(
            [
                "wind_u",
                "wind_v",
                "wind_speed",
                "air_temperature_2m",
                "dewpoint_temperature_2m",
                "total_precipitation",
            ]
        )
        by_variable = {item.variable: item for item in values}
        self.assertEqual(
            set(by_variable),
            {
                "wind_u",
                "wind_v",
                "wind_speed",
                "air_temperature_2m",
                "dewpoint_temperature_2m",
                "total_precipitation",
            },
        )
        self.assertAlmostEqual(
            by_variable["wind_speed"].value,
            math.hypot(by_variable["wind_u"].value, by_variable["wind_v"].value),
        )
        self.assertEqual(by_variable["air_temperature_2m"].unit, "degC")
        self.assertEqual(by_variable["dewpoint_temperature_2m"].unit, "degC")
        precipitation = by_variable["total_precipitation"]
        self.assertEqual(precipitation.unit, "m")
        self.assertTrue(precipitation.provenance.details["accumulated"])
        self.assertEqual(precipitation.valid_time, TIME)
        self.assertEqual(precipitation.latitude, 12.5)
        self.assertEqual(precipitation.longitude, 74.75)
