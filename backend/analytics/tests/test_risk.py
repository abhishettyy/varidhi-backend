import unittest

from analytics.integration import evaluate_zone
from analytics.tests.fixtures import complete_zone


class RiskTests(unittest.TestCase):
    def test_high_wind_and_wave_raise_risk(self):
        baseline = evaluate_zone("base", complete_zone())
        windy = evaluate_zone("wind", complete_zone(wind=20.0))
        waves = evaluate_zone("wave", complete_zone(wave=5.0))
        self.assertGreater(windy.risk_score, baseline.risk_score)
        self.assertGreater(waves.risk_score, baseline.risk_score)

    def test_precipitation_contributes(self):
        dry = evaluate_zone("dry", complete_zone(precipitation=0.0))
        wet = evaluate_zone("wet", complete_zone(precipitation=0.03))
        self.assertGreater(wet.risk_score, dry.risk_score)

    def test_missing_wind_or_wave_is_not_safe_and_reduces_confidence(self):
        complete = complete_zone()
        full = evaluate_zone("full", complete)
        no_wind = evaluate_zone("no-wind", [item for item in complete if item.variable != "wind_speed"])
        no_wave = evaluate_zone("no-wave", [item for item in complete if item.variable != "significant_wave_height"])
        self.assertLess(no_wind.confidence, full.confidence)
        self.assertLess(no_wave.confidence, full.confidence)
        self.assertEqual(no_wind.classification, "insufficient_evidence")
        self.assertIn("significant_wave_height", no_wave.missing_evidence)
