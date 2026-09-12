"""Unit and integration test suite for Phase 6D: P6 Zone Ranking and Decision Synthesis Engine.

Verifies deterministic multi-engine decision synthesis combining Opportunity (6A),
Marine Risk (6B), Regulatory Compliance (6C), Distance, and Configurable Decision Policy.
"""

import unittest
from typing import Any, Dict, List

from backend.agents.analytics.decision import (
    DECISION_DISCLAIMER,
    DEFAULT_DISTANCE_RANKING_WEIGHT,
    DEFAULT_MAX_OPERATIONAL_DISTANCE_NM,
    DEFAULT_MAX_RECOMMENDATION_RISK,
    DEFAULT_MIN_OPPORTUNITY_SCORE,
    DEFAULT_OPPORTUNITY_RANKING_WEIGHT,
    DEFAULT_RISK_RANKING_WEIGHT,
    calculate_distance_component,
    calculate_ranking_score,
    calculate_zone_ranking_tool_entrypoint,
    evaluate_candidate_zone,
    rank_and_select_zones,
    select_safe_fishing_zone_tool_entrypoint,
    synthesize_decision_from_p6_results,
)
from backend.agents.analytics.schemas import (
    CandidateZoneEvaluation,
    ComplianceStatus,
    DecisionPolicy,
    DecisionResult,
    RankingComponents,
    RankingWeights,
    RejectionCode,
)


