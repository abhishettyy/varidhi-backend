"""Comprehensive unit tests for Phase 4 DAG-driven Executor and Mock Tool Registry."""

import asyncio
import unittest

from backend.agents.mocks.tool_registry import get_tool_registry, reset_tool_registry
from backend.agents.nodes.executor import executor_node
from backend.agents.schemas.plan import (
    ExecutionPlan,
    InputPolicy,
    PlanStep,
    StepType,
    ToolExecutionTarget,
)
from backend.agents.state.marine_state import MarineState


class TestPhase4ExecutorDAG(unittest.TestCase):
    """Test suite validating generic DAG scheduling, dependency data passing, InputPolicy, and North Star demo."""

    def setUp(self):
        reset_tool_registry()

    # 1. Basic execution: single DATA step -> success
    def test_01_single_data_step(self):
        step = PlanStep(
            id="step_wind_1",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            parameters={"location": {"name": "Mangalore"}},
        )
        state: MarineState = {"execution_steps": [step], "errors": [], "tool_results": [], "analytics_results": []}

        res = asyncio.run(executor_node(state))
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["tool_results"]), 1)
        step_res = res["tool_results"][0]["result"]
        self.assertEqual(step_res["status"], "success")
        self.assertEqual(step_res["source"], "mock")
        self.assertEqual(step_res["operation"], "get_wind")
        self.assertIn("wind_speed_knots", step_res["data"])

    # 2. Multiple independent steps execute
    def test_02_multiple_independent_steps(self):
        step_a = PlanStep(id="step_a", type=StepType.DATA.value, operation="get_sst", depends_on=[])
        step_b = PlanStep(id="step_b", type=StepType.DATA.value, operation="get_chlorophyll", depends_on=[])
        step_c = PlanStep(id="step_c", type=StepType.DATA.value, operation="get_wind", depends_on=[])

        state: MarineState = {"execution_steps": [step_a, step_b, step_c], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["tool_results"]), 3)
        completed_ids = {r["step_id"] for r in res["tool_results"]}
        self.assertEqual(completed_ids, {"step_a", "step_b", "step_c"})

    # 3. Dependency order: A -> B -> C
    def test_03_dependency_chain_order(self):
        execution_order = []

        registry = get_tool_registry()

        def custom_a(parameters, dependencies):
            execution_order.append("A")
            return {"val": "A_done"}

        def custom_b(parameters, dependencies):
            execution_order.append("B")
            self.assertIn("step_a", dependencies)
            return {"val": "B_done"}

        def custom_c(parameters, dependencies):
            execution_order.append("C")
            self.assertIn("step_b", dependencies)
            return {"val": "C_done"}

        registry.register("op_a", custom_a)
        registry.register("op_b", custom_b)
        registry.register("op_c", custom_c)

        step_a = PlanStep(id="step_a", type=StepType.DATA.value, operation="op_a", depends_on=[])
        step_b = PlanStep(id="step_b", type=StepType.ANALYTICS.value, operation="op_b", depends_on=["step_a"])
        step_c = PlanStep(id="step_c", type=StepType.DECISION.value, operation="op_c", depends_on=["step_b"])

        state: MarineState = {"execution_steps": [step_a, step_b, step_c], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(execution_order, ["A", "B", "C"])

    # 4. Fan-in: A, B -> C receives both outputs explicitly
    def test_04_fan_in_dependency_passing(self):
        registry = get_tool_registry()
        received_dependencies = {}

        def custom_c(parameters, dependencies):
            nonlocal received_dependencies
            received_dependencies = dependencies
            return {"combined": True}

        registry.register("op_fanin_c", custom_c)

        step_a = PlanStep(id="temp_feed", type=StepType.DATA.value, operation="get_sst", depends_on=[])
        step_b = PlanStep(id="chla_feed", type=StepType.DATA.value, operation="get_chlorophyll", depends_on=[])
        step_c = PlanStep(id="fusion_calc", type=StepType.ANALYTICS.value, operation="op_fanin_c", depends_on=["temp_feed", "chla_feed"])

        state: MarineState = {"execution_steps": [step_a, step_b, step_c], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertEqual(len(res["errors"]), 0)
        self.assertIn("temp_feed", received_dependencies)
        self.assertIn("chla_feed", received_dependencies)
        self.assertEqual(received_dependencies["temp_feed"]["operation"], "get_sst")
        self.assertEqual(received_dependencies["chla_feed"]["operation"], "get_chlorophyll")

    # 5. Arbitrary IDs: no hardcoded step ID assumptions
    def test_05_arbitrary_step_ids(self):
        step_1 = PlanStep(id="marine_17", type=StepType.DATA.value, operation="get_wind", depends_on=[])
        step_2 = PlanStep(id="abc_weather", type=StepType.DATA.value, operation="get_wave", depends_on=[])
        step_3 = PlanStep(
            id="risk_calculation_xyz",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            depends_on=["marine_17", "abc_weather"],
        )

        state: MarineState = {"execution_steps": [step_1, step_2, step_3], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertEqual(len(res["errors"]), 0)
        analytics = res["analytics_results"]
        self.assertEqual(len(analytics), 1)
        self.assertEqual(analytics[0]["step_id"], "risk_calculation_xyz")
        self.assertEqual(analytics[0]["result"]["status"], "success")

    # 6. REQUIRE_ALL: Dependency failure blocks downstream step
    def test_06_require_all_blocking_behavior(self):
        registry = get_tool_registry()

        def failing_feed(parameters, dependencies):
            return {"status": "failed", "source": "mock", "error": "Hardware sensor offline"}

        registry.register("op_failing", failing_feed)

        step_bad = PlanStep(id="sensor_a", type=StepType.DATA.value, operation="op_failing", depends_on=[])
        step_downstream = PlanStep(
            id="vital_decision",
            type=StepType.DECISION.value,
            operation="select_safe_fishing_zone",
            depends_on=["sensor_a"],
            input_policy=InputPolicy.REQUIRE_ALL.value,
        )

        state: MarineState = {"execution_steps": [step_bad, step_downstream], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertGreater(len(res["errors"]), 0)
        downstream_result = [r for r in res["analytics_results"] if r["step_id"] == "vital_decision"][0]
        self.assertEqual(downstream_result["status"], "blocked")
        self.assertIn("Required dependency failed/missing", downstream_result["result"]["error"])

    # 7. ALLOW_PARTIAL: Dependency failure does not block downstream step
    def test_07_allow_partial_execution_behavior(self):
        registry = get_tool_registry()

        def failing_optional_sensor(parameters, dependencies):
            return {"status": "failed", "source": "mock", "error": "Cloud cover obscured satellite"}

        registry.register("op_cloudy_sst", failing_optional_sensor)

        step_pfz = PlanStep(id="pfz_data", type=StepType.DATA.value, operation="get_pfz", depends_on=[])
        step_sst = PlanStep(id="sst_data", type=StepType.DATA.value, operation="op_cloudy_sst", depends_on=[])
        step_opp = PlanStep(
            id="opp_calc",
            type=StepType.ANALYTICS.value,
            operation="calculate_opportunity",
            depends_on=["pfz_data", "sst_data"],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
        )

        state: MarineState = {"execution_steps": [step_pfz, step_sst, step_opp], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        opp_result = [r for r in res["analytics_results"] if r["step_id"] == "opp_calc"][0]
        self.assertEqual(opp_result["status"], "success")
        self.assertTrue(opp_result["partial"])
        self.assertIn("sst_data", opp_result["result"]["missing_dependencies"])

    # 8. OPTIONAL: Optional dependency failure does not block step
    def test_08_optional_input_policy_behavior(self):
        registry = get_tool_registry()

        def failing_feed(parameters, dependencies):
            return {"status": "failed", "source": "mock", "error": "Optional auxiliary buoy disconnected"}

        registry.register("op_aux_buoy", failing_feed)

        step_aux = PlanStep(id="aux_tide", type=StepType.DATA.value, operation="op_aux_buoy", depends_on=[])
        step_nav = PlanStep(
            id="nav_summary",
            type=StepType.RESPONSE.value,
            operation="summarize_conditions",
            depends_on=["aux_tide"],
            input_policy=InputPolicy.OPTIONAL.value,
        )

        state: MarineState = {"execution_steps": [step_aux, step_nav], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        nav_res = [r for r in res["analytics_results"] if r["step_id"] == "nav_summary"][0]
        self.assertEqual(nav_res["status"], "success")
        self.assertTrue(nav_res["partial"])

    # 9. Unknown operation handling: returns structured failure without crashing
    def test_09_unknown_operation_handling(self):
        step_unknown = PlanStep(
            id="alien_step",
            type=StepType.DATA.value,
            operation="non_existent_marine_tool_xyz",
            depends_on=[],
        )
        state: MarineState = {"execution_steps": [step_unknown], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertGreater(len(res["errors"]), 0)
        self.assertIn("Unknown operation 'non_existent_marine_tool_xyz'", res["errors"][0])
        self.assertEqual(res["tool_results"][0]["status"], "failed")

    # 10. Cycle detection: returns structured error and avoids infinite loop
    def test_10_dependency_cycle_detection(self):
        step_a = PlanStep(id="cycle_a", type=StepType.DATA.value, operation="get_wind", depends_on=["cycle_c"])
        step_b = PlanStep(id="cycle_b", type=StepType.DATA.value, operation="get_wave", depends_on=["cycle_a"])
        step_c = PlanStep(id="cycle_c", type=StepType.DATA.value, operation="get_sst", depends_on=["cycle_b"])

        state: MarineState = {"execution_steps": [step_a, step_b, step_c], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        self.assertGreater(len(res["errors"]), 0)
        self.assertIn("Dependency cycle detected", res["errors"][0])

    # 11. Parameter propagation: step parameters reach the mock tool handler
    def test_11_parameter_propagation(self):
        registry = get_tool_registry()
        received_params = {}

        def custom_loc_handler(parameters, dependencies):
            nonlocal received_params
            received_params = parameters
            return {"received": True}

        registry.register("op_param_test", custom_loc_handler)

        step = PlanStep(
            id="param_step",
            type=StepType.DATA.value,
            operation="op_param_test",
            parameters={"harbor": "Old Mangalore Port", "max_depth_m": 50, "vessel_type": "mechanized_trawler"},
            depends_on=[],
        )
        state: MarineState = {"execution_steps": [step], "errors": [], "tool_results": [], "analytics_results": []}
        asyncio.run(executor_node(state))

        self.assertEqual(received_params.get("harbor"), "Old Mangalore Port")
        self.assertEqual(received_params.get("max_depth_m"), 50)
        self.assertEqual(received_params.get("vessel_type"), "mechanized_trawler")

    # 12. Mock provenance verification: output has source = 'mock'
    def test_12_mock_provenance(self):
        step = PlanStep(id="provenance_check", type=StepType.DATA.value, operation="get_sst", depends_on=[])
        state: MarineState = {"execution_steps": [step], "errors": [], "tool_results": [], "analytics_results": []}
        res = asyncio.run(executor_node(state))

        step_res = res["tool_results"][0]["result"]
        self.assertEqual(step_res["source"], "mock")
        self.assertNotEqual(step_res["source"], "NOAA")
        self.assertNotEqual(step_res["source"], "INCOIS")

    # 13. North Star Fishing DAG execution end-to-end
    def test_13_north_star_fishing_dag_execution(self):
        """
        North Star scenario:
        'I'm near Mangalore. Where should I fish tomorrow morning?'

        DAG:
        DATA: pfz, sst, chlorophyll, wind, wave, swell, tide, restrictions
        ANALYTICS: opportunity(pfz, sst, chlorophyll), risk(wind, wave, swell, tide), ranking(opportunity, risk)
        DECISION: decision(ranking, restrictions) -> selects ZONE_B over ZONE_C (Restricted MPA) and ZONE_A (Rough Sea)
        RESPONSE: response(decision) -> final advisory
        """
        steps = [
            PlanStep(id="pfz", type=StepType.DATA.value, operation="get_pfz", depends_on=[]),
            PlanStep(id="sst", type=StepType.DATA.value, operation="get_sst", depends_on=[]),
            PlanStep(id="chlorophyll", type=StepType.DATA.value, operation="get_chlorophyll", depends_on=[]),
            PlanStep(id="wind", type=StepType.DATA.value, operation="get_wind", depends_on=[]),
            PlanStep(id="wave", type=StepType.DATA.value, operation="get_wave", depends_on=[]),
            PlanStep(id="swell", type=StepType.DATA.value, operation="get_swell", depends_on=[]),
            PlanStep(id="tide", type=StepType.DATA.value, operation="get_tide", depends_on=[]),
            PlanStep(id="restrictions", type=StepType.DATA.value, operation="check_restrictions", depends_on=[]),
            PlanStep(id="opportunity", type=StepType.ANALYTICS.value, operation="calculate_opportunity", depends_on=["pfz", "sst", "chlorophyll"]),
            PlanStep(id="risk", type=StepType.ANALYTICS.value, operation="calculate_marine_risk", depends_on=["wind", "wave", "swell", "tide"]),
            PlanStep(id="ranking", type=StepType.ANALYTICS.value, operation="rank_zones", depends_on=["opportunity", "risk"]),
            PlanStep(id="decision", type=StepType.DECISION.value, operation="select_safe_fishing_zone", depends_on=["ranking", "restrictions"]),
            PlanStep(id="response", type=StepType.RESPONSE.value, operation="generate_recommendation", depends_on=["decision"]),
        ]

        state: MarineState = {
            "execution_steps": steps,
            "errors": [],
            "tool_results": [],
            "analytics_results": [],
        }

        res = asyncio.run(executor_node(state))
        self.assertEqual(len(res["errors"]), 0)

        # Total 8 data steps in tool_results, 5 analytics/decision/response steps in analytics_results
        self.assertEqual(len(res["tool_results"]), 8)
        self.assertEqual(len(res["analytics_results"]), 5)

        # Inspect decision step outcome
        decision_entry = [r for r in res["analytics_results"] if r["step_id"] == "decision"][0]
        decision_data = decision_entry["result"]["data"]

        selected = decision_data["selected_zone"]
        self.assertEqual(selected["zone_id"], "ZONE_B", "Must select safe legal ZONE_B over ZONE_C (restricted) and ZONE_A (rough sea)")
        self.assertTrue(selected["is_legal"])
        self.assertTrue(selected["is_safe"])
        self.assertTrue(decision_data["safety_override_applied"])

        # Inspect final recommendation step outcome
        response_entry = [r for r in res["analytics_results"] if r["step_id"] == "response"][0]
        rec_data = response_entry["result"]["data"]
        self.assertIn("ZONE_B", rec_data["headline"])


if __name__ == "__main__":
    unittest.main()
