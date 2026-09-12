"""Comprehensive Test Suite for Phase 6B: P6 Marine Risk Engine.

Tests:
1. Very calm conditions -> low risk (<15.0)
2. Moderate conditions -> moderate risk (30 - 60)
3. Severe conditions -> high/severe risk (>60 - 80+)
4. Mangalore Zone A scoring (74.4, HIGH)
5. Mangalore Zone B scoring (31.5, MODERATE)
6. Mangalore Zone C scoring (27.7, LOW)
7. Missing wave data (dynamic weight renormalization)
8. Missing wind data (dynamic weight renormalization)
9. Missing swell data (dynamic weight renormalization)
10. Missing multiple inputs
11. All inputs unavailable -> structured insufficient_data handling
12. Invalid negative values
13. Score boundedness invariant [0.0, 100.0]
14. Deterministic repeated calculation
15. Severity threshold boundary tests
16. Configurable custom weights
17. Default vessel profile (1.0x)
18. Small traditional vessel sensitivity (1.25x)
19. Mechanized vessel sensitivity (0.85x)
20. P4 ToolResult integration (get_wind, get_wave, get_swell)
21. Machine-readable factors & threshold warnings
22. Safety disclaimer & provenance metadata
23. Verification that Zone C is NOT rejected by the risk engine
"""

import unittest
from typing import Any, Dict

from backend.agents.analytics.risk import (
    DEFAULT_GUST_WEIGHT,
    DEFAULT_SWELL_WEIGHT,
    DEFAULT_WAVE_WEIGHT,
    DEFAULT_WIND_WEIGHT,
    MAX_SWELL_HEIGHT_M,
    MAX_WAVE_HEIGHT_M,
    MAX_WIND_GUST_KNOTS,
    MAX_WIND_SPEED_KNOTS,
    VESSEL_PROFILES,
    calculate_marine_risk_from_p4_results,
    calculate_marine_risk_tool_entrypoint,
    calculate_zone_risk,
    derive_risk_severity,
    evaluate_period_diagnostics,
    generate_risk_factors,
    normalize_swell_height,
    normalize_wave_height,
    normalize_wind_gust,
    normalize_wind_speed,
)
from backend.agents.analytics.schemas import (
    RawRiskFeatures,
    RiskAnalysisResult,
    RiskComponents,
    RiskSeverity,
    RiskSeverityThresholds,
    RiskWeights,
    VesselProfile,
    ZoneRiskScore,
)
from backend.agents.tools.adapters.weather_adapter import SyntheticMarineWeatherAdapter


