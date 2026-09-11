"""Unit and integration tests for Phase 5B: Mock Data Integration & Contract Hardening."""

import asyncio
import unittest
from typing import Any, Dict

from backend.agents.graph.workflow import run_marine_agent_async, run_minimal_marine_graph_async
from backend.agents.mocks.fixtures.mangalore_scenario import MANGALORE_REFERENCE, MANGALORE_ZONES, get_scenario_zones
from backend.agents.mocks.tool_registry import ToolRegistry, get_tool_registry
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.planner import planner_node
from backend.agents.nodes.tool_selection import tool_selection_node
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.plan import ExecutionPlan, InputPolicy, PlanStep, StepType, ToolExecutionTarget
from backend.agents.schemas.response import RoleType
from backend.agents.schemas.tools import ToolResult, ToolResultStatus
from backend.agents.state.marine_state import MarineState
from backend.agents.tools.adapters.base import BaseDataAdapter
from backend.agents.tools.data_tools import (
    p4_check_restrictions,
    p4_fetch_hazard_bulletins,
    p4_fetch_ocean_weather,
    p4_get_chlorophyll,
    p4_get_currents,
    p4_get_pfz,
    p4_get_sst,
    p4_get_swell,
    p4_get_tide,
    p4_get_wave,
    p4_get_wind,
    set_weather_adapter,
)
from backend.agents.tools.registry_bridge import (
    register_mock_tools,
    register_p4_tools,
    use_mock_tools,
    use_p4_tools,
)


