"""Comprehensive Test Suite for Phase 6A: P6 Opportunity Scoring Engine.

Tests:
1. Perfect/high opportunity inputs (Score = 100.0)
2. Low opportunity inputs (Score = 0.0)
3. Normal Mangalore Zone A scoring
4. Normal Mangalore Zone B scoring
5. Normal Mangalore Zone C scoring
6. Missing Chlorophyll (dynamic weight renormalization)
7. Missing SST (dynamic weight renormalization)
8. Missing PFZ (dynamic weight renormalization)
9. Missing multiple features (e.g. only PFZ available)
10. All features missing / empty input
11. Invalid PFZ confidence handling
12. Invalid distance handling
13. Deterministic repeated calculation
14. Score bounded range invariant [0.0, 100.0]
15. Components and raw features exposure
16. Configurable custom weights
17. Integration with P4 ToolResult dependency dictionaries
18. Scientific disclaimer presence
"""

import unittest
from typing import Any, Dict

from backend.agents.analytics.opportunity import (
    DEFAULT_CHLOROPHYLL_WEIGHT,
    DEFAULT_DISTANCE_WEIGHT,
    DEFAULT_PFZ_WEIGHT,
    DEFAULT_SST_FRONT_WEIGHT,
    MAX_CHLOROPHYLL_MG_M3,
    MAX_OPERATIONAL_DISTANCE_NM,
    MAX_SST_GRADIENT_DELTA_C,
    calculate_opportunity_from_p4_results,
    calculate_opportunity_tool_entrypoint,
    calculate_zone_opportunity,
    normalize_chlorophyll,
    normalize_distance,
    normalize_pfz_confidence,
    normalize_sst_gradient,
    parse_numeric_gradient,
)
from backend.agents.analytics.schemas import (
    OpportunityAnalysisResult,
    OpportunityComponents,
    OpportunityWeights,
    RawOpportunityFeatures,
    ZoneOpportunityScore,
)
from backend.agents.tools.adapters.ocean_adapter import SyntheticOceanAdapter
from backend.agents.tools.adapters.pfz_adapter import SyntheticPFZAdapter


