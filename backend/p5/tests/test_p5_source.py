"""P5 data API: selection rules of the mock source and the HTTP round trip."""

import json
import os
import unittest

from fastapi.testclient import TestClient

from backend.p5.api import create_app
from backend.p5.client import HttpP5DataSource
from backend.p5.source import (
    MockP5DataSource, P5Error, P5Query, format_time, get_p5_source, haversine_nm, parse_time, set_p5_source,
)

MANGALORE = (12.8681, 74.8427)


class TestMockP5DataSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = MockP5DataSource()
        cls.ref = cls.src.manifest["reference_time"]

    def test_all_zones_without_location(self):
        resp = self.src.query("sst")
        self.assertEqual(resp.status, "success")
        self.assertEqual(len(resp.records), len(self.src.zones()))

    def test_radius_filter_matches_geometry(self):
        resp = self.src.query("sst", P5Query(latitude=MANGALORE[0], longitude=MANGALORE[1], radius_nm=10))
        expected = {z["zone_id"] for z in self.src.zones()
                    if haversine_nm(*MANGALORE, z["latitude"], z["longitude"]) <= 10}
        self.assertTrue(expected)
        self.assertLess(len(expected), len(self.src.zones()))
        self.assertEqual({r["zone_id"] for r in resp.records}, expected)

    def test_explicit_zone_ids_and_unknown_zone(self):
        resp = self.src.query("wind", P5Query(zone_ids=["ZONE_A", "ZONE_Z"]))
        self.assertEqual([r["zone_id"] for r in resp.records], ["ZONE_A"])
        self.assertEqual(resp.missing, [{"zone_id": "ZONE_Z", "reason": "unknown_zone"}])
        self.assertEqual(resp.status, "partial")

    def test_latest_available_golden_values(self):
        rec = self.src.query("sst", P5Query(zone_ids=["ZONE_A"])).records[0]
        self.assertEqual(rec["data"]["sst_celsius"], 28.4)
        self.assertEqual(rec["data"]["thermal_front_delta_celsius"], 0.9)
        self.assertIsNone(rec["valid_time"])

    def test_latest_available_never_looks_ahead(self):
        at = "2026-09-07T00:00:00Z"
        rec = self.src.query("sst", P5Query(zone_ids=["ZONE_A"], at=at)).records[0]
        self.assertLessEqual(parse_time(rec["observation_time"]), parse_time(at))
        self.assertEqual(rec["observation_time"], "2026-09-06T09:00:00Z")

    def test_standing_restriction_never_ages_out(self):
        """ZONE_C's sanctuary was notified in January; it must still be returned — and BLOCKED."""
        rec = self.src.query("restrictions", P5Query(zone_ids=["ZONE_C"])).records[0]
        self.assertEqual(rec["observation_time"], "2026-01-01T00:00:00Z")
        self.assertEqual(rec["data"]["regulatory_status"], "BLOCKED")
        self.assertEqual(len(self.src.query("restrictions").records), len(self.src.zones()))

    def test_cloud_gap_falls_back_to_last_valid_observation(self):
        with open(self.src.data_dir / "chlorophyll.jsonl", encoding="utf-8") as f:
            recs = [json.loads(line) for line in f]
        # a cloud-covered day that has an earlier valid observation to fall back on
        cloudy = next(r for r in recs if r["quality"] == "missing" and any(
            o["zone_id"] == r["zone_id"] and o["observation_time"] < r["observation_time"]
            and o["data"]["chlorophyll_a_mg_m3"] is not None for o in recs))
        at = format_time(parse_time(cloudy["observation_time"]).replace(hour=12))
        resp = self.src.query("chlorophyll", P5Query(zone_ids=[cloudy["zone_id"]], at=at))
        rec = resp.records[0]
        self.assertIsNotNone(rec["data"]["chlorophyll_a_mg_m3"])
        self.assertLess(rec["observation_time"], cloudy["observation_time"])
        self.assertEqual(resp.metadata["selection"][0]["fallback_from"], cloudy["observation_time"])
        self.assertEqual(resp.status, "partial")

    def test_forecast_picks_nearest_step(self):
        rec = self.src.query("wind", P5Query(zone_ids=["ZONE_A"])).records[0]
        self.assertEqual(rec["valid_time"], self.ref)
        self.assertEqual(rec["data"]["wind_speed_knots"], 22.0)  # golden step 0
        rec = self.src.query("wind", P5Query(zone_ids=["ZONE_A"], at="2026-09-12T02:00:00Z")).records[0]
        self.assertEqual(rec["valid_time"], "2026-09-12T00:00:00Z")
        self.assertIsNone(rec["observation_time"])

    def test_forecast_outside_horizon_is_missing_not_extrapolated(self):
        resp = self.src.query("wave", P5Query(zone_ids=["ZONE_A"], at="2026-09-20T00:00:00Z"))
        self.assertEqual(resp.status, "unavailable")
        self.assertEqual(resp.records, [])
        self.assertEqual(resp.missing, [{"zone_id": "ZONE_A", "reason": "outside_forecast_horizon"}])

    def test_historical_clip_does_not_mutate_dataset(self):
        q = P5Query(zone_ids=["ZONE_E"], variable="sst", start="2026-08-01T00:00:00Z", end="2026-08-31T00:00:00Z")
        rec = self.src.query("historical", q).records[0]
        self.assertEqual(rec["metadata"]["points"], 31)
        self.assertEqual(len(rec["data"]["series"]), 31)
        self.assertTrue(all("2026-08-01" <= p["timestamp"][:10] <= "2026-08-31" for p in rec["data"]["series"]))
        full = self.src.query("historical", P5Query(zone_ids=["ZONE_E"], variable="SST")).records[0]
        self.assertEqual(len(full["data"]["series"]), 90)

    def test_bad_requests_raise(self):
        with self.assertRaises(P5Error):
            self.src.query("tsunami")
        with self.assertRaises(P5Error):
            self.src.query("wind", P5Query(at="tomorrow"))


class TestP5HttpService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = MockP5DataSource()
        cls.remote = HttpP5DataSource(client=TestClient(create_app(cls.local)))

    def test_http_client_matches_in_process_source(self):
        q = P5Query(latitude=MANGALORE[0], longitude=MANGALORE[1], at="2026-09-12T00:00:00Z")
        for rtype in ("pfz", "sst", "chlorophyll", "wind", "wave", "swell", "tide", "currents", "restrictions"):
            self.assertEqual(self.remote.query(rtype, q).to_dict(), self.local.query(rtype, q).to_dict(), rtype)

    def test_catalogue_endpoints(self):
        self.assertEqual(len(self.remote.zones()), 12)
        self.assertEqual(self.remote.describe()["contract_version"], "p5-normalized-v1")

    def test_http_errors_surface_as_p5_errors(self):
        with self.assertRaises(P5Error):
            self.remote.query("tsunami")
        with self.assertRaises(P5Error):
            self.remote.query("wind", P5Query(at="not-a-time"))

    def test_env_var_selects_http_source(self):
        old = os.environ.get("P5_API_URL")
        os.environ["P5_API_URL"] = "http://p5.internal:8105"
        set_p5_source(None)
        try:
            self.assertIsInstance(get_p5_source(), HttpP5DataSource)
        finally:
            if old is None:
                del os.environ["P5_API_URL"]
            else:
                os.environ["P5_API_URL"] = old
            set_p5_source(None)


if __name__ == "__main__":
    unittest.main()
