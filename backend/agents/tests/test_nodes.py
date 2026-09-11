"""Unit tests for individual LangGraph nodes (understand_query and planner)."""

import asyncio
import unittest

from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.nodes.planner import planner_node
from backend.agents.schemas.intent import MarineIntent
from backend.agents.state.marine_state import MarineState


class TestMarineNodes(unittest.TestCase):
    """Test suite for understand_query and planner nodes."""

    def test_understand_query_mangalore_fishing(self):
        """Verify prompt example: 'I'm near Mangalore. Where should I fish tomorrow morning?'"""
        state: MarineState = {
            "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
            "user_type": "fisherman",
            "tool_results": [],
            "analytics_results": [],
            "errors": [],
        }

        result = asyncio.run(understand_query_node(state))

        # Check Intent
        self.assertEqual(result["intent"], MarineIntent.FISHING_RECOMMENDATION.value)

        # Check Structured Location
        location = result["location"]
        self.assertIsNotNone(location)
        self.assertEqual(location.get("name"), "Mangalore")
        self.assertAlmostEqual(location.get("latitude"), 12.8681, places=3)
        self.assertAlmostEqual(location.get("longitude"), 74.8427, places=3)
        self.assertEqual(location.get("harbor"), "Mangalore Old Port")

        # Check Structured Time Range
        time_range = result["time_range"]
        self.assertIsInstance(time_range, dict)
        self.assertEqual(time_range.get("raw"), "tomorrow morning")
        self.assertEqual(time_range.get("relative_day"), "tomorrow")
        self.assertEqual(time_range.get("period"), "morning")

    def test_understand_query_weather_safety(self):
        """Verify weather intent extraction and time parsing."""
        state: MarineState = {
            "query": "What is the wave height and wind speed near Kochi today afternoon?",
            "user_type": "fisherman",
            "errors": [],
        }

        result = asyncio.run(understand_query_node(state))
        self.assertEqual(result["intent"], MarineIntent.WEATHER_QUERY.value)
        self.assertEqual(result["location"].get("name"), "Kochi")
        self.assertEqual(result["time_range"].get("raw"), "today afternoon")
        self.assertEqual(result["time_range"].get("relative_day"), "today")
        self.assertEqual(result["time_range"].get("period"), "afternoon")

    def test_understand_query_coordinates(self):
        """Verify explicit coordinate extraction."""
        state: MarineState = {
            "query": "Check fishing potential at 15.30 N, 73.80 E this weekend",
            "user_type": "researcher",
            "errors": [],
        }

        result = asyncio.run(understand_query_node(state))
        self.assertEqual(result["intent"], MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertAlmostEqual(result["location"].get("latitude"), 15.30, places=2)
        self.assertAlmostEqual(result["location"].get("longitude"), 73.80, places=2)
        self.assertEqual(result["time_range"].get("raw"), "this weekend")
        self.assertEqual(result["time_range"].get("relative_day"), "this weekend")

    def test_planner_fishing_recommendation(self):
        """Verify planner output contains PFZ, SST, weather, waves, tide, restrictions for fishing."""
        state: MarineState = {
            "query": "Where should I fish tomorrow?",
            "intent": MarineIntent.FISHING_RECOMMENDATION.value,
            "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
            "time_range": {"raw": "tomorrow morning", "relative_day": "tomorrow", "period": "morning"},
            "user_type": "fisherman",
        }

        result = asyncio.run(planner_node(state))
        plan = result["plan"]

        self.assertIsInstance(plan, list)
        self.assertIn("PFZ", plan)
        self.assertIn("SST", plan)
        self.assertIn("weather", plan)
        self.assertIn("waves", plan)
        self.assertIn("tide", plan)
        self.assertIn("restrictions", plan)

    def test_planner_weather_safety(self):
        """Verify planner output for sea state & weather safety queries."""
        state: MarineState = {
            "query": "Is it safe to go out to sea?",
            "intent": MarineIntent.MARINE_SAFETY.value,
            "location": {"name": "Veraval", "latitude": 20.9077, "longitude": 70.3678},
            "time_range": {"raw": "next 24 hours", "relative_day": "today", "period": "all-day"},
            "user_type": "maritime_operator",
        }

        result = asyncio.run(planner_node(state))
        plan = result["plan"]

        self.assertIn("weather", plan)
        self.assertIn("waves", plan)
        self.assertIn("wind", plan)
        self.assertIn("risk_score", plan)


if __name__ == "__main__":
    unittest.main()
