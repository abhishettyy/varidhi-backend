import unittest

from analytics.integration import evaluate_zone
from analytics.ranking import rank_zones
from analytics.tests.fixtures import complete_zone


class RankingTests(unittest.TestCase):
    def test_multiple_zone_ranking(self):
        better = evaluate_zone("better", complete_zone())
        worse = evaluate_zone("worse", complete_zone(wind=20.0, wave=5.0))
        self.assertEqual(rank_zones([worse, better])[0].zone_id, "better")

    def test_deterministic_tie_breaking(self):
        zone_b = evaluate_zone("b", complete_zone())
        zone_a = evaluate_zone("a", complete_zone())
        self.assertEqual([zone.zone_id for zone in rank_zones([zone_b, zone_a])], ["a", "b"])