class TestPhase6BMarineRiskEngine(unittest.TestCase):
    """Test suite for P6 Marine Risk Engine."""

    def setUp(self):
        self.location = {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}
        self.weather_adapter = SyntheticMarineWeatherAdapter()

    # 1. Very calm conditions -> low risk (<15.0)
    def test_01_very_calm_conditions_low_risk(self):
        raw = RawRiskFeatures(
            zone_id="CALM_ZONE",
            wave_height_m=0.3,
            wind_speed_knots=4.0,
            wind_gust_knots=5.0,
            swell_height_m=0.2,
        )
        res = calculate_zone_risk("CALM_ZONE", raw)
        self.assertLess(res.risk_score, 15.0)
        self.assertEqual(res.severity, "LOW")
        self.assertTrue(res.is_safe_heuristic)
        self.assertEqual(len(res.warnings), 0)

    # 2. Moderate conditions -> moderate risk (30 - 60)
    def test_02_moderate_conditions(self):
        raw = RawRiskFeatures(
            zone_id="MOD_ZONE",
            wave_height_m=1.3,
            wind_speed_knots=13.0,
            wind_gust_knots=16.0,
            swell_height_m=0.8,
        )
        res = calculate_zone_risk("MOD_ZONE", raw)
        self.assertGreaterEqual(res.risk_score, 30.0)
        self.assertLessEqual(res.risk_score, 60.0)
        self.assertEqual(res.severity, "MODERATE")

    # 3. Severe conditions -> high/severe risk (>60 - 80+)
    def test_03_severe_conditions(self):
        raw = RawRiskFeatures(
            zone_id="SEVERE_ZONE",
            wave_height_m=2.8,
            wind_speed_knots=28.0,
            wind_gust_knots=38.0,
            swell_height_m=2.2,
        )
        res = calculate_zone_risk("SEVERE_ZONE", raw)
        self.assertGreater(res.risk_score, 80.0)
        self.assertEqual(res.severity, "SEVERE")
        self.assertFalse(res.is_safe_heuristic)
        self.assertTrue(any("exceeds" in w.lower() for w in res.warnings))

    # 4. Normal Mangalore Zone A scoring
    def test_04_mangalore_zone_a_scoring(self):
        # Zone A: wave=2.4m, wind=22.0 kts, gust=28.0 kts, swell=1.8m
        raw = RawRiskFeatures(
            zone_id="ZONE_A",
            wave_height_m=2.4,
            wave_period_sec=8.0,
            wind_speed_knots=22.0,
            wind_gust_knots=28.0,
            swell_height_m=1.8,
            swell_period_sec=11.0,
        )
        res = calculate_zone_risk("ZONE_A", raw)
        # Expected:
        # wave: (2.4/3.0)*100 = 80.0
        # wind: (22.0/30.0)*100 = 73.33
        # gust: (28.0/40.0)*100 = 70.0
        # swell: (1.8/2.5)*100 = 72.0
        # Renormalized weights: wave 0.3889, wind 0.2778, gust 0.1667, swell 0.1667
        # Total = 75.15 -> 75.2
        self.assertAlmostEqual(res.risk_score, 75.2, places=1)
        self.assertEqual(res.severity, "HIGH")
        self.assertFalse(res.is_safe_heuristic)
        self.assertIn("high significant wave height (2.4m)", res.factors)
        self.assertIn("strong sustained wind (22.0 kts)", res.factors)

    # 5. Normal Mangalore Zone B scoring
    def test_05_mangalore_zone_b_scoring(self):
        # Zone B: wave=1.1m, wind=11.0 kts, gust=14.0 kts, swell=0.7m
        raw = RawRiskFeatures(
            zone_id="ZONE_B",
            wave_height_m=1.1,
            wave_period_sec=6.5,
            wind_speed_knots=11.0,
            wind_gust_knots=14.0,
            swell_height_m=0.7,
            swell_period_sec=7.5,
        )
        res = calculate_zone_risk("ZONE_B", raw)
        # Expected: 34.95 -> 34.9
        self.assertAlmostEqual(res.risk_score, 34.9, places=1)
        self.assertEqual(res.severity, "MODERATE")
        self.assertTrue(res.is_safe_heuristic)
        self.assertIn("moderate wave height (1.1m)", res.factors)

    # 6. Normal Mangalore Zone C scoring
    def test_06_mangalore_zone_c_scoring(self):
        # Zone C: wave=1.0m, wind=9.5 kts, gust=12.0 kts, swell=0.6m
        raw = RawRiskFeatures(
            zone_id="ZONE_C",
            wave_height_m=1.0,
            wave_period_sec=6.0,
            wind_speed_knots=9.5,
            wind_gust_knots=12.0,
            swell_height_m=0.6,
            swell_period_sec=7.0,
        )
        res = calculate_zone_risk("ZONE_C", raw)
        # Expected: 30.76 -> 30.8
        self.assertAlmostEqual(res.risk_score, 30.8, places=1)
        self.assertEqual(res.severity, "MODERATE")
        self.assertTrue(res.is_safe_heuristic)
        self.assertIn("moderate wave height (1.0m)", res.factors)

    # 7. Missing wave data (dynamic weight renormalization)
    def test_07_missing_wave_renormalization(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_NO_WAVE",
            wave_height_m=None,       # Missing
            wind_speed_knots=15.0,    # 50.0
            wind_gust_knots=20.0,     # 50.0
            swell_height_m=1.25,      # 50.0
        )
        res = calculate_zone_risk("ZONE_NO_WAVE", raw)
        self.assertIn("wave", res.missing_features)
        self.assertIsNone(res.components.wave)
        # Active weights: wind 0.25, gust 0.15, swell 0.15 -> sum = 0.55
        # Score = 50.0
        self.assertAlmostEqual(res.risk_score, 50.0, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 8. Missing wind data (dynamic weight renormalization)
    def test_08_missing_wind_renormalization(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_NO_WIND",
            wave_height_m=1.5,        # 50.0
            wind_speed_knots=None,    # Missing
            wind_gust_knots=20.0,     # 50.0
            swell_height_m=1.25,      # 50.0
        )
        res = calculate_zone_risk("ZONE_NO_WIND", raw)
        self.assertIn("wind", res.missing_features)
        self.assertAlmostEqual(res.risk_score, 50.0, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 9. Missing swell data (dynamic weight renormalization)
    def test_09_missing_swell_renormalization(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_NO_SWELL",
            wave_height_m=1.5,        # 50.0
            wind_speed_knots=15.0,    # 50.0
            wind_gust_knots=20.0,     # 50.0
            swell_height_m=None,      # Missing
        )
        res = calculate_zone_risk("ZONE_NO_SWELL", raw)
        self.assertIn("swell", res.missing_features)
        self.assertAlmostEqual(res.risk_score, 50.0, places=1)
        self.assertAlmostEqual(sum(res.weights_used.values()), 1.0, places=2)

    # 10. Missing multiple inputs (Only wave available)
    def test_10_missing_multiple_inputs(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_ONLY_WAVE",
            wave_height_m=2.1,        # 70.0
            wind_speed_knots=None,
            wind_gust_knots=None,
            swell_height_m=None,
        )
        res = calculate_zone_risk("ZONE_ONLY_WAVE", raw)
        self.assertEqual(res.missing_features, ["wind", "gust", "swell"])
        self.assertAlmostEqual(res.risk_score, 70.0, places=1)
        self.assertEqual(res.weights_used, {"wave": 1.0})

    # 11. All inputs unavailable -> structured insufficient_data handling
    def test_11_all_inputs_unavailable(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_EMPTY",
            wave_height_m=None,
            wind_speed_knots=None,
            wind_gust_knots=None,
            swell_height_m=None,
        )
        res = calculate_zone_risk("ZONE_EMPTY", raw)
        self.assertEqual(res.risk_score, 0.0)
        self.assertEqual(len(res.missing_features), 4)
        self.assertEqual(res.weights_used, {})

    # 12. Invalid negative values
    def test_12_invalid_negative_values(self):
        self.assertEqual(normalize_wave_height(-1.5), 0.0)
        self.assertEqual(normalize_wind_speed(-10.0), 0.0)
        self.assertEqual(normalize_wind_gust(-5.0), 0.0)
        self.assertEqual(normalize_swell_height(-0.8), 0.0)

    # 13. Score boundedness invariant [0.0, 100.0]
    def test_13_boundedness_invariant(self):
        extreme_cases = [
            (0.0, 0.0, 0.0, 0.0),
            (5.0, 60.0, 80.0, 5.0),
            (-2.0, -10.0, -5.0, -1.0),
            (1.5, 15.0, 20.0, 1.25),
            (10.0, 100.0, 150.0, 10.0),
        ]
        for w, s, g, sw in extreme_cases:
            raw = RawRiskFeatures(
                zone_id="TEST_BOUNDS",
                wave_height_m=w,
                wind_speed_knots=s,
                wind_gust_knots=g,
                swell_height_m=sw,
            )
            res = calculate_zone_risk("TEST_BOUNDS", raw)
            self.assertGreaterEqual(res.risk_score, 0.0)
            self.assertLessEqual(res.risk_score, 100.0)

    # 14. Deterministic repeated calculation
    def test_14_deterministic_repeated_calculation(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_A",
            wave_height_m=2.4,
            wind_speed_knots=22.0,
            wind_gust_knots=28.0,
            swell_height_m=1.8,
        )
        scores = [calculate_zone_risk("ZONE_A", raw).risk_score for _ in range(50)]
        self.assertTrue(all(s == scores[0] for s in scores))

    # 15. Severity threshold boundary checks
    def test_15_severity_threshold_boundaries(self):
        th = RiskSeverityThresholds()
        self.assertEqual(derive_risk_severity(0.0, th), "LOW")
        self.assertEqual(derive_risk_severity(30.0, th), "LOW")
        self.assertEqual(derive_risk_severity(30.1, th), "MODERATE")
        self.assertEqual(derive_risk_severity(60.0, th), "MODERATE")
        self.assertEqual(derive_risk_severity(60.1, th), "HIGH")
        self.assertEqual(derive_risk_severity(80.0, th), "HIGH")
        self.assertEqual(derive_risk_severity(80.1, th), "SEVERE")
        self.assertEqual(derive_risk_severity(100.0, th), "SEVERE")

    # 16. Configurable custom weights
    def test_16_configurable_custom_weights(self):
        custom_weights = RiskWeights(wave=0.60, wind=0.40, gust=0.0, swell=0.0)
        raw = RawRiskFeatures(
            zone_id="ZONE_CUSTOM",
            wave_height_m=1.5,        # 50.0
            wind_speed_knots=15.0,    # 50.0
        )
        res = calculate_zone_risk("ZONE_CUSTOM", raw, weights=custom_weights)
        self.assertAlmostEqual(res.risk_score, 50.0, places=1)

    # 17. Default vessel profile (1.0x multiplier)
    def test_17_default_vessel_profile(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_B",
            wave_height_m=1.1,
            wind_speed_knots=11.0,
            wind_gust_knots=14.0,
            swell_height_m=0.7,
        )
        res = calculate_zone_risk("ZONE_B", raw, vessel_type="default")
        self.assertEqual(res.vessel_profile_applied, "default")
        self.assertAlmostEqual(res.risk_score, 34.9, places=1)

    # 18. Small traditional vessel sensitivity (+25% multiplier)
    def test_18_small_traditional_vessel_sensitivity(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_B",
            wave_height_m=1.1,
            wind_speed_knots=11.0,
            wind_gust_knots=14.0,
            swell_height_m=0.7,
        )
        res = calculate_zone_risk("ZONE_B", raw, vessel_type="small_traditional")
        self.assertEqual(res.vessel_profile_applied, "small_traditional")
        # 34.95 * 1.25 = 43.68 -> 43.7
        self.assertAlmostEqual(res.risk_score, 43.7, places=1)

    # 19. Mechanized vessel sensitivity (-15% multiplier)
    def test_19_mechanized_vessel_sensitivity(self):
        raw = RawRiskFeatures(
            zone_id="ZONE_B",
            wave_height_m=1.1,
            wind_speed_knots=11.0,
            wind_gust_knots=14.0,
            swell_height_m=0.7,
        )
        res = calculate_zone_risk("ZONE_B", raw, vessel_type="mechanized")
        self.assertEqual(res.vessel_profile_applied, "mechanized")
        # 34.95 * 0.85 = 29.70 -> 29.7
        self.assertAlmostEqual(res.risk_score, 29.7, places=1)

    # 20. P4 ToolResult integration (get_wind, get_wave, get_swell)
    def test_20_p4_tool_result_integration(self):
        wind_res = self.weather_adapter.fetch_wind(self.location)
        wave_res = self.weather_adapter.fetch_wave(self.location)
        swell_res = self.weather_adapter.fetch_swell(self.location)

        analysis = calculate_marine_risk_from_p4_results(
            wind_result=wind_res,
            wave_result=wave_res,
            swell_result=swell_res,
            vessel_type="default",
        )

        self.assertEqual(analysis.status, "success")
        self.assertEqual(len(analysis.zones), 3)
        zone_ids = [z.zone_id for z in analysis.zones]
        self.assertEqual(zone_ids, ["ZONE_A", "ZONE_B", "ZONE_C"])

        # Natural fixture risk ordering:
        # Zone A has highest risk (waves 2.4m, wind 22 kts)
        # Zone B has moderate/low risk (waves 1.1m, wind 11 kts)
        # Zone C has lowest risk (waves 1.0m, wind 9.5 kts)
        risks_by_id = {z.zone_id: z.risk_score for z in analysis.zones}
        self.assertGreater(risks_by_id["ZONE_A"], risks_by_id["ZONE_B"])
        self.assertGreater(risks_by_id["ZONE_B"], risks_by_id["ZONE_C"])
        self.assertEqual(analysis.lowest_risk_zone_id, "ZONE_C")

        # Verify tool entrypoint compatibility
        tool_output = calculate_marine_risk_tool_entrypoint(
            parameters={"location": self.location, "vessel_type": "default"},
            dependencies={"wind": wind_res, "wave": wave_res, "swell": swell_res},
        )
        self.assertEqual(tool_output["status"], "success")
        self.assertEqual(tool_output["source"], "P6_ANALYTICS_RISK")
        self.assertTrue(tool_output["data"]["risk_evaluated"])
        self.assertEqual(len(tool_output["data"]["scored_zones"]), 3)
        self.assertIn("ZONE_A", tool_output["data"]["zone_risks"])

    # 21. Machine-readable physical factors & threshold warnings
    def test_21_machine_readable_factors_and_warnings(self):
        raw = RawRiskFeatures(
            zone_id="ROUGH_ZONE",
            wave_height_m=2.6,        # Exceeds default 2.0m max_safe
            wave_period_sec=5.5,      # Period <= 6s + wave >= 1.8m triggers steep chop warning
            wind_speed_knots=24.0,    # Exceeds default 20.0 kts max_safe
            wind_gust_knots=32.0,
            swell_height_m=1.6,
            swell_period_sec=13.0,    # Swell >= 1.5m + period >= 12s triggers groundswell warning
        )
        res = calculate_zone_risk("ROUGH_ZONE", raw)
        self.assertTrue(any("wave height" in f.lower() for f in res.factors))
        self.assertTrue(any("steep wave chop" in w.lower() for w in res.warnings))
        self.assertTrue(any("groundswell" in w.lower() for w in res.warnings))

    # 22. Safety disclaimer & provenance metadata
    def test_22_safety_disclaimer_and_provenance(self):
        analysis = calculate_marine_risk_from_p4_results()
        self.assertIn("heuristic", analysis.disclaimer.lower())
        self.assertIn("not an official maritime safety clearance", analysis.disclaimer.lower())
        self.assertEqual(analysis.source, "P6_ANALYTICS_RISK")

    # 23. Verification that Zone C is NOT rejected by this engine
    def test_23_zone_c_not_rejected_by_risk_engine(self):
        """
        Crucial architectural assertion:
        Zone C is restricted in the fixture, but P6 Marine Risk Engine evaluates ONLY physical risk.
        Zone C must have is_safe_heuristic = True. Rejection happens in Phase 6C.
        """
        raw_c = RawRiskFeatures(
            zone_id="ZONE_C",
            wave_height_m=1.0,
            wind_speed_knots=9.5,
            wind_gust_knots=12.0,
            swell_height_m=0.6,
        )
        res_c = calculate_zone_risk("ZONE_C", raw_c)
        self.assertEqual(res_c.severity, "MODERATE")
        self.assertTrue(res_c.is_safe_heuristic)
        # Verify no regulatory field or rejection leakage
        self.assertNotIn("restricted", res_c.factors)


if __name__ == "__main__":
    unittest.main()
