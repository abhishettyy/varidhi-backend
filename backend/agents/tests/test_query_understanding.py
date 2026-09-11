"""Comprehensive unit tests for Phase 2 Query Understanding layer."""

import asyncio
import unittest

from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.nodes.planner import planner_node
from backend.agents.schemas.intent import MarineIntent, MarineVariable, QueryIntent
from backend.agents.state.marine_state import MarineState


class TestPhase2QueryUnderstanding(unittest.TestCase):
    """
    Comprehensive test suite for Phase 2 Query Understanding covering:
    - 10 intent categories
    - Known / unknown locations and coordinate recognition
    - Temporal expressions
    - Single and multi-variable extraction
    - Missing entity handling (zero hallucination)
    - Ambiguous, empty, and invalid inputs
    - Planner integration
    """

    # 1. Fishing recommendation
    def test_01_fishing_recommendation(self):
        state: MarineState = {"query": "I'm near Mangalore. Where should I fish tomorrow morning?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertGreaterEqual(res["confidence"], 0.85)

    # 2. PFZ search
    def test_02_pfz_search(self):
        state: MarineState = {"query": "What is the nearest PFZ to Mangalore?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.PFZ_SEARCH.value)
        self.assertIn(MarineVariable.PFZ.value, res["variables"])

    # 3. Marine safety
    def test_03_marine_safety(self):
        state: MarineState = {"query": "Is it safe to go fishing tomorrow morning?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.MARINE_SAFETY.value)

    # 4. Weather
    def test_04_weather(self):
        state: MarineState = {"query": "What's the weather around Mangalore tonight?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.WEATHER_QUERY.value)

    # 5. Hazard
    def test_05_hazard(self):
        state: MarineState = {"query": "Are there any dangerous conditions near Mangalore?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.HAZARD_QUERY.value)

    # 6. Geofence
    def test_06_geofence(self):
        state: MarineState = {"query": "Is this point inside a restricted marine zone?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.GEOFENCE_QUERY.value)

    # 7. Route
    def test_07_route(self):
        state: MarineState = {"query": "Can my route cross this restricted area?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.ROUTE_QUERY.value)

    # 8. Vessel
    def test_08_vessel(self):
        state: MarineState = {"query": "Where is vessel IMO1234567?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.VESSEL_QUERY.value)
        self.assertIsNotNone(res["vessel"])
        self.assertEqual(res["vessel"]["id"], "IMO1234567")

    # 9. Historical analysis
    def test_09_historical_analysis(self):
        state: MarineState = {"query": "Show SST and chlorophyll around Mangalore for the last 30 days."}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.HISTORICAL_ANALYSIS.value)
        self.assertIsNotNone(res["time_range"])
        self.assertTrue(res["time_range"]["is_historical"])

    # 10. General marine query
    def test_10_general_marine_query(self):
        state: MarineState = {"query": "Hello, what can you tell me about the ocean?"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.GENERAL_MARINE_QUERY.value)

    # 11. Known location: Mangalore
    def test_11_known_location_mangalore(self):
        state: MarineState = {"query": "Where should I fish near Mangalore?"}
        res = asyncio.run(understand_query_node(state))
        loc = res["location"]
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Mangalore")
        self.assertAlmostEqual(loc["latitude"], 12.8681, places=3)
        self.assertAlmostEqual(loc["longitude"], 74.8427, places=3)
        self.assertEqual(loc["harbor"], "Mangalore Old Port")
        self.assertEqual(loc["region"], "Karnataka Coast")

    # 12. Unknown location (strict null policy: no fabricated coordinates)
    def test_12_unknown_location(self):
        state: MarineState = {"query": "Check fishing potential near Emerald Lagoon tomorrow"}
        res = asyncio.run(understand_query_node(state))
        loc = res["location"]
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Emerald Lagoon")
        self.assertIsNone(loc["latitude"], "Latitude must remain None for unknown locations")
        self.assertIsNone(loc["longitude"], "Longitude must remain None for unknown locations")

    # 13. Raw latitude/longitude coordinates
    def test_13_raw_coordinates(self):
        state: MarineState = {"query": "Check sea conditions at 12.91, 74.85 today"}
        res = asyncio.run(understand_query_node(state))
        loc = res["location"]
        self.assertIsNotNone(loc)
        self.assertAlmostEqual(loc["latitude"], 12.91, places=2)
        self.assertAlmostEqual(loc["longitude"], 74.85, places=2)
        self.assertEqual(loc["name"], "12.91, 74.85")

    # 14. Tomorrow morning
    def test_14_tomorrow_morning(self):
        state: MarineState = {"query": "Where to catch tuna tomorrow morning near Mangalore?"}
        res = asyncio.run(understand_query_node(state))
        tr = res["time_range"]
        self.assertIsNotNone(tr)
        self.assertEqual(tr["raw"], "tomorrow morning")
        self.assertEqual(tr["relative_day"], "tomorrow")
        self.assertEqual(tr["period"], "morning")
        self.assertFalse(tr["is_historical"])

    # 15. Tonight
    def test_15_tonight(self):
        state: MarineState = {"query": "What's the weather around Mangalore tonight?"}
        res = asyncio.run(understand_query_node(state))
        tr = res["time_range"]
        self.assertIsNotNone(tr)
        self.assertEqual(tr["raw"], "tonight")
        self.assertEqual(tr["period"], "night")

    # 16. Last 30 days
    def test_16_last_30_days(self):
        state: MarineState = {"query": "Show SST around Mangalore for the last 30 days."}
        res = asyncio.run(understand_query_node(state))
        tr = res["time_range"]
        self.assertIsNotNone(tr)
        self.assertEqual(tr["raw"], "last 30 days")
        self.assertTrue(tr["is_historical"])

    # 17. SST extraction
    def test_17_sst_extraction(self):
        state: MarineState = {"query": "Check sea surface temperature near Mangalore"}
        res = asyncio.run(understand_query_node(state))
        self.assertIn(MarineVariable.SST.value, res["variables"])

    # 18. Chlorophyll extraction
    def test_18_chlorophyll_extraction(self):
        state: MarineState = {"query": "Check chlorophyll-a density near Mangalore"}
        res = asyncio.run(understand_query_node(state))
        self.assertIn(MarineVariable.CHLOROPHYLL.value, res["variables"])

    # 19. Multiple variables
    def test_19_multiple_variables(self):
        state: MarineState = {
            "query": "Check SST, chlorophyll, wind speed, wave height, swell, and currents near Mangalore"
        }
        res = asyncio.run(understand_query_node(state))
        vars_extracted = res["variables"]
        self.assertIn(MarineVariable.SST.value, vars_extracted)
        self.assertIn(MarineVariable.CHLOROPHYLL.value, vars_extracted)
        self.assertIn(MarineVariable.WIND.value, vars_extracted)
        self.assertIn(MarineVariable.WAVE.value, vars_extracted)
        self.assertIn(MarineVariable.SWELL.value, vars_extracted)
        self.assertIn(MarineVariable.CURRENT.value, vars_extracted)

    # 20. Missing location (never invented)
    def test_20_missing_location(self):
        state: MarineState = {"query": "Is it safe to go fishing tomorrow morning?"}
        res = asyncio.run(understand_query_node(state))
        self.assertIsNone(res["location"], "Location must remain None when missing from query")

    # 21. Missing time (never invented)
    def test_21_missing_time(self):
        state: MarineState = {"query": "What is the nearest PFZ to Mangalore?"}
        res = asyncio.run(understand_query_node(state))
        self.assertIsNone(res["time_range"], "Time range must remain None when missing from query")

    # 22. Ambiguous query
    def test_22_ambiguous_query(self):
        state: MarineState = {"query": "Tell me something interesting"}
        res = asyncio.run(understand_query_node(state))
        self.assertEqual(res["intent"], MarineIntent.GENERAL_MARINE_QUERY.value)
        self.assertIsNone(res["location"])
        self.assertIsNone(res["time_range"])
        self.assertIn("query_intent", res)
        self.assertEqual(res["query_intent"]["intent"], MarineIntent.GENERAL_MARINE_QUERY.value)

    # 23. Empty / invalid query (does not crash)
    def test_23_empty_and_invalid_query(self):
        invalid_queries = ["", "   ", "???!!!", "!@#$%^&*()", "   \n\t   "]
        for q in invalid_queries:
            with self.subTest(query=q):
                state: MarineState = {"query": q}
                res = asyncio.run(understand_query_node(state))
                self.assertIsNotNone(res)
                self.assertEqual(res["intent"], MarineIntent.GENERAL_MARINE_QUERY.value)
                self.assertIsNone(res["location"])
                self.assertIsNone(res["time_range"])
                self.assertEqual(res["variables"], [])
                self.assertIn("query_intent", res)

    # Planner integration: planner produces valid plans from normalized QueryIntent
    def test_24_planner_integration(self):
        for intent in MarineIntent:
            state: MarineState = {
                "intent": intent.value,
                "location": {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427},
                "variables": ["SST", "WAVE"],
            }
            plan_res = asyncio.run(planner_node(state))
            self.assertIn("plan", plan_res)
            self.assertIsInstance(plan_res["plan"], list)
            self.assertGreater(len(plan_res["plan"]), 0)


if __name__ == "__main__":
    unittest.main()
