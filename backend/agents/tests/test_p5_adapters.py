"""P4 tools served from the P5 data API: contract, golden parity, time handling, E2E."""

import asyncio
import unittest

from fastapi.testclient import TestClient

from backend.agents.analytics.opportunity import calculate_opportunity_from_p4_results
from backend.agents.graph.workflow import run_marine_agent_async
from backend.agents.schemas.response import RoleType
from backend.agents.schemas.tools import ToolResult
from backend.agents.tools.adapters.ocean_adapter import SyntheticOceanAdapter
from backend.agents.tools.adapters.pfz_adapter import SyntheticPFZAdapter
from backend.agents.tools.data_tools import (
    p4_check_restrictions, p4_fetch_hazard_bulletins, p4_fetch_ocean_weather, p4_get_chlorophyll,
    p4_get_currents, p4_get_historical_data, p4_get_pfz, p4_get_sst, p4_get_swell, p4_get_tide,
    p4_get_wave, p4_get_wind, use_synthetic_adapters,
)
from backend.agents.tools.registry_bridge import use_mock_tools, use_p5_tools
from backend.p5.api import create_app
from backend.p5.client import HttpP5DataSource
from backend.p5.source import MockP5DataSource

MANGALORE = {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}
REFERENCE = {"iso_start": "2026-09-11T00:00:00Z"}


def run(tool, **params):
    return asyncio.run(tool(parameters=params, dependencies={}))


class TestP4ToolsOverP5(unittest.TestCase):
    def setUp(self):
        use_p5_tools(MockP5DataSource())

    def tearDown(self):
        use_synthetic_adapters()
        use_mock_tools()

    def test_every_tool_returns_a_valid_tool_result(self):
        tools = [("get_pfz", p4_get_pfz), ("get_sst", p4_get_sst), ("get_chlorophyll", p4_get_chlorophyll),
                 ("get_wind", p4_get_wind), ("get_wave", p4_get_wave), ("get_swell", p4_get_swell),
                 ("get_tide", p4_get_tide), ("get_currents", p4_get_currents),
                 ("check_restrictions", p4_check_restrictions), ("fetch_ocean_weather", p4_fetch_ocean_weather),
                 ("fetch_hazard_bulletins", p4_fetch_hazard_bulletins), ("get_historical_data", p4_get_historical_data)]
        for op, tool in tools:
            res = run(tool, location=MANGALORE, requested_time=REFERENCE)
            self.assertEqual(ToolResult(**res).operation, op)
            self.assertIn(res["status"], ("success", "partial"), f"{op}: {res.get('error')}")
            self.assertEqual(res["source"], "synthetic", op)

    def test_golden_fixture_values_reach_p4_unchanged(self):
        wind = run(p4_get_wind, location=MANGALORE, requested_time=REFERENCE)["data"]
        self.assertEqual(wind["zone_wind"]["ZONE_A"]["speed_knots"], 22.0)
        self.assertEqual(wind["zone_data"]["ZONE_A"]["gust_knots"], 28.0)
        wave = run(p4_get_wave, location=MANGALORE, requested_time=REFERENCE)["data"]
        self.assertEqual(wave["zone_wave"]["ZONE_A"]["wave_height_m"], 2.4)
        sst = run(p4_get_sst, location=MANGALORE, requested_time=REFERENCE)["data"]
        self.assertEqual(sst["zone_gradients"]["ZONE_A"]["sst_celsius"], 28.4)
        self.assertEqual(sst["zone_gradients"]["ZONE_A"]["gradient"], 0.9)
        rest = run(p4_check_restrictions, location=MANGALORE)["data"]
        self.assertTrue(rest["zone_restrictions"]["ZONE_C"]["restricted"])
        self.assertEqual(rest["zone_restrictions"]["ZONE_C"]["status"], "BLOCKED")

    def test_opportunity_scores_identical_to_synthetic_fixture(self):
        """P6 must not notice the switch: same inputs for ZONE_A/B/C -> same scores."""
        via_p5 = calculate_opportunity_from_p4_results(
            pfz_result=run(p4_get_pfz, location=MANGALORE),
            sst_result=run(p4_get_sst, location=MANGALORE),
            chlorophyll_result=run(p4_get_chlorophyll, location=MANGALORE))
        via_fixture = calculate_opportunity_from_p4_results(
            pfz_result=SyntheticPFZAdapter().fetch_pfz(MANGALORE),
            sst_result=SyntheticOceanAdapter().fetch_sst(MANGALORE),
            chlorophyll_result=SyntheticOceanAdapter().fetch_chlorophyll(MANGALORE))
        p5_scores = {z.zone_id: z.opportunity_score for z in via_p5.zones}
        for z in via_fixture.zones:
            self.assertEqual(p5_scores[z.zone_id], z.opportunity_score, z.zone_id)
        self.assertGreater(len(p5_scores), 3)  # plus the extra P5 zones

    def test_time_semantics_and_relative_planner_times(self):
        sst = run(p4_get_sst, location=MANGALORE)
        self.assertIsNotNone(sst["observation_time"])
        self.assertIsNone(sst["valid_time"])
        # planner output for "tomorrow morning": 06:00 IST on 12 Sep = 00:30Z -> nearest 6-hourly step 00:00Z
        wind = run(p4_get_wind, location=MANGALORE, requested_time={"relative_day": "tomorrow", "period": "morning"})
        self.assertEqual(wind["valid_time"], "2026-09-12T00:00:00Z")
        self.assertIsNone(wind["observation_time"])

    def test_outside_forecast_horizon_reports_missing_instead_of_inventing(self):
        res = run(p4_get_wave, location=MANGALORE, requested_time={"iso_start": "2026-09-20T00:00:00Z"})
        self.assertEqual(res["status"], "unavailable")
        self.assertIsNone(res["data"]["significant_wave_height_m"])
        self.assertEqual(res["data"]["zone_wave"], {})
        self.assertTrue(res["missing_dependencies"])
        self.assertIn("outside_forecast_horizon", res["error"])

    def test_location_far_from_dataset_is_unavailable(self):
        res = run(p4_get_pfz, location={"name": "Karwar", "latitude": 14.81, "longitude": 74.13})
        self.assertEqual(res["status"], "unavailable")
        self.assertEqual(res["data"]["region"], "Karwar")
        self.assertEqual(res["data"]["zones"], [])

    def test_historical_series_for_planner_window(self):
        res = run(p4_get_historical_data, variable="SST", zone_id="ZONE_E",
                  requested_time={"relative_day": "last 30 days", "is_historical": True})
        data = res["data"]
        self.assertEqual(data["zone_id"], "ZONE_E")
        self.assertEqual(len(data["series"]), 30)
        self.assertEqual(len(data["time_series"]), 30)
        self.assertNotIn("trend", data)

    def test_north_star_flow_runs_on_p5_data(self):
        response = asyncio.run(run_marine_agent_async(
            "I'm near Mangalore. Where should I fish tomorrow morning?", role=RoleType.FISHERMAN))
        self.assertEqual(response.status, "success")
        self.assertIn("Mangalore", response.markdown_content)
        self.assertTrue(response.evidence_summary)

    def test_same_results_over_http_transport(self):
        in_process = run(p4_get_wind, location=MANGALORE, requested_time=REFERENCE)
        use_p5_tools(HttpP5DataSource(client=TestClient(create_app(MockP5DataSource()))))
        over_http = run(p4_get_wind, location=MANGALORE, requested_time=REFERENCE)
        self.assertEqual(over_http["data"], in_process["data"])
        self.assertEqual(over_http["valid_time"], in_process["valid_time"])


if __name__ == "__main__":
    unittest.main()
