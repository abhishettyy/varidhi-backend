"""Comprehensive unit and integration tests for Phase 5A / P4 tool integrations."""

import asyncio
import unittest
from typing import Any, Dict

from backend.agents.graph.workflow import run_marine_agent_async, run_minimal_marine_graph_async
from backend.agents.mocks.tool_registry import ToolRegistry, get_tool_registry
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.planner import planner_node
from backend.agents.nodes.tool_selection import tool_selection_node
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.plan import ExecutionPlan, PlanStep, StepType, ToolExecutionTarget
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


class TestP4ToolContractsAndIntegration(unittest.TestCase):
    """Test suite validating P4 tool contracts, provenance, isolation, and registry integration."""

    def setUp(self):
        """Ensure clean state before each test."""
        # Use P4 tools by default for P4 tests
        use_p4_tools()

    def tearDown(self):
        """Restore default mock tools after tests."""
        use_mock_tools()

    # =================================================================
    # 1. Tool Contract & Schema Tests
    # =================================================================

    def test_01_p4_tools_canonical_envelope(self):
        """Each P4 tool must return the canonical dictionary structure matching ToolResult."""
        params = {
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "requested_time": {"iso_start": "2026-09-12T06:00:00Z", "descriptor": "tomorrow morning"},
        }
        tools = [
            ("get_pfz", p4_get_pfz),
            ("get_sst", p4_get_sst),
            ("get_chlorophyll", p4_get_chlorophyll),
            ("get_wind", p4_get_wind),
            ("get_wave", p4_get_wave),
            ("get_swell", p4_get_swell),
            ("get_tide", p4_get_tide),
            ("get_currents", p4_get_currents),
            ("check_restrictions", p4_check_restrictions),
            ("fetch_ocean_weather", p4_fetch_ocean_weather),
            ("fetch_hazard_bulletins", p4_fetch_hazard_bulletins),
        ]

        for op_name, tool_func in tools:
            res = asyncio.run(tool_func(parameters=params, dependencies={}))
            self.assertIsInstance(res, dict, f"Tool {op_name} must return a dict")
            self.assertIn("status", res, f"{op_name} missing status")
            self.assertIn("source", res, f"{op_name} missing source")
            self.assertIn("operation", res, f"{op_name} missing operation")
            self.assertIn("data", res, f"{op_name} missing data payload")
            self.assertIn("observation_time", res, f"{op_name} missing observation_time key")
            self.assertIn("valid_time", res, f"{op_name} missing valid_time key")

            # Validate against Pydantic ToolResult schema
            validated = ToolResult(**res)
            self.assertEqual(validated.operation, op_name)

    # =================================================================
    # 2. Source Labeling (Synthetic vs Official)
    # =================================================================

    def test_02_synthetic_data_explicitly_labeled(self):
        """Synthetic adapters must be honestly labeled with source='synthetic'."""
        params = {"location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}}

        res_pfz = asyncio.run(p4_get_pfz(parameters=params, dependencies={}))
        self.assertEqual(res_pfz["source"], "synthetic")

        res_sst = asyncio.run(p4_get_sst(parameters=params, dependencies={}))
        self.assertEqual(res_sst["source"], "synthetic")

        res_wind = asyncio.run(p4_get_wind(parameters=params, dependencies={}))
        self.assertEqual(res_wind["source"], "synthetic")

    # =================================================================
    # 3. Observation vs Forecast Time Semantics
    # =================================================================

    def test_03_time_semantics_observation_vs_forecast(self):
        """
        SST, Chlorophyll, and PFZ represent latest available satellite observations (observation_time != None, valid_time = None).
        Wind, Wave, Swell, Tide represent forecasts (valid_time != None).
        """
        params = {
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "requested_time": {"iso_start": "2026-09-12T06:00:00Z"},
            "temporal_mode": "latest_available",
        }

        # Observation tools
        res_sst = asyncio.run(p4_get_sst(parameters=params, dependencies={}))
        self.assertIsNotNone(res_sst["observation_time"])
        self.assertIsNone(res_sst["valid_time"])

        res_chla = asyncio.run(p4_get_chlorophyll(parameters=params, dependencies={}))
        self.assertIsNotNone(res_chla["observation_time"])
        self.assertIsNone(res_chla["valid_time"])

        res_pfz = asyncio.run(p4_get_pfz(parameters=params, dependencies={}))
        self.assertIsNotNone(res_pfz["observation_time"])
        self.assertIsNone(res_pfz["valid_time"])

        # Forecast tools
        params["temporal_mode"] = "forecast"
        res_wind = asyncio.run(p4_get_wind(parameters=params, dependencies={}))
        self.assertIsNotNone(res_wind["valid_time"])

        res_wave = asyncio.run(p4_get_wave(parameters=params, dependencies={}))
        self.assertIsNotNone(res_wave["valid_time"])

        res_swell = asyncio.run(p4_get_swell(parameters=params, dependencies={}))
        self.assertIsNotNone(res_swell["valid_time"])

        res_tide = asyncio.run(p4_get_tide(parameters=params, dependencies={}))
        self.assertIsNotNone(res_tide["valid_time"])

    # =================================================================
    # 4. Parameter Propagation
    # =================================================================

    def test_04_location_parameter_propagation(self):
        """Location parameters from plan reach the P4 tool and adapt data accordingly."""
        custom_loc = {"name": "Karwar", "latitude": 14.81, "longitude": 74.13}
        params = {"location": custom_loc}

        res_pfz = asyncio.run(p4_get_pfz(parameters=params, dependencies={}))
        self.assertEqual(res_pfz["data"]["region"], "Karwar")
        self.assertAlmostEqual(res_pfz["data"]["latitude"], 14.81, places=2)
        self.assertAlmostEqual(res_pfz["data"]["longitude"], 74.13, places=2)

        res_wind = asyncio.run(p4_get_wind(parameters=params, dependencies={}))
        self.assertEqual(res_wind["data"]["location"], "Karwar")

    # =================================================================
    # 5. No Scientific / Decision Leakage in P4
    # =================================================================

    def test_05_no_scientific_or_safety_decisions_in_p4(self):
        """
        P4 tools provide pure observation/forecast data.
        get_wave must not return safety judgments ('safe'/'unsafe').
        check_restrictions must identify restrictions without prescribing fishing spots.
        get_chlorophyll must not decide fish presence.
        """
        params = {"location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}}

        res_wave = asyncio.run(p4_get_wave(parameters=params, dependencies={}))
        self.assertIn("significant_wave_height_m", res_wave["data"])
        self.assertNotIn("safe", res_wave["data"])
        self.assertNotIn("decision", res_wave["data"])

        res_restr = asyncio.run(p4_check_restrictions(parameters=params, dependencies={}))
        self.assertIn("restricted", res_restr["data"])
        self.assertNotIn("recommended_spot", res_restr["data"])

        res_chla = asyncio.run(p4_get_chlorophyll(parameters=params, dependencies={}))
        self.assertNotIn("fish_detected", res_chla["data"])

    # =================================================================
    # 6. Graceful Failure Handling
    # =================================================================

    def test_06_graceful_failure_handling_on_adapter_error(self):
        """When an adapter encounters an error, P4 returns a structured error without crashing."""
        class FailingAdapter(BaseDataAdapter):
            @property
            def source_name(self) -> str:
                return "failing_provider"
            @property
            def is_synthetic(self) -> bool:
                return False
            def fetch_wind(self, *args, **kwargs):
                raise ConnectionError("Upstream marine API connection refused")

        set_weather_adapter(FailingAdapter())
        try:
            res = asyncio.run(p4_get_wind(parameters={}, dependencies={}))
            self.assertEqual(res["status"], "error")
            self.assertEqual(res["source"], "failing_provider")
            self.assertIn("Upstream marine API connection refused", res["error"])
            self.assertEqual(res["data"], {})
        finally:
            from backend.agents.tools.adapters.weather_adapter import SyntheticMarineWeatherAdapter
            set_weather_adapter(SyntheticMarineWeatherAdapter())

    # =================================================================
    # 7. Registry Interoperability (Mock <-> P4 Swapping)
    # =================================================================

    def test_07_registry_swapping_without_executor_modification(self):
        """Registry can seamlessly swap between mock tools and P4 tools without changing executor."""
        custom_registry = ToolRegistry()

        # Step 1: Default mock tools
        res_mock = asyncio.run(custom_registry.execute("get_sst", parameters={}))
        self.assertEqual(res_mock["source"], "mock")

        # Step 2: Swap to P4 tools
        register_p4_tools(custom_registry)
        res_p4 = asyncio.run(custom_registry.execute("get_sst", parameters={}))
        self.assertEqual(res_p4["source"], "synthetic")
        self.assertEqual(res_p4["operation"], "get_sst")
        self.assertIn("gradient_celsius_per_km", res_p4["data"])

        # Step 3: Swap back to mock tools
        register_mock_tools(custom_registry)
        res_restored = asyncio.run(custom_registry.execute("get_sst", parameters={}))
        self.assertEqual(res_restored["source"], "mock")

    # =================================================================
    # 8. End-to-End North Star Flow with P4 Tools
    # =================================================================

    def test_08_north_star_mangalore_e2e_with_p4_tools(self):
        """
        Execute complete North Star workflow:
        'I'm near Mangalore. Where should I fish tomorrow morning?'
        with P4 tools registered in the active registry.
        """
        use_p4_tools()

        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        response = asyncio.run(run_marine_agent_async(query, role=RoleType.FISHERMAN))

        self.assertIsNotNone(response)
        self.assertEqual(response.status, "success")
        self.assertIsNotNone(response.markdown_content)
        self.assertIn("Mangalore", response.markdown_content)
        self.assertIsNotNone(response.safety_alert)
        self.assertIsNotNone(response.visual_payload)
        self.assertIn("SST", response.visual_payload.metric_badges)

        # Verify that tool outputs were assembled into evidence
        evidence_items = response.evidence_summary
        self.assertTrue(len(evidence_items) > 0)

    # =================================================================
    # 9. Individual Additional P4 Tools (Swell, Tide, Currents)
    # =================================================================

    def test_09_additional_tools_swell_tide_currents(self):
        """Validate get_swell, get_tide, get_currents contracts."""
        params = {"location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}}

        res_swell = asyncio.run(p4_get_swell(parameters=params, dependencies={}))
        self.assertEqual(res_swell["operation"], "get_swell")
        self.assertIn("swell_height_m", res_swell["data"])
        self.assertIn("swell_period_sec", res_swell["data"])

        res_tide = asyncio.run(p4_get_tide(parameters=params, dependencies={}))
        self.assertEqual(res_tide["operation"], "get_tide")
        self.assertIn("tide_phase", res_tide["data"])
        self.assertIn("water_level_m", res_tide["data"])

        res_currents = asyncio.run(p4_get_currents(parameters=params, dependencies={}))
        self.assertEqual(res_currents["operation"], "get_currents")
        self.assertIn("current_speed_knots", res_currents["data"])


if __name__ == "__main__":
    unittest.main()