class TestPhase5BMockHardening(unittest.TestCase):
    """Test suite verifying mock data consistency, multi-zone alignment, and P6 readiness."""

    def setUp(self):
        use_p4_tools()

    def tearDown(self):
        use_mock_tools()

    # =================================================================
    # 1. Multi-Zone Alignment & Cross-Tool Consistency
    # =================================================================

    def test_01_multi_zone_candidate_consistency(self):
        """Verify that Zone A, Zone B, and Zone C are consistent across all P4 tools."""
        params = {
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "requested_time": {"iso_start": "2026-09-12T06:00:00Z", "descriptor": "tomorrow morning"},
        }

        # Retrieve data from all core P4 tools
        pfz_res = asyncio.run(p4_get_pfz(params, {}))
        sst_res = asyncio.run(p4_get_sst(params, {}))
        chl_res = asyncio.run(p4_get_chlorophyll(params, {}))
        wind_res = asyncio.run(p4_get_wind(params, {}))
        wave_res = asyncio.run(p4_get_wave(params, {}))
        restr_res = asyncio.run(p4_check_restrictions(params, {}))

        # Check that all tools returned success and synthetic source
        for r, name in [(pfz_res, "PFZ"), (sst_res, "SST"), (chl_res, "CHL"), (wind_res, "WIND"), (wave_res, "WAVE"), (restr_res, "RESTR")]:
            self.assertEqual(r["status"], "success", f"{name} should succeed")
            self.assertEqual(r["source"], "synthetic", f"{name} source must be synthetic")

        # 1. Check PFZ Zones
        pfz_zones = {z["zone_id"]: z for z in pfz_res["data"]["zones"]}
        self.assertEqual(set(pfz_zones.keys()), {"ZONE_A", "ZONE_B", "ZONE_C"})

        # 2. Check SST Zone Gradients
        sst_zones = sst_res["data"]["zone_gradients"]
        self.assertEqual(set(sst_zones.keys()), {"ZONE_A", "ZONE_B", "ZONE_C"})
        self.assertAlmostEqual(sst_zones["ZONE_A"]["sst_celsius"], 28.4)
        self.assertAlmostEqual(sst_zones["ZONE_B"]["sst_celsius"], 28.7)
        self.assertAlmostEqual(sst_zones["ZONE_C"]["sst_celsius"], 28.2)

        # 3. Check Chlorophyll Zones
        chl_zones = chl_res["data"]["zone_chlorophyll"]
        self.assertEqual(set(chl_zones.keys()), {"ZONE_A", "ZONE_B", "ZONE_C"})
        self.assertAlmostEqual(chl_zones["ZONE_A"]["chla_mg_m3"], 2.8)
        self.assertAlmostEqual(chl_zones["ZONE_B"]["chla_mg_m3"], 2.3)
        self.assertAlmostEqual(chl_zones["ZONE_C"]["chla_mg_m3"], 3.2)

        # 4. Check Wind Zones (Zone A rough 22kts, Zone B calm 11kts, Zone C calm 9.5kts)
        wind_zones = wind_res["data"]["zone_wind"]
        self.assertEqual(set(wind_zones.keys()), {"ZONE_A", "ZONE_B", "ZONE_C"})
        self.assertAlmostEqual(wind_zones["ZONE_A"]["speed_knots"], 22.0)
        self.assertAlmostEqual(wind_zones["ZONE_B"]["speed_knots"], 11.0)
        self.assertAlmostEqual(wind_zones["ZONE_C"]["speed_knots"], 9.5)

        # 5. Check Wave Zones (Zone A rough 2.4m, Zone B calm 1.1m, Zone C calm 1.0m)
        wave_zones = wave_res["data"]["zone_wave"]
        self.assertEqual(set(wave_zones.keys()), {"ZONE_A", "ZONE_B", "ZONE_C"})
        self.assertAlmostEqual(wave_zones["ZONE_A"]["wave_height_m"], 2.4)
        self.assertAlmostEqual(wave_zones["ZONE_B"]["wave_height_m"], 1.1)
        self.assertAlmostEqual(wave_zones["ZONE_C"]["wave_height_m"], 1.0)

        # 6. Check Restrictions (Zone A & B legal, Zone C restricted)
        restr_zones = restr_res["data"]["zone_restrictions"]
        self.assertFalse(restr_zones["ZONE_A"]["restricted"])
        self.assertFalse(restr_zones["ZONE_B"]["restricted"])
        self.assertTrue(restr_zones["ZONE_C"]["restricted"])
        self.assertEqual(restr_zones["ZONE_C"]["status"], "BLOCKED")

    # =================================================================
    # 2. Determinism & Non-Randomness
    # =================================================================

    def test_02_deterministic_reproducibility(self):
        """Repeated invocations with identical parameters produce identical deterministic outputs."""
        params = {"location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}}

        run1 = asyncio.run(p4_get_pfz(params, {}))
        run2 = asyncio.run(p4_get_pfz(params, {}))

        self.assertEqual(run1["data"]["zones"], run2["data"]["zones"])
        self.assertEqual(run1["data"]["confidence"], run2["data"]["confidence"])

    # =================================================================
    # 3. Dynamic Location Adaptation without Hardcoding
    # =================================================================

    def test_03_arbitrary_coordinates_shift_deterministically(self):
        """Coordinates outside Mangalore shift candidate zones deterministically."""
        params = {"location": {"name": "Goa Offshore", "latitude": 15.2993, "longitude": 73.98}}

        pfz_res = asyncio.run(p4_get_pfz(params, {}))
        zones = pfz_res["data"]["zones"]

        self.assertEqual(len(zones), 3)
        # Latitudes should be centered around Goa (~15.3), not Mangalore (12.86)
        for z in zones:
            self.assertAlmostEqual(z["latitude"], 15.3, delta=0.5)
            self.assertAlmostEqual(z["longitude"], 73.98, delta=0.5)

    # =================================================================
    # 4. Input Policy: Missing Optional Data vs Missing Required Data
    # =================================================================

    def test_04_optional_data_missing_allows_workflow_continuation(self):
        """When an optional step (e.g. swell or tide) fails, workflow continues with partial status."""
        plan = ExecutionPlan(
            plan_id="test_optional_plan",
            steps=[
                PlanStep(
                    id="step_weather_req",
                    type=StepType.DATA.value,
                    operation="get_wind",
                    required=True,
                    input_policy=InputPolicy.REQUIRE_ALL.value,
                ),
                PlanStep(
                    id="step_swell_opt",
                    type=StepType.DATA.value,
                    operation="unknown_optional_op",
                    required=False,
                    input_policy=InputPolicy.OPTIONAL.value,
                ),
                PlanStep(
                    id="step_analytics",
                    type=StepType.ANALYTICS.value,
                    operation="calculate_marine_risk",
                    depends_on=["step_weather_req", "step_swell_opt"],
                    input_policy=InputPolicy.ALLOW_PARTIAL.value,
                ),
            ],
        )

        state: MarineState = {
            "execution_plan": plan,
            "execution_steps": plan.steps,
            "tool_results": [],
            "analytics_results": [],
            "errors": [],
        }

        res = asyncio.run(executor_node(state))
        # The analytics step should execute with partial flag
        analytics_steps = [s for s in res["analytics_results"] if s["step_id"] == "step_analytics"]
        self.assertEqual(len(analytics_steps), 1)
        self.assertTrue(analytics_steps[0]["partial"])

    def test_05_required_dependency_failure_blocks_downstream(self):
        """When a required dependency fails under REQUIRE_ALL, downstream step is blocked."""
        plan = ExecutionPlan(
            plan_id="test_require_all_plan",
            steps=[
                PlanStep(
                    id="step_failing_req",
                    type=StepType.DATA.value,
                    operation="non_existent_required_op",
                    required=True,
                    input_policy=InputPolicy.REQUIRE_ALL.value,
                ),
                PlanStep(
                    id="step_downstream",
                    type=StepType.ANALYTICS.value,
                    operation="calculate_opportunity",
                    depends_on=["step_failing_req"],
                    input_policy=InputPolicy.REQUIRE_ALL.value,
                ),
            ],
        )

        state: MarineState = {
            "execution_plan": plan,
            "execution_steps": plan.steps,
            "tool_results": [],
            "analytics_results": [],
            "errors": [],
        }

        res = asyncio.run(executor_node(state))
        downstream_entries = [s for s in res["analytics_results"] if s["step_id"] == "step_downstream"]
        self.assertEqual(len(downstream_entries), 1)
        self.assertEqual(downstream_entries[0]["status"], "blocked")

    # =================================================================
    # 5. P6 Data Readiness Audit
    # =================================================================

    def test_06_p6_input_fields_presence(self):
        """P4 outputs contain all necessary fields for P6 opportunity, risk, and ranking calculations."""
        params = {"location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}}

        pfz = asyncio.run(p4_get_pfz(params, {}))
        sst = asyncio.run(p4_get_sst(params, {}))
        chl = asyncio.run(p4_get_chlorophyll(params, {}))
        wind = asyncio.run(p4_get_wind(params, {}))
        wave = asyncio.run(p4_get_wave(params, {}))
        swell = asyncio.run(p4_get_swell(params, {}))
        tide = asyncio.run(p4_get_tide(params, {}))
        restr = asyncio.run(p4_check_restrictions(params, {}))

        # PFZ fields needed by P6
        for z in pfz["data"]["zones"]:
            self.assertIn("zone_id", z)
            self.assertIn("lat", z)
            self.assertIn("lon", z)
            self.assertIn("bearing", z)
            self.assertIn("distance_nm", z)
            self.assertIn("confidence", z)
            self.assertIn("species", z)

        # SST fields needed by P6
        self.assertIn("mean_sst_celsius", sst["data"])
        self.assertIn("zone_gradients", sst["data"])

        # Chlorophyll fields needed by P6
        self.assertIn("chlorophyll_a_mg_m3", chl["data"])
        self.assertIn("zone_chlorophyll", chl["data"])

        # Wind & Wave fields needed by P6
        self.assertIn("zone_wind", wind["data"])
        self.assertIn("zone_wave", wave["data"])
        self.assertIn("zone_swell", swell["data"])
        self.assertIn("water_level_m", tide["data"])

        # Restrictions fields needed by P6
        self.assertIn("zone_restrictions", restr["data"])

    # =================================================================
    # 6. Complete North Star DAG Execution with P4 Mock Data
    # =================================================================

    def test_07_north_star_complete_workflow_p4_execution(self):
        """
        Execute the complete North Star workflow:
        'I'm near Mangalore. Where should I fish tomorrow morning?'
        Validates the complete chain:
        understand_query -> planner -> tool_selection -> executor -> P4 tools -> evidence -> response.
        """
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"

        # 1. Run minimal graph to inspect state and plan
        min_state: MarineState = asyncio.run(run_minimal_marine_graph_async(query, user_type="fisherman"))
        self.assertEqual(min_state["intent"], MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertEqual(min_state["location"]["name"], "Mangalore")

        exec_plan: ExecutionPlan = min_state["execution_plan"]
        self.assertGreater(len(exec_plan.steps), 0)

        # 2. Run full graph through DAG executor backed by P4 tools
        full_response = asyncio.run(run_marine_agent_async(query, role=RoleType.FISHERMAN))

        self.assertIsNotNone(full_response)
        self.assertEqual(full_response.status, "success")
        self.assertIsNotNone(full_response.markdown_content)
        self.assertIn("Mangalore", full_response.markdown_content)
        self.assertIsNotNone(full_response.visual_payload)
        self.assertIn("SST", full_response.visual_payload.metric_badges)
        self.assertIn("Wave Height", full_response.visual_payload.metric_badges)
        self.assertIn("Wind Speed", full_response.visual_payload.metric_badges)


if __name__ == "__main__":
    unittest.main()
