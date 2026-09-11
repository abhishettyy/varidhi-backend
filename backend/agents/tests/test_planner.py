"""Comprehensive unit tests for Phase 3 Planner / Task Planning layer."""

import asyncio
import unittest

from backend.agents.nodes.planner import planner_node
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.schemas.intent import MarineIntent, MarineVariable
from backend.agents.schemas.plan import ExecutionPlan, PlanStep, StepType
from backend.agents.state.marine_state import MarineState


class TestPhase3Planner(unittest.TestCase):
    """Test suite for Phase 3 ExecutionPlan generation, DAG dependencies, and intent mapping."""

    # 1. Fishing recommendation plan
    def test_01_fishing_recommendation_plan(self):
        state: MarineState = {
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": {"raw": "tomorrow morning", "relative_day": "tomorrow", "period": "morning"},
            "variables": ["PFZ", "SST"],
            "constraints": {"max_wave_height_m": 2.0},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertIsInstance(plan, ExecutionPlan)
        step_ids = [s.id for s in plan.steps]

        # Verify DATA steps present
        self.assertIn("pfz", step_ids)
        self.assertIn("sst", step_ids)
        self.assertIn("chlorophyll", step_ids)
        self.assertIn("wind", step_ids)
        self.assertIn("wave", step_ids)
        self.assertIn("restrictions", step_ids)

        # Verify ANALYTICS, DECISION, RESPONSE steps
        self.assertIn("opportunity", step_ids)
        self.assertIn("risk", step_ids)
        self.assertIn("ranking", step_ids)
        self.assertIn("decision", step_ids)
        self.assertIn("response", step_ids)

    # 2. PFZ search plan
    def test_02_pfz_search_plan(self):
        state: MarineState = {
            "intent": MarineIntent.PFZ_SEARCH.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "variables": ["PFZ"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("pfz", step_ids)
        self.assertIn("distance", step_ids)
        self.assertIn("ranking", step_ids)
        self.assertIn("response", step_ids)

    # 3. Marine safety plan
    def test_03_marine_safety_plan(self):
        state: MarineState = {
            "intent": MarineIntent.MARINE_SAFETY.value,
            "location": {"name": "Veraval", "latitude": 20.9077, "longitude": 70.3678},
            "time_range": {"raw": "today", "period": "all-day"},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("wind", step_ids)
        self.assertIn("wave", step_ids)
        self.assertIn("risk", step_ids)
        self.assertIn("decision", step_ids)
        self.assertIn("response", step_ids)

    # 4. Weather plan
    def test_04_weather_plan(self):
        state: MarineState = {
            "intent": MarineIntent.WEATHER_QUERY.value,
            "location": {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
            "time_range": {"raw": "tonight", "period": "night"},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("wind", step_ids)
        self.assertIn("wave", step_ids)
        self.assertIn("response", step_ids)
        # Should not request fishing opportunity
        self.assertNotIn("opportunity", step_ids)

    # 5. Hazard plan
    def test_05_hazard_plan(self):
        state: MarineState = {
            "intent": MarineIntent.HAZARD_QUERY.value,
            "location": {"name": "Vizag", "latitude": 17.6868, "longitude": 83.2185},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("wind", step_ids)
        self.assertIn("wave", step_ids)
        self.assertIn("risk", step_ids)
        self.assertIn("decision", step_ids)
        self.assertIn("response", step_ids)

    # 6. Geofence plan
    def test_06_geofence_plan(self):
        state: MarineState = {
            "intent": MarineIntent.GEOFENCE_QUERY.value,
            "location": {"name": "12.86, 74.84", "latitude": 12.86, "longitude": 74.84},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("geofence", step_ids)
        self.assertIn("restrictions", step_ids)
        self.assertIn("decision", step_ids)
        self.assertIn("response", step_ids)

    # 7. Route plan
    def test_07_route_plan(self):
        state: MarineState = {
            "intent": MarineIntent.ROUTE_QUERY.value,
            "route": {"origin": "Kochi", "destination": "Mangalore"},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("geofence", step_ids)
        self.assertIn("wind", step_ids)
        self.assertIn("wave", step_ids)
        self.assertIn("route_analysis", step_ids)
        self.assertIn("decision", step_ids)
        self.assertIn("response", step_ids)

    # 8. Vessel plan
    def test_08_vessel_plan(self):
        state: MarineState = {
            "intent": MarineIntent.VESSEL_QUERY.value,
            "vessel": {"id": "IMO1234567"},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("vessel_pos", step_ids)
        self.assertIn("vessel_act", step_ids)
        self.assertIn("response", step_ids)
        self.assertFalse(plan.requires_clarification)

    # 9. Historical analysis plan
    def test_09_historical_analysis_plan(self):
        state: MarineState = {
            "intent": MarineIntent.HISTORICAL_ANALYSIS.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": {"raw": "last 30 days", "is_historical": True},
            "variables": ["SST", "CHLOROPHYLL"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("historical_sst", step_ids)
        self.assertIn("historical_chlorophyll", step_ids)
        self.assertIn("trends", step_ids)
        self.assertIn("response", step_ids)

    # 10. General marine query plan
    def test_10_general_marine_query_plan(self):
        state: MarineState = {
            "intent": MarineIntent.GENERAL_MARINE_QUERY.value,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].id, "response")
        self.assertEqual(plan.steps[0].type, StepType.RESPONSE.value)

    # 11. Dynamic SST variable augmentation
    def test_11_dynamic_sst_variable(self):
        state: MarineState = {
            "intent": MarineIntent.HISTORICAL_ANALYSIS.value,
            "variables": ["SST"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("historical_sst", step_ids)
        self.assertNotIn("historical_chlorophyll", step_ids)

    # 12. Dynamic Chlorophyll variable augmentation
    def test_12_dynamic_chlorophyll_variable(self):
        state: MarineState = {
            "intent": MarineIntent.HISTORICAL_ANALYSIS.value,
            "variables": ["CHLOROPHYLL"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("historical_chlorophyll", step_ids)
        self.assertNotIn("historical_sst", step_ids)

    # 13. Multiple variables
    def test_13_multiple_variables(self):
        state: MarineState = {
            "intent": MarineIntent.HISTORICAL_ANALYSIS.value,
            "variables": ["SST", "CHLOROPHYLL", "WAVE"],
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        step_ids = [s.id for s in plan.steps]
        self.assertIn("historical_sst", step_ids)
        self.assertIn("historical_chlorophyll", step_ids)
        self.assertIn("historical_wave", step_ids)

    # 14. Missing location handling
    def test_14_missing_location(self):
        state: MarineState = {
            "intent": MarineIntent.PFZ_SEARCH.value,
            "location": None,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertTrue(plan.requires_clarification)
        self.assertIn("location", plan.missing)
        # Still produces valid steps
        self.assertGreater(len(plan.steps), 0)

    # 15. Missing time handling
    def test_15_missing_time(self):
        state: MarineState = {
            "intent": MarineIntent.WEATHER_QUERY.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": None,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertGreater(len(plan.steps), 0)

    # 16. Missing vessel handling
    def test_16_missing_vessel(self):
        state: MarineState = {
            "intent": MarineIntent.VESSEL_QUERY.value,
            "vessel": None,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertTrue(plan.requires_clarification)
        self.assertIn("vessel", plan.missing)

    # 17. Missing route handling
    def test_17_missing_route(self):
        state: MarineState = {
            "intent": MarineIntent.ROUTE_QUERY.value,
            "route": None,
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertGreater(len(plan.steps), 0)

    # 18. Dependency correctness in DAG
    def test_18_dependency_correctness(self):
        state: MarineState = {
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        steps_by_id = {s.id: s for s in plan.steps}

        # 1. Independent DATA steps have empty depends_on
        for data_id in ["pfz", "sst", "chlorophyll", "wind", "wave", "swell", "tide", "restrictions"]:
            self.assertEqual(steps_by_id[data_id].depends_on, [], f"Data step {data_id} must have no dependencies")

        # 2. Analytics depend on required data
        self.assertEqual(steps_by_id["opportunity"].depends_on, ["pfz", "sst", "chlorophyll"])
        self.assertEqual(steps_by_id["risk"].depends_on, ["wind", "wave", "swell", "tide"])
        self.assertEqual(steps_by_id["ranking"].depends_on, ["opportunity", "risk"])

        # 3. Decision depends on ranking and restrictions
        self.assertEqual(steps_by_id["decision"].depends_on, ["ranking", "restrictions"])

        # 4. Response depends on decision
        self.assertEqual(steps_by_id["response"].depends_on, ["decision"])

    # 19. Required vs Optional steps
    def test_19_required_vs_optional_steps(self):
        state: MarineState = {
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
        }
        res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = res["execution_plan"]

        steps_by_id = {s.id: s for s in plan.steps}

        self.assertTrue(steps_by_id["pfz"].required)
        self.assertTrue(steps_by_id["wind"].required)
        self.assertTrue(steps_by_id["wave"].required)
        self.assertTrue(steps_by_id["restrictions"].required)
        self.assertFalse(steps_by_id["sst"].required)
        self.assertFalse(steps_by_id["chlorophyll"].required)
        self.assertFalse(steps_by_id["swell"].required)
        self.assertFalse(steps_by_id["tide"].required)

    # 20. Invalid / empty intent
    def test_20_invalid_or_empty_intent(self):
        for bad_intent in ["", None, "UNKNOWN_INTENT_XYZ"]:
            state: MarineState = {"intent": bad_intent}
            res = asyncio.run(planner_node(state))
            plan: ExecutionPlan = res["execution_plan"]
            self.assertIsInstance(plan, ExecutionPlan)
            self.assertGreater(len(plan.steps), 0)

    # 21. Planner does not execute tools
    def test_21_planner_does_not_execute_tools(self):
        state: MarineState = {
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
        }
        res = asyncio.run(planner_node(state))
        # Verify planner only returns plan/execution_plan, no tool outputs
        self.assertIn("execution_plan", res)
        self.assertNotIn("tool_results", res)
        self.assertNotIn("analytics_results", res)

    # 22. End-to-end integration: Query Understanding -> Planner for Mangalore query
    def test_22_e2e_mangalore_query_to_plan(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state: MarineState = {"query": query}

        # Step 1: Understand Query
        qu_res = asyncio.run(understand_query_node(state))
        state.update(qu_res)

        # Step 2: Plan
        plan_res = asyncio.run(planner_node(state))
        plan: ExecutionPlan = plan_res["execution_plan"]

        self.assertEqual(plan.intent, MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertFalse(plan.requires_clarification)
        self.assertEqual(plan.steps[0].parameters["location"]["name"], "Mangalore")


if __name__ == "__main__":
    unittest.main()