class TestPhase6AOpportunityEngine(unittest.TestCase):
    """Test suite for P6 Opportunity Scoring Engine."""

    def setUp(self):
        self.location = {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}
        self.pfz_adapter = SyntheticPFZAdapter()
        self.ocean_adapter = SyntheticOceanAdapter()

    # 1. Perfect / maximum opportunity inputs
    def test_01_perfect_opportunity_inputs(self):
        raw = RawOpportunityFeatures(
            zone_id="PERFECT_ZONE",
            pfz_confidence=1.0,
            sst_gradient_delta=1.2,
            chlorophyll_a_mg_m3=4.0,
            distance_nm=0.0,
        )
        res = calculate_zone_opportunity("PERFECT_ZONE", raw)
        self.assertEqual(res.opportunity_score, 100.0)
        self.assertEqual(res.convergence_grade, "High")
        self.assertEqual(res.components.pfz, 100.0)
        self.assertEqual(res.components.sst_front, 100.0)
        self.assertEqual(res.components.chlorophyll, 100.0)
        self.assertEqual(res.components.distance, 100.0)
        self.assertEqual(len(res.missing_features), 0)

    # 2. Low / zero opportunity inputs
    def test_02_low_opportunity_inputs(self):
        raw = RawOpportunityFeatures(
            zone_id="POOR_ZONE",
            pfz_confidence=0.0,
            sst_gradient_delta=0.0,
            chlorophyll_a_mg_m3=0.0,
            distance_nm=30.0,  # Max distance => 0 proximity score
        )
        res = calculate_zone_opportunity("POOR_ZONE", raw)
        self.assertEqual(res.opportunity_score, 0.0)
        self.assertEqual(res.convergence_grade, "Low")
        self.assertEqual(res.components.pfz, 0.0)
        self.assertEqual(res.components.sst_front, 0.0)
        self.assertEqual(res.components.chlorophyll, 0.0)
        self.assertEqual(res.components.distance, 0.0)

    # 3. Normal Mangalore Zone A
    def test_03_mangalore_zone_a_scoring(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_A",
            pfz_confidence=0.88,
            sst_gradient_delta=0.9,
            chlorophyll_a_mg_m3=2.8,
            distance_nm=14.5,
        )
        res = calculate_zone_opportunity("ZONE_A", raw)
        # Expected:
        # PFZ: 88.0 * 0.40 = 35.2
        # SST: (0.9/1.2)*100 = 75.0 * 0.25 = 18.75
        # Chl: (2.8/4.0)*100 = 70.0 * 0.25 = 17.5
        # Dist: (1 - 14.5/30)*100 = 51.67 * 0.10 = 5.167
        # Total = 35.2 + 18.75 + 17.5 + 5.167 = 76.617 -> 76.6
        self.assertAlmostEqual(res.opportunity_score, 76.6, places=1)
        self.assertEqual(res.convergence_grade, "Moderate-High")
        self.assertIn("strong PFZ advisory confidence (0.88)", res.explanation_factors)
        self.assertIn("strong thermal-front gradient (0.9°C delta)", res.explanation_factors)

    # 4. Normal Mangalore Zone B
    def test_04_mangalore_zone_b_scoring(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_B",
            pfz_confidence=0.82,
            sst_gradient_delta=0.6,
            chlorophyll_a_mg_m3=2.3,
            distance_nm=8.2,
        )
        res = calculate_zone_opportunity("ZONE_B", raw)
        # Expected:
        # PFZ: 82.0 * 0.40 = 32.8
        # SST: (0.6/1.2)*100 = 50.0 * 0.25 = 12.5
        # Chl: (2.3/4.0)*100 = 57.5 * 0.25 = 14.375
        # Dist: (1 - 8.2/30)*100 = 72.67 * 0.10 = 7.267
        # Total = 32.8 + 12.5 + 14.375 + 7.267 = 66.942 -> 66.9
        self.assertAlmostEqual(res.opportunity_score, 66.9, places=1)
        self.assertEqual(res.convergence_grade, "Moderate")
        self.assertIn("good PFZ advisory confidence (0.82)", res.explanation_factors)
        self.assertIn("favorable proximity (8.2 NM)", res.explanation_factors)

    # 5. Normal Mangalore Zone C
    def test_05_mangalore_zone_c_scoring(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_C",
            pfz_confidence=0.94,
            sst_gradient_delta=1.1,
            chlorophyll_a_mg_m3=3.2,
            distance_nm=18.0,
        )
        res = calculate_zone_opportunity("ZONE_C", raw)
        # Expected:
        # PFZ: 94.0 * 0.40 = 37.6
        # SST: (1.1/1.2)*100 = 91.67 * 0.25 = 22.917
        # Chl: (3.2/4.0)*100 = 80.0 * 0.25 = 20.0
        # Dist: (1 - 18.0/30)*100 = 40.0 * 0.10 = 4.0
        # Total = 37.6 + 22.917 + 20.0 + 4.0 = 84.517 -> 84.5
        self.assertAlmostEqual(res.opportunity_score, 84.5, places=1)
        self.assertIn("strong PFZ advisory confidence (0.94)", res.explanation_factors)
        self.assertIn("high chlorophyll-a concentration (3.2 mg/m³)", res.explanation_factors)

    # 6. Missing Chlorophyll (Dynamic weight renormalization)
    def test_06_missing_chlorophyll_renormalization(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_NO_CHL",
            pfz_confidence=0.80,         # 80.0
            sst_gradient_delta=0.6,     # 50.0
            chlorophyll_a_mg_m3=None,   # Missing
            distance_nm=15.0,           # 50.0
        )
        res = calculate_zone_opportunity("ZONE_NO_CHL", raw)
        self.assertIn("chlorophyll", res.missing_features)
        self.assertIsNone(res.components.chlorophyll)
        
        # Base weights: PFZ 0.40, SST 0.25, Dist 0.10 -> Total active = 0.75
        # Renormalized:
        # PFZ: 0.40 / 0.75 = 0.5333
        # SST: 0.25 / 0.75 = 0.3333
        # Dist: 0.10 / 0.75 = 0.1333
        # Score = 0.5333*80 + 0.3333*50 + 0.1333*50 = 42.664 + 16.665 + 6.665 = 65.99 -> 66.0
        self.assertAlmostEqual(res.opportunity_score, 66.0, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 7. Missing SST (Dynamic weight renormalization)
    def test_07_missing_sst_renormalization(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_NO_SST",
            pfz_confidence=0.90,         # 90.0
            sst_gradient_delta=None,    # Missing
            chlorophyll_a_mg_m3=2.0,    # 50.0
            distance_nm=15.0,           # 50.0
        )
        res = calculate_zone_opportunity("ZONE_NO_SST", raw)
        self.assertIn("sst_front", res.missing_features)
        # Active weights: PFZ 0.40, Chl 0.25, Dist 0.10 -> Total 0.75
        # Score = (0.40/0.75)*90 + (0.25/0.75)*50 + (0.10/0.75)*50 = 48.0 + 16.67 + 6.67 = 71.3
        self.assertAlmostEqual(res.opportunity_score, 71.3, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 8. Missing PFZ (Dynamic weight renormalization)
    def test_08_missing_pfz_renormalization(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_NO_PFZ",
            pfz_confidence=None,        # Missing
            sst_gradient_delta=0.9,     # 75.0
            chlorophyll_a_mg_m3=3.0,    # 75.0
            distance_nm=15.0,           # 50.0
        )
        res = calculate_zone_opportunity("ZONE_NO_PFZ", raw)
        self.assertIn("pfz", res.missing_features)
        # Active weights: SST 0.25, Chl 0.25, Dist 0.10 -> Total 0.60
        # Renormalized: SST 0.25/0.6 = 0.4167, Chl 0.25/0.6 = 0.4167, Dist 0.10/0.6 = 0.1667
        # Score = 0.4167*75 + 0.4167*75 + 0.1667*50 = 31.25 + 31.25 + 8.33 = 70.8
        self.assertAlmostEqual(res.opportunity_score, 70.8, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 9. Missing multiple features (Only PFZ available)
    def test_09_missing_multiple_features(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_ONLY_PFZ",
            pfz_confidence=0.85,
            sst_gradient_delta=None,
            chlorophyll_a_mg_m3=None,
            distance_nm=None,
        )
        res = calculate_zone_opportunity("ZONE_ONLY_PFZ", raw)
        self.assertEqual(res.missing_features, ["sst_front", "chlorophyll", "distance"])
        # Renormalized weight for PFZ = 1.0
        self.assertAlmostEqual(res.opportunity_score, 85.0, places=1)
        self.assertEqual(res.weights_used, {"pfz": 1.0})

    # 10. All features missing
    def test_10_all_features_missing(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_EMPTY",
            pfz_confidence=None,
            sst_gradient_delta=None,
            chlorophyll_a_mg_m3=None,
            distance_nm=None,
        )
        res = calculate_zone_opportunity("ZONE_EMPTY", raw)
        self.assertEqual(res.opportunity_score, 0.0)
        self.assertEqual(len(res.missing_features), 4)
        self.assertEqual(res.weights_used, {})

    # 11. Invalid PFZ confidence values
    def test_11_invalid_pfz_confidence(self):
        # Negative confidence clamped to 0
        self.assertEqual(normalize_pfz_confidence(-0.5), 0.0)
        # > 1.0 clamped to 100.0
        self.assertEqual(normalize_pfz_confidence(1.5), 100.0)
        # String float parsed
        self.assertEqual(normalize_pfz_confidence("0.75"), 75.0)
        # Non-numeric string returns None
        self.assertIsNone(normalize_pfz_confidence("invalid_str"))

    # 12. Invalid distance values
    def test_12_invalid_distance(self):
        # Negative distance treated as 0 (full proximity = 100.0)
        self.assertEqual(normalize_distance(-5.0), 100.0)
        # Distance exceeding 30 NM gives 0 score
        self.assertEqual(normalize_distance(45.0), 0.0)
        # String distance parsed
        self.assertEqual(normalize_distance("15.0"), 50.0)
        # Malformed string returns None
        self.assertIsNone(normalize_distance("unknown_nm"))

    # 13. Deterministic repeated calculation
    def test_13_deterministic_repeated_calculation(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_DETERMINISTIC",
            pfz_confidence=0.88,
            sst_gradient_delta=0.9,
            chlorophyll_a_mg_m3=2.8,
            distance_nm=14.5,
        )
        scores = [calculate_zone_opportunity("ZONE_DETERMINISTIC", raw).opportunity_score for _ in range(50)]
        self.assertTrue(all(s == scores[0] for s in scores))

    # 14. Score always remains bounded in [0.0, 100.0]
    def test_14_boundedness_invariant(self):
        test_cases = [
            (0.0, 0.0, 0.0, 100.0),
            (1.0, 5.0, 10.0, -10.0),
            (0.5, 0.6, 2.0, 15.0),
            (0.99, 1.19, 3.99, 0.1),
            (2.0, 2.0, 8.0, 50.0),
        ]
        for pfz, sst, chl, dist in test_cases:
            raw = RawOpportunityFeatures(
                zone_id="TEST_BOUNDS",
                pfz_confidence=pfz,
                sst_gradient_delta=sst,
                chlorophyll_a_mg_m3=chl,
                distance_nm=dist,
            )
            res = calculate_zone_opportunity("TEST_BOUNDS", raw)
            self.assertGreaterEqual(res.opportunity_score, 0.0)
            self.assertLessEqual(res.opportunity_score, 100.0)

    # 15. Components and raw features are exposed
    def test_15_components_and_raw_features_exposed(self):
        raw = RawOpportunityFeatures(
            zone_id="ZONE_A",
            pfz_confidence=0.88,
            sst_gradient_delta=0.9,
            chlorophyll_a_mg_m3=2.8,
            distance_nm=14.5,
            species=["Pelagic Tuna", "Kingfish"],
        )
        res = calculate_zone_opportunity("ZONE_A", raw)
        res_dict = res.to_dict()
        self.assertIn("components", res_dict)
        self.assertIn("raw_features", res_dict)
        self.assertIn("weights_used", res_dict)
        self.assertIn("explanation_factors", res_dict)
        self.assertEqual(res_dict["raw_features"]["species"], ["Pelagic Tuna", "Kingfish"])

    # 16. Configurable custom weights
    def test_16_configurable_custom_weights(self):
        custom_weights = OpportunityWeights(
            pfz=0.50,
            sst_front=0.0,
            chlorophyll=0.0,
            distance=0.50,
        )
        raw = RawOpportunityFeatures(
            zone_id="ZONE_CUSTOM",
            pfz_confidence=0.80,  # 80.0
            distance_nm=15.0,     # 50.0
        )
        res = calculate_zone_opportunity("ZONE_CUSTOM", raw, weights=custom_weights)
        # 0.50 * 80 + 0.50 * 50 = 40 + 25 = 65.0
        self.assertAlmostEqual(res.opportunity_score, 65.0, places=1)

    # 17. Full Multi-Zone P4 ToolResult dependency integration
    def test_17_full_p4_tool_result_integration(self):
        pfz_res = self.pfz_adapter.fetch_pfz(self.location)
        sst_res = self.ocean_adapter.fetch_sst(self.location)
        chl_res = self.ocean_adapter.fetch_chlorophyll(self.location)

        analysis = calculate_opportunity_from_p4_results(
            pfz_result=pfz_res,
            sst_result=sst_res,
            chlorophyll_result=chl_res,
            location=self.location,
        )

        self.assertEqual(analysis.status, "success")
        self.assertEqual(len(analysis.zones), 3)
        zone_ids = [z.zone_id for z in analysis.zones]
        self.assertEqual(zone_ids, ["ZONE_A", "ZONE_B", "ZONE_C"])

        # Natural fixture scores:
        # Zone C has highest opportunity (strong front, highest Chl-a, highest PFZ)
        # Zone A is second highest
        # Zone B is third (moderate front)
        scores_by_id = {z.zone_id: z.opportunity_score for z in analysis.zones}
        self.assertGreater(scores_by_id["ZONE_C"], scores_by_id["ZONE_A"])
        self.assertGreater(scores_by_id["ZONE_A"], scores_by_id["ZONE_B"])
        self.assertEqual(analysis.best_opportunity_zone_id, "ZONE_C")

        # Verify tool entrypoint compatibility
        tool_output = calculate_opportunity_tool_entrypoint(
            parameters={"location": self.location},
            dependencies={"pfz": pfz_res, "sst": sst_res, "chlorophyll": chl_res},
        )
        self.assertEqual(tool_output["status"], "success")
        self.assertEqual(tool_output["source"], "P6_ANALYTICS_OPPORTUNITY")
        self.assertTrue(tool_output["data"]["opportunity_evaluated"])
        self.assertEqual(len(tool_output["data"]["scored_zones"]), 3)

    # 18. Scientific Disclaimer Presence
    def test_18_scientific_disclaimer_presence(self):
        analysis = calculate_opportunity_from_p4_results()
        self.assertIn("heuristic", analysis.disclaimer.lower())
        self.assertIn("not a validated probability", analysis.disclaimer.lower())


if __name__ == "__main__":
    unittest.main()
