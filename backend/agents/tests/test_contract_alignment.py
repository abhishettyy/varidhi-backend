"""Comprehensive unit tests for Phase 3.5 ExecutionPlan Contract Alignment."""

import asyncio
import unittest

from backend.agents.graph.workflow import run_marine_agent_async, run_minimal_marine_graph_async
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.planner import planner_node
from backend.agents.nodes.tool_selection import tool_selection_node
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.plan import (
    ExecutionPlan,
    InputPolicy,
    PlanStep,
    StepType,
    ToolExecutionTarget,
)
from backend.agents.schemas.response import RoleType
from backend.agents.state.marine_state import MarineState


class TestPhase35ContractAlignment(unittest.TestCase):
    """Test suite validating ExecutionPlan as the single source of truth across all agent nodes."""

    # 1. Full graph uses ExecutionPlan instead of legacy plan
    def test_01_full_graph_uses_execution_plan(self):
        query = "Where should I fish tomorrow morning near Mangalore?"
        state: MarineState = asyncio.run(run_minimal_marine_graph_async(query, user_type="fisherman"))

        self.assertIn("execution_plan", state)
        exec_plan: ExecutionPlan = state["execution_plan"]
        self.assertIsInstance(exec_plan, ExecutionPlan)
        self.assertEqual(exec_plan.intent, MarineIntent.FISHING_RECOMMENDATION.value)

        # Ensure tool selection picks up execution_plan directly
        ts_res = asyncio.run(tool_selection_node(state))
        exec_steps = ts_res["execution_steps"]

        # IDs match execution_plan steps exactly
        expected_ids = [s.id for s in exec_plan.steps]
        actual_ids = [s.id for s in exec_steps]
        self.assertEqual(actual_ids, expected_ids)

    # 2. Structured plan steps survive tool selection unchanged
    def test_02_structured_steps_survive_tool_selection(self):
        step_custom = PlanStep(
            id="custom_thermal_step",
            type=StepType.DATA.value,
            operation="fetch_sst_data",
            depends_on=[],
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            required=True,
            parameters={"location": {"name": "Goa", "latitude": 15.29, "longitude": 73.98}},
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
        )
        plan = ExecutionPlan(
            plan_id="plan_test_01",
            intent=MarineIntent.FISHING_RECOMMENDATION.value,
            steps=[step_custom],
        )
        state: MarineState = {
            "execution_plan": plan,
            "plan": ["weather", "sst"],  # Legacy plan list present but must NOT override
        }

        res = asyncio.run(tool_selection_node(state))
        steps = res["execution_steps"]

        self.assertEqual(len(steps), 1)
        survived = steps[0]
        self.assertEqual(survived.id, "custom_thermal_step")
        self.assertEqual(survived.operation, "fetch_sst_data")
        self.assertEqual(survived.type, StepType.DATA.value)
        self.assertEqual(survived.target, ToolExecutionTarget.P4_EXTERNAL_TOOL)

    # 3. Dependencies survive tool selection unchanged
    def test_03_dependencies_survive_tool_selection(self):
        step_a = PlanStep(id="data_a", type=StepType.DATA.value, operation="op_a", depends_on=[])
        step_b = PlanStep(id="data_b", type=StepType.DATA.value, operation="op_b", depends_on=[])
        step_c = PlanStep(id="analytics_c", type=StepType.ANALYTICS.value, operation="op_c", depends_on=["data_a", "data_b"])

        plan = ExecutionPlan(
            plan_id="plan_dag_test",
            steps=[step_a, step_b, step_c],
        )
        state: MarineState = {
            "execution_plan": plan,
            "plan": ["PFZ", "weather"],
        }

        res = asyncio.run(tool_selection_node(state))
        steps_by_id = {s.id: s for s in res["execution_steps"]}

        self.assertEqual(steps_by_id["analytics_c"].depends_on, ["data_a", "data_b"])
        self.assertEqual(steps_by_id["data_a"].depends_on, [])
        self.assertEqual(steps_by_id["data_b"].depends_on, [])

    # 4. Parameters survive tool selection unchanged
    def test_04_parameters_survive_tool_selection(self):
        custom_params = {
            "location": {"name": "Karwar", "latitude": 14.80, "longitude": 74.13},
            "temporal_mode": "forecast",
            "threshold_knots": 25.0,
        }
        step = PlanStep(
            id="wind_step",
            type=StepType.DATA.value,
            operation="get_wind",
            parameters=custom_params,
        )
        plan = ExecutionPlan(steps=[step])
        state: MarineState = {"execution_plan": plan}

        res = asyncio.run(tool_selection_node(state))
        survived_step = res["execution_steps"][0]
        self.assertEqual(survived_step.parameters, custom_params)
        self.assertEqual(survived_step.parameters["threshold_knots"], 25.0)

    # 5. Input policy survives tool selection unchanged
    def test_05_input_policy_survives_tool_selection(self):
        step = PlanStep(
            id="risk_step",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            input_policy=InputPolicy.ALLOW_PARTIAL.value,
            depends_on=["wind", "wave"],
        )
        plan = ExecutionPlan(steps=[step])
        state: MarineState = {"execution_plan": plan}

        res = asyncio.run(tool_selection_node(state))
        self.assertEqual(res["execution_steps"][0].input_policy, InputPolicy.ALLOW_PARTIAL.value)

    # 6. No duplicate steps are created
    def test_06_no_duplicate_steps_created(self):
        state: MarineState = {
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": {"raw": "today"},
        }
        plan_res = asyncio.run(planner_node(state))
        state.update(plan_res)

        ts_res = asyncio.run(tool_selection_node(state))
        exec_steps = ts_res["execution_steps"]

        step_ids = [s.id for s in exec_steps]
        self.assertEqual(len(step_ids), len(set(step_ids)), "Steps must contain unique step IDs without duplication")

    # 7. Legacy plan fallback still works when ExecutionPlan is absent
    def test_07_legacy_plan_fallback_when_execution_plan_absent(self):
        state: MarineState = {
            "plan": ["weather", "sst", "PFZ"],
            "location": {"name": "Cochin", "latitude": 9.93, "longitude": 76.26},
            "execution_plan": None,
        }
        res = asyncio.run(tool_selection_node(state))
        steps = res["execution_steps"]

        self.assertGreater(len(steps), 0)
        step_ids = [s.id for s in steps]
        self.assertIn("step_weather", step_ids)
        self.assertIn("step_sst", step_ids)
        self.assertIn("step_chlorophyll", step_ids)
        self.assertIn("step_pfz_calc", step_ids)

    # 8. Route missing information is correctly flagged
    def test_08_route_missing_information_flagged(self):
        # Empty route
        state: MarineState = {
            "intent": MarineIntent.ROUTE_QUERY.value,
            "route": None,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertTrue(plan.requires_clarification)
        self.assertIn("route", plan.missing)

        # Route without origin or destination
        state_empty_route: MarineState = {
            "intent": MarineIntent.ROUTE_QUERY.value,
            "route": {},
        }
        res2 = asyncio.run(planner_node(state_empty_route))
        plan2: ExecutionPlan = res2["execution_plan"]
        self.assertTrue(plan2.requires_clarification)
        self.assertIn("route", plan2.missing)

        # Route with valid origin and destination
        state_valid_route: MarineState = {
            "intent": MarineIntent.ROUTE_QUERY.value,
            "route": {"origin": "Mangalore Port", "destination": "Karwar Harbor"},
        }
        res3 = asyncio.run(planner_node(state_valid_route))
        plan3: ExecutionPlan = res3["execution_plan"]
        self.assertFalse(plan3.requires_clarification)
        self.assertEqual(len(plan3.missing), 0)

    # 9. Geofence missing location is correctly flagged
    def test_09_geofence_missing_location_flagged(self):
        state_no_loc: MarineState = {
            "intent": MarineIntent.GEOFENCE_QUERY.value,
            "location": None,
        }
        res = asyncio.run(planner_node(state_no_loc))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertTrue(plan.requires_clarification)
        self.assertIn("location", plan.missing)

        # Valid location
        state_valid_loc: MarineState = {
            "intent": MarineIntent.GEOFENCE_QUERY.value,
            "location": {"name": "12.86, 74.84", "latitude": 12.86, "longitude": 74.84},
        }
        res_valid = asyncio.run(planner_node(state_valid_loc))
        plan_valid: ExecutionPlan = res_valid["execution_plan"]
        self.assertFalse(plan_valid.requires_clarification)
        self.assertEqual(len(plan_valid.missing), 0)

    # 10. Historical plan remains dynamically variable-driven
    def test_10_historical_plan_dynamic_variables(self):
        state: MarineState = {
            "intent": MarineIntent.HISTORICAL_ANALYSIS.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": {"raw": "last 30 days", "is_historical": True},
            "variables": ["SST", "CHLOROPHYLL"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertEqual(step_ids, ["historical_sst", "historical_chlorophyll", "trends", "response"])
        self.assertNotIn("wind", step_ids)
        self.assertNotIn("wave", step_ids)
        self.assertFalse(plan.requires_clarification)

    # 11. Dynamic dependency resolution in executor without hardcoded step IDs
    def test_11_executor_dynamic_dependency_resolution(self):
        # Step with arbitrary ID 'custom_wind' and analytics step 'custom_risk' depending on it
        step_1 = PlanStep(
            id="custom_wind",
            type=StepType.DATA.value,
            operation="get_wind",
            depends_on=[],
            target=ToolExecutionTarget.P4_EXTERNAL_TOOL,
            parameters={"location": {"name": "Mangalore"}},
        )
        step_2 = PlanStep(
            id="custom_risk",
            type=StepType.ANALYTICS.value,
            operation="calculate_marine_risk",
            depends_on=["custom_wind"],
            target=ToolExecutionTarget.P6_MARINE_ANALYTICS,
            parameters={"vessel_type": "small_motorized_boat"},
        )
        state: MarineState = {
            "execution_steps": [step_1, step_2],
            "errors": [],
            "tool_results": [],
            "analytics_results": [],
        }

        res = asyncio.run(executor_node(state))
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["tool_results"]), 1)
        self.assertEqual(len(res["analytics_results"]), 1)

        tool_res = res["tool_results"][0]
        analytics_res = res["analytics_results"][0]

        self.assertEqual(tool_res["step_id"], "custom_wind")
        self.assertEqual(analytics_res["step_id"], "custom_risk")
        self.assertEqual(analytics_res["result"]["status"], "success")

    # 12. Full marine agent invocation succeeds end-to-end
    def test_12_full_marine_agent_end_to_end(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        resp = asyncio.run(run_marine_agent_async(query, role=RoleType.FISHERMAN))

        self.assertIsNotNone(resp)
        self.assertEqual(resp.status, "success")
        self.assertIsNotNone(resp.safety_alert)
        self.assertIsNotNone(resp.visual_payload)
        self.assertTrue(len(resp.markdown_content) > 0)


if __name__ == "__main__":
    unittest.main()
