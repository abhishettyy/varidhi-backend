"""Unit tests for Phase 2 Query Understanding layer and structured QueryIntent."""

import asyncio
import unittest

from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.nodes.planner import planner_node
from backend.agents.schemas.intent import MarineIntent, MarineVariable, QueryIntent
from backend.agents.state.marine_state import MarineState


class TestQueryUnderstanding(unittest.TestCase):
    """Test suite for Query Understanding, entity extraction, and structured QueryIntent schema."""

    def test_example_1_fishing_recommendation(self):
        """Example 1: 'I'm near Mangalore. Where should I fish tomorrow morning?'"""
        state: MarineState = {"query": "I'm near Mangalore. Where should I fish tomorrow morning?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertIsNotNone(result["location"])
        self.assertEqual(result["location"]["name"], "Mangalore")
        self.assertAlmostEqual(result["location"]["latitude"], 12.8681, places=3)
        self.assertAlmostEqual(result["location"]["longitude"], 74.8427, places=3)
        self.assertIsNotNone(result["time_range"])
        self.assertEqual(result["time_range"]["raw"], "tomorrow morning")
        self.assertEqual(result["time_range"]["relative_day"], "tomorrow")
        self.assertEqual(result["time_range"]["period"], "morning")

    def test_example_2_pfz_search(self):
        """Example 2: 'What is the nearest PFZ to Mangalore?'"""
        state: MarineState = {"query": "What is the nearest PFZ to Mangalore?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.PFZ_SEARCH.value)
        self.assertIsNotNone(result["location"])
        self.assertEqual(result["location"]["name"], "Mangalore")
        self.assertIn(MarineVariable.PFZ.value, result["variables"])
        self.assertIsNone(result["time_range"], "No time range was specified, must remain None")

    def test_example_3_marine_safety(self):
        """Example 3: 'Is it safe to go fishing tomorrow morning?'"""
        state: MarineState = {"query": "Is it safe to go fishing tomorrow morning?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.MARINE_SAFETY.value)
        self.assertIsNone(result["location"], "No location was specified, must remain None")
        self.assertIsNotNone(result["time_range"])
        self.assertEqual(result["time_range"]["raw"], "tomorrow morning")

    def test_example_4_weather_query(self):
        """Example 4: 'What's the weather around Mangalore tonight?'"""
        state: MarineState = {"query": "What's the weather around Mangalore tonight?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.WEATHER_QUERY.value)
        self.assertIsNotNone(result["location"])
        self.assertEqual(result["location"]["name"], "Mangalore")
        self.assertIsNotNone(result["time_range"])
        self.assertEqual(result["time_range"]["raw"], "tonight")
        self.assertEqual(result["time_range"]["period"], "night")

    def test_example_5_hazard_query(self):
        """Example 5: 'Are there any dangerous conditions near Mangalore?'"""
        state: MarineState = {"query": "Are there any dangerous conditions near Mangalore?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.HAZARD_QUERY.value)
        self.assertIsNotNone(result["location"])
        self.assertEqual(result["location"]["name"], "Mangalore")
        self.assertIsNone(result["time_range"])

    def test_example_6_geofence_query(self):
        """Example 6: 'Is this point inside a restricted marine zone?'"""
        state: MarineState = {"query": "Is this point inside a restricted marine zone?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.GEOFENCE_QUERY.value)
        self.assertIsNone(result["location"])
        self.assertIsNone(result["time_range"])

    def test_example_7_route_query(self):
        """Example 7: 'Can my route cross this restricted area?'"""
        state: MarineState = {"query": "Can my route cross this restricted area?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.ROUTE_QUERY.value)
        self.assertIsNone(result["location"])
        self.assertIsNone(result["time_range"])

    def test_example_8_vessel_query(self):
        """Example 8: 'Where is vessel IMO1234567?'"""
        state: MarineState = {"query": "Where is vessel IMO1234567?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.VESSEL_QUERY.value)
        self.assertIsNotNone(result["vessel"])
        self.assertEqual(result["vessel"]["id"], "IMO1234567")
        self.assertIsNone(result["location"])
        self.assertIsNone(result["time_range"])

    def test_example_9_historical_analysis(self):
        """Example 9: 'Show SST and chlorophyll around Mangalore for the last 30 days.'"""
        state: MarineState = {"query": "Show SST and chlorophyll around Mangalore for the last 30 days."}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.HISTORICAL_ANALYSIS.value)
        self.assertIsNotNone(result["location"])
        self.assertEqual(result["location"]["name"], "Mangalore")
        self.assertIn(MarineVariable.SST.value, result["variables"])
        self.assertIn(MarineVariable.CHLOROPHYLL.value, result["variables"])
        self.assertIsNotNone(result["time_range"])
        self.assertEqual(result["time_range"]["raw"], "last 30 days")
        self.assertTrue(result["time_range"]["is_historical"])

    def test_example_10_general_marine_query(self):
        """Example 10: 'Hello, what can you tell me about the ocean?'"""
        state: MarineState = {"query": "Hello, what can you tell me about the ocean?"}
        result = asyncio.run(understand_query_node(state))

        self.assertEqual(result["intent"], MarineIntent.GENERAL_MARINE_QUERY.value)
        self.assertIsNone(result["location"])
        self.assertIsNone(result["time_range"])

    def test_coordinate_input_recognition(self):
        """Verify recognizing coordinate input like '12.91, 74.85' structurally."""
        state: MarineState = {"query": "Check sea conditions at 12.91, 74.85 today"}
        result = asyncio.run(understand_query_node(state))

        loc = result["location"]
        self.assertIsNotNone(loc)
        self.assertAlmostEqual(loc["latitude"], 12.91, places=2)
        self.assertAlmostEqual(loc["longitude"], 74.85, places=2)
        self.assertEqual(loc["name"], "12.91, 74.85")

    def test_unknown_location_preserves_name_null_coords(self):
        """Verify unknown locations preserve name while keeping latitude/longitude null."""
        state: MarineState = {"query": "Check fishing potential near Emerald Lagoon tomorrow"}
        result = asyncio.run(understand_query_node(state))

        loc = result["location"]
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Emerald Lagoon")
        self.assertIsNone(loc["latitude"], "Latitude must be None for unknown locations")
        self.assertIsNone(loc["longitude"], "Longitude must be None for unknown locations")

    def test_temporal_expressions_variety(self):
        """Verify recognition of various temporal expressions."""
        test_phrases = [
            ("waves this morning near Mangalore", "this morning", "morning", False),
            ("wind this week near Mangalore", "this week", "all-day", False),
            ("sea state next week near Mangalore", "next week", "all-day", False),
            ("SST trends for the last 7 days", "last 7 days", "all-day", True),
            ("past month wave observations", "past month", "all-day", True),
        ]

        for query, expected_raw, expected_period, expected_hist in test_phrases:
            with self.subTest(query=query):
                state: MarineState = {"query": query}
                result = asyncio.run(understand_query_node(state))
                tr = result["time_range"]
                self.assertIsNotNone(tr, f"Failed to extract time range from '{query}'")
                self.assertEqual(tr["raw"], expected_raw)
                self.assertEqual(tr["period"], expected_period)
                self.assertEqual(tr["is_historical"], expected_hist)

    def test_marine_variables_comprehensive(self):
        """Verify extraction of all requested marine variables."""
        query = (
            "Check sea surface temperature, chlorophyll-a, PFZ, wind speed, "
            "wave height, swell, tide, currents, and vessel activity near Mangalore"
        )
        state: MarineState = {"query": query}
        result = asyncio.run(understand_query_node(state))
        vars_extracted = result["variables"]

        self.assertIn(MarineVariable.SST.value, vars_extracted)
        self.assertIn(MarineVariable.CHLOROPHYLL.value, vars_extracted)
        self.assertIn(MarineVariable.PFZ.value, vars_extracted)
        self.assertIn(MarineVariable.WIND.value, vars_extracted)
        self.assertIn(MarineVariable.WAVE.value, vars_extracted)
        self.assertIn(MarineVariable.SWELL.value, vars_extracted)
        self.assertIn(MarineVariable.TIDE.value, vars_extracted)
        self.assertIn(MarineVariable.CURRENT.value, vars_extracted)
        self.assertIn(MarineVariable.VESSEL_ACTIVITY.value, vars_extracted)

    def test_planner_integration_all_intents(self):
        """Verify planner node generates valid plans for all 10 intent categories."""
        for intent in MarineIntent:
            state: MarineState = {
                "intent": intent.value,
                "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
                "variables": ["SST", "WAVE"],
            }
            res = asyncio.run(planner_node(state))
            self.assertIn("plan", res)
            self.assertIsInstance(res["plan"], list)
            self.assertGreater(len(res["plan"]), 0)


if __name__ == "__main__":
    unittest.main()