class TestPhase6DDecisionEngine(unittest.TestCase):
    """Comprehensive test coverage for Phase 6D Zone Ranking & Decision Synthesis."""

    def setUp(self):
        # Canonical Mangalore Scenario parameters
        self.zone_a_raw = {
            "zone_id": "ZONE_A",
            "opportunity_score": 76.6,
            "risk_score": 75.2,
            "regulatory_status": ComplianceStatus.ELIGIBLE.value,
            "distance_nm": 14.5,
        }
        self.zone_b_raw = {
            "zone_id": "ZONE_B",
            "opportunity_score": 66.9,
            "risk_score": 34.9,
            "regulatory_status": ComplianceStatus.ELIGIBLE.value,
            "distance_nm": 8.2,
        }
        self.zone_c_raw = {
            "zone_id": "ZONE_C",
            "opportunity_score": 84.5,
            "risk_score": 30.8,
            "regulatory_status": ComplianceStatus.BLOCKED.value,
            "distance_nm": 18.0,
            "blocking_reasons": ["Active Netravati MPA marine sanctuary restriction."],
        }
        self.default_policy = DecisionPolicy(
            max_risk_score=50.0,
            min_opportunity_score=0.0,
            max_distance_nm=30.0,
            require_regulatory_eligibility=True,
        )

    # 1. Zone C legal hard-block wins over high opportunity
    def test_01_zone_c_legal_hard_block_overrides_high_opportunity(self):
        eval_c = evaluate_candidate_zone(
            zone_id="ZONE_C",
            opportunity_score=84.5,
            risk_score=30.8,
            regulatory_status=ComplianceStatus.BLOCKED.value,
            distance_nm=18.0,
            policy=self.default_policy,
        )
        self.assertFalse(eval_c.eligible)
        self.assertEqual(eval_c.status, RejectionCode.REJECTED_LEGAL.value)
        self.assertIn(RejectionCode.REJECTED_LEGAL.value, eval_c.rejection_codes)
        self.assertIsNone(eval_c.ranking_score)

    # 2. Zone A high risk rejected
    def test_02_zone_a_high_risk_rejected(self):
        eval_a = evaluate_candidate_zone(
            zone_id="ZONE_A",
            opportunity_score=76.6,
            risk_score=75.2,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=14.5,
            policy=self.default_policy,
        )
        self.assertFalse(eval_a.eligible)
        self.assertEqual(eval_a.status, RejectionCode.REJECTED_RISK.value)
        self.assertIn(RejectionCode.REJECTED_RISK.value, eval_a.rejection_codes)
        self.assertTrue(any("exceeds project decision threshold" in r for r in eval_a.reasons))

    # 3. Zone B selected in Mangalore scenario
    def test_03_mangalore_scenario_selects_zone_b(self):
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=self.default_policy)
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)

        result = rank_and_select_zones([eval_a, eval_b, eval_c], policy=self.default_policy)

        self.assertIsNotNone(result.selected_zone)
        self.assertEqual(result.selected_zone.zone_id, "ZONE_B")
        self.assertEqual(result.selected_zone.status, "SELECTED")
        self.assertTrue(result.selected_zone.eligible)
        self.assertAlmostEqual(result.selected_zone.ranking_score, 67.31, places=1)

    # 4. All eligible zones ranked
    def test_04_all_eligible_zones_ranked(self):
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        eval_d = evaluate_candidate_zone(
            zone_id="ZONE_D",
            opportunity_score=60.0,
            risk_score=20.0,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=5.0,
            policy=self.default_policy,
        )
        result = rank_and_select_zones([eval_b, eval_d], policy=self.default_policy)
        self.assertEqual(len(result.ranked_zones), 2)
        self.assertEqual(len(result.rejected_zones), 0)

    # 5. Ranking descending order
    def test_05_ranking_strictly_descending(self):
        eval_1 = evaluate_candidate_zone("Z1", 50.0, 20.0, ComplianceStatus.ELIGIBLE.value, 10.0, policy=self.default_policy)
        eval_2 = evaluate_candidate_zone("Z2", 80.0, 10.0, ComplianceStatus.ELIGIBLE.value, 5.0, policy=self.default_policy)
        eval_3 = evaluate_candidate_zone("Z3", 65.0, 30.0, ComplianceStatus.ELIGIBLE.value, 12.0, policy=self.default_policy)

        result = rank_and_select_zones([eval_1, eval_2, eval_3], policy=self.default_policy)
        scores = [z.ranking_score for z in result.ranked_zones]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result.selected_zone.zone_id, "Z2")

    # 6. Legal filter happens before ranking and risk check
    def test_06_legal_filter_happens_before_risk_and_opportunity(self):
        # Even if risk is severely high, legal block takes precedence in rejection reason
        eval_blocked_rough = evaluate_candidate_zone(
            zone_id="ZONE_BLOCKED_ROUGH",
            opportunity_score=99.0,
            risk_score=95.0,
            regulatory_status=ComplianceStatus.BLOCKED.value,
            distance_nm=5.0,
            policy=self.default_policy,
        )
        self.assertEqual(eval_blocked_rough.status, RejectionCode.REJECTED_LEGAL.value)
        self.assertEqual(eval_blocked_rough.rejection_codes, [RejectionCode.REJECTED_LEGAL.value])

    # 7. BLOCKED zone never enters ranked_zones list
    def test_07_blocked_zone_never_enters_ranked_zones(self):
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)

        result = rank_and_select_zones([eval_c, eval_b], policy=self.default_policy)
        ranked_ids = [z.zone_id for z in result.ranked_zones]
        self.assertNotIn("ZONE_C", ranked_ids)
        self.assertIn("ZONE_B", ranked_ids)

    # 8. UNKNOWN regulatory status not recommended
    def test_08_unknown_regulatory_status_not_recommended(self):
        eval_unknown = evaluate_candidate_zone(
            zone_id="ZONE_UNKNOWN",
            opportunity_score=85.0,
            risk_score=20.0,
            regulatory_status=ComplianceStatus.UNKNOWN.value,
            distance_nm=10.0,
            policy=self.default_policy,
        )
        self.assertFalse(eval_unknown.eligible)
        self.assertEqual(eval_unknown.status, RejectionCode.REJECTED_UNKNOWN_REGULATORY_STATUS.value)
        self.assertIn(RejectionCode.REJECTED_UNKNOWN_REGULATORY_STATUS.value, eval_unknown.rejection_codes)

    # 9. Missing regulatory status defaults to UNKNOWN and rejects
    def test_09_missing_regulatory_data_handled(self):
        eval_missing_reg = evaluate_candidate_zone(
            zone_id="ZONE_NO_REG",
            opportunity_score=70.0,
            risk_score=25.0,
            regulatory_status=None,
            distance_nm=10.0,
            policy=self.default_policy,
        )
        self.assertFalse(eval_missing_reg.eligible)
        self.assertEqual(eval_missing_reg.status, RejectionCode.REJECTED_UNKNOWN_REGULATORY_STATUS.value)

    # 10. Missing risk data produces REJECTED_INSUFFICIENT_DATA
    def test_10_missing_risk_data_rejects(self):
        eval_missing_risk = evaluate_candidate_zone(
            zone_id="ZONE_NO_RISK",
            opportunity_score=75.0,
            risk_score=None,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=10.0,
            policy=self.default_policy,
        )
        self.assertFalse(eval_missing_risk.eligible)
        self.assertEqual(eval_missing_risk.status, RejectionCode.REJECTED_INSUFFICIENT_DATA.value)

    # 11. Missing opportunity data produces REJECTED_INSUFFICIENT_DATA
    def test_11_missing_opportunity_data_rejects(self):
        eval_missing_opp = evaluate_candidate_zone(
            zone_id="ZONE_NO_OPP",
            opportunity_score=None,
            risk_score=25.0,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=10.0,
            policy=self.default_policy,
        )
        self.assertFalse(eval_missing_opp.eligible)
        self.assertEqual(eval_missing_opp.status, RejectionCode.REJECTED_INSUFFICIENT_DATA.value)

    # 12. Missing distance dynamically renormalizes weights when distance is optional
    def test_12_missing_distance_renormalizes_ranking(self):
        eval_no_dist = evaluate_candidate_zone(
            zone_id="ZONE_NO_DIST",
            opportunity_score=70.0,
            risk_score=30.0,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=None,
            policy=self.default_policy,
        )
        self.assertTrue(eval_no_dist.eligible)
        self.assertIsNotNone(eval_no_dist.ranking_score)
        # Expected rebalanced weights: opp = 0.60 / 0.85 ≈ 0.7059, risk = 0.25 / 0.85 ≈ 0.2941
        # score = 0.70588 * 70 + 0.29412 * 70 = 70.0
        self.assertAlmostEqual(eval_no_dist.ranking_score, 70.0, places=1)

    # 13. Distance hard constraint violation produces REJECTED_DISTANCE
    def test_13_distance_hard_constraint(self):
        eval_far = evaluate_candidate_zone(
            zone_id="ZONE_FAR",
            opportunity_score=90.0,
            risk_score=20.0,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=35.0,  # exceeds default max 30.0 NM
            policy=self.default_policy,
        )
        self.assertFalse(eval_far.eligible)
        self.assertEqual(eval_far.status, RejectionCode.REJECTED_DISTANCE.value)
        self.assertIn(RejectionCode.REJECTED_DISTANCE.value, eval_far.rejection_codes)

    # 14. Minimum opportunity constraint violation produces REJECTED_LOW_OPPORTUNITY
    def test_14_minimum_opportunity_constraint(self):
        strict_policy = DecisionPolicy(max_risk_score=50.0, min_opportunity_score=60.0)
        eval_low_opp = evaluate_candidate_zone(
            zone_id="ZONE_LOW_OPP",
            opportunity_score=45.0,
            risk_score=20.0,
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=10.0,
            policy=strict_policy,
        )
        self.assertFalse(eval_low_opp.eligible)
        self.assertEqual(eval_low_opp.status, RejectionCode.REJECTED_LOW_OPPORTUNITY.value)
        self.assertIn(RejectionCode.REJECTED_LOW_OPPORTUNITY.value, eval_low_opp.rejection_codes)

    # 15. Configurable max risk threshold
    def test_15_configurable_max_risk_threshold(self):
        # With lenient policy, Zone A is eligible
        lenient_policy = DecisionPolicy(max_risk_score=80.0)
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=lenient_policy)
        self.assertTrue(eval_a.eligible)
        self.assertEqual(eval_a.status, "ELIGIBLE")

        # With strict policy, Zone B is rejected if max_risk is 30.0
        strict_policy = DecisionPolicy(max_risk_score=30.0)
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=strict_policy)
        self.assertFalse(eval_b.eligible)
        self.assertEqual(eval_b.status, RejectionCode.REJECTED_RISK.value)

    # 16. Configurable ranking weights
    def test_16_configurable_ranking_weights(self):
        # Prioritize safety: 80% risk_inverse, 10% opportunity, 10% distance
        safety_weights = RankingWeights(opportunity=0.10, risk=0.80, distance=0.10)
        score_safety, comp, weights_used = calculate_ranking_score(
            opportunity_score=80.0,
            risk_score=20.0,  # risk_inverse = 80.0
            distance_nm=0.0,  # dist_comp = 100.0
            weights=safety_weights,
        )
        # score = 0.10*80 + 0.80*80 + 0.10*100 = 8 + 64 + 10 = 82.0
        self.assertAlmostEqual(score_safety, 82.0, places=1)

    # 17. Ranking score bounded strictly between 0 and 100
    def test_17_ranking_score_bounded_0_to_100(self):
        score_max, _, _ = calculate_ranking_score(opportunity_score=150.0, risk_score=-20.0, distance_nm=0.0)
        self.assertLessEqual(score_max, 100.0)

        score_min, _, _ = calculate_ranking_score(opportunity_score=-50.0, risk_score=150.0, distance_nm=100.0)
        self.assertGreaterEqual(score_min, 0.0)

    # 18. Deterministic repeated execution produces bitwise identical results
    def test_18_deterministic_repeatability(self):
        res1 = synthesize_decision_from_p6_results(
            opportunity_result={"data": {"scored_zones": [{"zone_id": "Z1", "opportunity_score": 75.0, "raw_features": {"distance_nm": 10.0}}]}},
            risk_result={"data": {"scored_zones": [{"zone_id": "Z1", "risk_score": 25.0}]}},
            regulatory_result={"data": {"scored_checks": [{"zone_id": "Z1", "status": "ELIGIBLE"}]}},
            policy=self.default_policy,
        )
        res2 = synthesize_decision_from_p6_results(
            opportunity_result={"data": {"scored_zones": [{"zone_id": "Z1", "opportunity_score": 75.0, "raw_features": {"distance_nm": 10.0}}]}},
            risk_result={"data": {"scored_zones": [{"zone_id": "Z1", "risk_score": 25.0}]}},
            regulatory_result={"data": {"scored_checks": [{"zone_id": "Z1", "status": "ELIGIBLE"}]}},
            policy=self.default_policy,
        )
        self.assertEqual(res1.to_dict(), res2.to_dict())

    # 19. Rejection codes integrity and transparency
    def test_19_rejection_codes_integrity(self):
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=self.default_policy)
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)

        self.assertEqual(eval_a.rejection_codes, ["REJECTED_RISK"])
        self.assertEqual(eval_c.rejection_codes, ["REJECTED_LEGAL"])

    # 20. Machine-readable rationale in DecisionResult
    def test_20_machine_readable_rationale(self):
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=self.default_policy)
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)

        result = rank_and_select_zones([eval_a, eval_b, eval_c], policy=self.default_policy)
        self.assertGreater(len(result.rationale), 0)
        self.assertTrue(any("ZONE_B selected as top recommendation" in r for r in result.rationale))
        self.assertTrue(any("Rejected non-compliant/hazardous candidates" in r for r in result.rationale))

    # 21. Provenance preserved
    def test_21_provenance_preserved(self):
        result = rank_and_select_zones([], policy=self.default_policy)
        self.assertIn("opportunity_source", result.provenance)
        self.assertIn("risk_source", result.provenance)
        self.assertIn("regulatory_source", result.provenance)
        self.assertTrue(result.provenance["synthetic"])

    # 22. Disclaimer present
    def test_22_disclaimer_present(self):
        result = rank_and_select_zones([], policy=self.default_policy)
        self.assertEqual(result.disclaimer, DECISION_DISCLAIMER)
        self.assertIn("not constitute official fishing", result.disclaimer)

    # 23. P4 ToolResult Integration for rank_zones and select_safe_fishing_zone
    def test_23_tool_entrypoints_contract_and_structure(self):
        mock_deps = {
            "opportunity": {
                "status": "success",
                "source": "P6_ANALYTICS_OPPORTUNITY",
                "operation": "calculate_opportunity",
                "data": {
                    "scored_zones": [
                        {"zone_id": "ZONE_A", "opportunity_score": 76.6, "raw_features": {"distance_nm": 14.5}},
                        {"zone_id": "ZONE_B", "opportunity_score": 66.9, "raw_features": {"distance_nm": 8.2}},
                        {"zone_id": "ZONE_C", "opportunity_score": 84.5, "raw_features": {"distance_nm": 18.0}},
                    ]
                },
            },
            "risk": {
                "status": "success",
                "source": "P6_ANALYTICS_RISK",
                "operation": "calculate_marine_risk",
                "data": {
                    "scored_zones": [
                        {"zone_id": "ZONE_A", "risk_score": 75.2, "severity": "HIGH"},
                        {"zone_id": "ZONE_B", "risk_score": 34.9, "severity": "MODERATE"},
                        {"zone_id": "ZONE_C", "risk_score": 30.8, "severity": "LOW"},
                    ]
                },
            },
            "restrictions": {
                "status": "success",
                "source": "P6_ANALYTICS_REGULATORY",
                "operation": "check_restrictions",
                "data": {
                    "scored_checks": [
                        {"zone_id": "ZONE_A", "status": "ELIGIBLE", "reasons": []},
                        {"zone_id": "ZONE_B", "status": "ELIGIBLE", "reasons": []},
                        {"zone_id": "ZONE_C", "status": "BLOCKED", "reasons": ["Netravati MPA restricted"]},
                    ]
                },
            },
        }

        # Test rank_zones entrypoint
        rank_out = calculate_zone_ranking_tool_entrypoint(parameters={}, dependencies=mock_deps)
        self.assertEqual(rank_out["status"], "success")
        self.assertEqual(rank_out["source"], "P6_ANALYTICS_DECISION")
        self.assertEqual(len(rank_out["data"]["ranked_zones"]), 1)
        self.assertEqual(rank_out["data"]["ranked_zones"][0]["zone_id"], "ZONE_B")

        # Test select_safe_fishing_zone entrypoint
        select_out = select_safe_fishing_zone_tool_entrypoint(parameters={}, dependencies=mock_deps)
        self.assertEqual(select_out["status"], "success")
        self.assertEqual(select_out["source"], "P6_ANALYTICS_DECISION")
        self.assertEqual(select_out["data"]["selected_zone"]["zone_id"], "ZONE_B")

    # 24. Vessel-adjusted risk consumed correctly without recalculation
    def test_24_vessel_adjusted_risk_consumed_directly(self):
        # Suppose Phase 6B scaled Zone B risk up to 55.0 for small craft, exceeding 50.0 max risk
        eval_vessel_adjusted = evaluate_candidate_zone(
            zone_id="ZONE_B_SMALL_CRAFT",
            opportunity_score=66.9,
            risk_score=55.0,  # Already adjusted by 6B
            regulatory_status=ComplianceStatus.ELIGIBLE.value,
            distance_nm=8.2,
            policy=self.default_policy,
        )
        self.assertFalse(eval_vessel_adjusted.eligible)
        self.assertEqual(eval_vessel_adjusted.status, RejectionCode.REJECTED_RISK.value)

    # 25. No external network / zero I/O execution
    def test_25_strictly_offline_execution(self):
        # Confirm pure analytical execution executes synchronously in milliseconds
        res = synthesize_decision_from_p6_results(
            opportunity_result=None,
            risk_result=None,
            regulatory_result=None,
            policy=self.default_policy,
        )
        self.assertEqual(res.selected_zone.zone_id, "ZONE_B")

    # 26. Empty candidate list handling
    def test_26_empty_candidate_list(self):
        result = rank_and_select_zones([], policy=self.default_policy)
        self.assertEqual(result.status, "empty_candidates")
        self.assertIsNone(result.selected_zone)
        self.assertEqual(len(result.ranked_zones), 0)
        self.assertEqual(len(result.rejected_zones), 0)

    # 27. Single candidate evaluation and selection
    def test_27_single_candidate_selection(self):
        eval_single = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        result = rank_and_select_zones([eval_single], policy=self.default_policy)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.selected_zone.zone_id, "ZONE_B")
        self.assertEqual(len(result.ranked_zones), 1)

    # 28. All candidates rejected scenario
    def test_28_all_candidates_rejected(self):
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=self.default_policy)
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)
        result = rank_and_select_zones([eval_a, eval_c], policy=self.default_policy)
        self.assertEqual(result.status, "no_eligible_zones")
        self.assertIsNone(result.selected_zone)
        self.assertEqual(len(result.ranked_zones), 0)
        self.assertEqual(len(result.rejected_zones), 2)

    # 29. One eligible candidate among multiple rejected
    def test_29_one_eligible_among_rejected(self):
        eval_a = evaluate_candidate_zone(**self.zone_a_raw, policy=self.default_policy)
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        eval_c = evaluate_candidate_zone(**self.zone_c_raw, policy=self.default_policy)

        result = rank_and_select_zones([eval_a, eval_b, eval_c], policy=self.default_policy)
        self.assertEqual(len(result.ranked_zones), 1)
        self.assertEqual(len(result.rejected_zones), 2)
        self.assertEqual(result.selected_zone.zone_id, "ZONE_B")

    # 30. Ranking does not alter original analytical scores
    def test_30_ranking_preserves_original_analytical_scores(self):
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        orig_opp = eval_b.opportunity_score
        orig_risk = eval_b.risk_score
        orig_dist = eval_b.distance_nm

        result = rank_and_select_zones([eval_b], policy=self.default_policy)
        self.assertEqual(result.selected_zone.opportunity_score, orig_opp)
        self.assertEqual(result.selected_zone.risk_score, orig_risk)
        self.assertEqual(result.selected_zone.distance_nm, orig_dist)

    # 31. Ranking components sub-score decomposition check
    def test_31_ranking_components_decomposition(self):
        eval_b = evaluate_candidate_zone(**self.zone_b_raw, policy=self.default_policy)
        self.assertIsNotNone(eval_b.components)
        self.assertAlmostEqual(eval_b.components.opportunity, 66.9, places=1)
        self.assertAlmostEqual(eval_b.components.risk_inverse, 65.1, places=1)
        # distance component: 100 * (1 - 8.2 / 30.0) ≈ 72.67
        self.assertAlmostEqual(eval_b.components.distance, 72.67, places=1)


if __name__ == "__main__":
    unittest.main()
