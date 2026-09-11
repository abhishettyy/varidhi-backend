import math
import unittest

from analytics.integration import evaluate_zone
from analytics.opportunity import calculate_opportunity_score
from analytics.tests.fixtures import complete_zone, observation


class OpportunityTests(unittest.TestCase):
    def test_preferred_sst_band_saturates_provisional_partial_score(self):
        result = evaluate_zone("preferred-band", complete_zone(sst=28.8))
        self.assertEqual(result.partial_environmental_opportunity_score, 100.0)

    def test_favorable_and_unfavorable_sst(self):
        favorable = evaluate_zone("a", complete_zone(sst=28.0))
        unfavorable = evaluate_zone("b", complete_zone(sst=19.0))
        self.assertGreater(
            favorable.partial_environmental_opportunity_score,
            unfavorable.partial_environmental_opportunity_score,
        )

    def test_missing_chlorophyll_and_pfz_reduce_confidence(self):
        result = calculate_opportunity_score(sea_surface_temperature=None)
        self.assertIn("chlorophyll_a", result.missing_evidence)
        self.assertIn("pfz_score", result.missing_evidence)
        partial = evaluate_zone("partial", complete_zone())
        self.assertIn("chlorophyll_a", partial.missing_evidence)
        self.assertIn("pfz_score", partial.missing_evidence)
        self.assertLess(partial.confidence, 1.0)

    def test_no_nan_propagation_and_reasons_evidence_present(self):
        observations = complete_zone()
        observations[0] = observation("sea_surface_temperature", math.nan, "degC")
        result = evaluate_zone("nan", observations)
        self.assertTrue(math.isfinite(result.final_score))
        self.assertTrue(result.reasons)
        self.assertTrue(result.evidence)
