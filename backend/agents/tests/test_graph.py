"""Unit tests for LangGraph workflow execution and state integrity."""

import unittest
from backend.agents.graph.workflow import (
    run_minimal_marine_graph,
    run_marine_agent,
    get_minimal_marine_graph,
    get_marine_agent_graph,
)
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.response import RoleType


class TestMarineGraphExecution(unittest.TestCase):
    """Test suite for graph compilation, execution, and MarineState schema integrity."""

    def test_minimal_graph_mangalore_query(self):
        """
        Execute minimal graph on example query:
        'I'm near Mangalore. Where should I fish tomorrow morning?'
        """
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        final_state = run_minimal_marine_graph(query, user_type="fisherman")

        # 1. Verify Query & User Type
        self.assertEqual(final_state.get("query"), query)
        self.assertEqual(final_state.get("user_type"), "fisherman")

        # 2. Verify Intent
        self.assertEqual(final_state.get("intent"), MarineIntent.FISHING_RECOMMENDATION.value)

        # 3. Verify Structured Location
        location = final_state.get("location")
        self.assertIsInstance(location, dict)
        self.assertEqual(location.get("name"), "Mangalore")
        self.assertAlmostEqual(location.get("latitude"), 12.8681, places=3)
        self.assertAlmostEqual(location.get("longitude"), 74.8427, places=3)
        self.assertEqual(location.get("harbor"), "Mangalore Old Port")
        self.assertEqual(location.get("region"), "Karnataka Coast")

        # 4. Verify Structured Time Range
        time_range = final_state.get("time_range")
        self.assertIsInstance(time_range, dict)
        self.assertEqual(time_range.get("raw"), "tomorrow morning")
        self.assertEqual(time_range.get("relative_day"), "tomorrow")
        self.assertEqual(time_range.get("period"), "morning")

        # 5. Verify Plan
        plan = final_state.get("plan")
        self.assertIsInstance(plan, list)
        self.assertIn("PFZ", plan)
        self.assertIn("SST", plan)
        self.assertIn("weather", plan)
        self.assertIn("waves", plan)
        self.assertIn("tide", plan)
        self.assertIn("restrictions", plan)

        # 6. Verify Error List is clean
        self.assertEqual(len(final_state.get("errors", [])), 0)

    def test_minimal_graph_weather_query(self):
        """Execute minimal graph on weather safety inquiry."""
        query = "How rough are the waves and wind near Chennai today evening?"
        final_state = run_minimal_marine_graph(query, user_type="maritime_operator")

        self.assertEqual(final_state.get("intent"), MarineIntent.WEATHER_QUERY.value)
        self.assertEqual(final_state.get("location").get("name"), "Chennai")
        self.assertEqual(final_state.get("time_range").get("raw"), "today evening")
        self.assertEqual(final_state.get("time_range").get("relative_day"), "today")
        self.assertEqual(final_state.get("time_range").get("period"), "evening")
        self.assertIn("waves", final_state.get("plan"))
        self.assertIn("wind", final_state.get("plan"))

    def test_full_marine_agent_execution(self):
        """Verify full graph execution completes and produces valid response & evidence."""
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        response = run_marine_agent(query, role=RoleType.FISHERMAN)

        self.assertIsNotNone(response)
        self.assertEqual(response.status, "success")
        self.assertIsNotNone(response.safety_alert)
        self.assertIsNotNone(response.markdown_content)
        self.assertTrue(len(response.markdown_content) > 0)
        self.assertIsNotNone(response.visual_payload)
        self.assertIn("SST", response.visual_payload.metric_badges)

    def test_graph_singletons(self):
        """Verify graph compilations are singletons and callable."""
        min_g = get_minimal_marine_graph()
        full_g = get_marine_agent_graph()
        self.assertIsNotNone(min_g)
        self.assertIsNotNone(full_g)


if __name__ == "__main__":
    unittest.main()
