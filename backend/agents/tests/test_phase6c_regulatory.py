"""Comprehensive Test Suite for Phase 6C: P6 Regulatory & Marine Spatial Restrictions Engine.

Tests:
1. Unrestricted zone -> ELIGIBLE
2. Marine Protected Area (MPA) -> BLOCKED
3. Naval / military exercise zone -> BLOCKED
4. Active fishing closure -> BLOCKED
5. Active temporary closure -> BLOCKED
6. Expired closure -> not blocking (ELIGIBLE)
7. Future closure -> not blocking (ELIGIBLE)
8. Permanent restriction -> BLOCKED
9. Shipping lane warning -> ELIGIBLE + WARNING
10. Unknown jurisdiction -> UNKNOWN (eligible=False, hard_block=False)
11. Missing regulatory data -> INSUFFICIENT_DATA
12. Point inside polygon spatial check
13. Point outside polygon spatial check
14. Boundary / polygon vertex edge behavior
15. Multiple overlapping restrictions
16. Blocking + warning combination
17. Deterministic repeated calculation
18. Synthetic provenance and metadata verification
19. P4 ToolResult integration
20. Mangalore Zone A -> ELIGIBLE
21. Mangalore Zone B -> ELIGIBLE
22. Mangalore Zone C -> BLOCKED
23. Legality independent of Phase 6A opportunity score
24. Legality independent of Phase 6B physical risk score
25. Zero external network/API dependencies
"""

import unittest
from typing import Any, Dict, List

from backend.agents.analytics.opportunity import calculate_zone_opportunity
from backend.agents.analytics.regulatory import (
    calculate_regulatory_compliance_tool_entrypoint,
    check_spatial_intersection,
    evaluate_regulatory_compliance_from_p4_results,
    evaluate_zone_compliance,
    is_point_in_polygon,
    is_restriction_temporally_active,
)
from backend.agents.analytics.risk import calculate_zone_risk
from backend.agents.analytics.schemas import (
    ComplianceStatus,
    RawOpportunityFeatures,
    RawRiskFeatures,
    RegulatoryAnalysisResult,
    RegulatoryCheck,
    RegulatoryDecision,
    Restriction,
    RestrictionType,
)
from backend.agents.mocks.fixtures.regulatory_mangalore import (
    MANGALORE_REGULATORY_REFERENCE_TIME,
    SYNTHETIC_REGULATORY_RESTRICTIONS,
    get_synthetic_restrictions,
)
from backend.agents.tools.adapters.restrictions_adapter import SyntheticRestrictionsAdapter


class TestPhase6CRegulatoryEngine(unittest.TestCase):
    """Test suite for P6 Regulatory & Marine Spatial Restrictions Engine."""

    def setUp(self):
        self.location = {"name": "Mangalore", "latitude": 12.8681, "longitude": 74.8427}
        self.ref_time = MANGALORE_REGULATORY_REFERENCE_TIME  # "2026-09-12T06:00:00Z"
        self.restrictions_adapter = SyntheticRestrictionsAdapter()

    # 1. Unrestricted zone -> ELIGIBLE
    def test_01_unrestricted_zone_eligible(self):
        # Coordinates in open, clear coastal waters outside shipping lanes and MPAs
        res = evaluate_zone_compliance(
            zone_id="ZONE_CLEAR_OPEN",
            latitude=13.05,
            longitude=74.60,
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)
        self.assertEqual(len(res.blocking_restrictions), 0)
        self.assertEqual(len(res.warnings), 0)

    # 2. Marine Protected Area (MPA) -> BLOCKED
    def test_02_mpa_blocked(self):
        mpa = Restriction(
            restriction_id="TEST_MPA_01",
            restriction_type=RestrictionType.MPA.value,
            name="Coral Reef Conservation Sanctuary",
            status="active",
            zone_id="ZONE_MPA",
            reason="Biodiversity hotspot protected under marine conservation law",
            is_hard_block=True,
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_MPA",
            restrictions=[mpa],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)
        self.assertEqual(len(res.blocking_restrictions), 1)
        self.assertIn("HARD BLOCK", res.reasons[0])

    # 3. Naval / military exercise zone -> BLOCKED
    def test_03_naval_zone_blocked(self):
        naval = Restriction(
            restriction_id="TEST_NAV_01",
            restriction_type=RestrictionType.NAVAL_ZONE.value,
            name="Naval Surface Gunnery Firing Range",
            status="active",
            zone_id="ZONE_NAV",
            reason="Active live-fire exercises in progress",
            is_hard_block=True,
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_NAV",
            restrictions=[naval],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)

    # 4. Active fishing closure -> BLOCKED
    def test_04_fishing_closure_blocked(self):
        closure = Restriction(
            restriction_id="TEST_CLOSURE_01",
            restriction_type=RestrictionType.FISHING_RESTRICTED_ZONE.value,
            name="Juvenile Demersal Nursery Sanctuary",
            status="active",
            zone_id="ZONE_NURSERY",
            reason="Closed to bottom trawling and gillnetting",
            is_hard_block=True,
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_NURSERY",
            restrictions=[closure],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)

    # 5. Active temporary closure -> BLOCKED
    def test_05_temporary_closure_active_blocked(self):
        temp_active = Restriction(
            restriction_id="TEMP_ACTIVE_01",
            restriction_type=RestrictionType.TEMPORARY_CLOSURE.value,
            name="Emergency Oil Spill Remediation Exclusion",
            status="active",
            zone_id="ZONE_SPILL",
            reason="Temporary maritime cleanup perimeter",
            valid_from="2026-09-01T00:00:00Z",
            valid_to="2026-09-20T00:00:00Z",
            is_hard_block=True,
        )
        # Reference time is 2026-09-12 (inside window)
        res = evaluate_zone_compliance(
            zone_id="ZONE_SPILL",
            restrictions=[temp_active],
            reference_time="2026-09-12T12:00:00Z",
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)

    # 6. Expired closure -> not blocking (ELIGIBLE)
    def test_06_expired_closure_not_blocking(self):
        expired = Restriction(
            restriction_id="EXPIRED_CLOSURE_01",
            restriction_type=RestrictionType.TEMPORARY_CLOSURE.value,
            name="Monsoon Ban July 2026",
            status="active",
            zone_id="ZONE_EXPIRED",
            reason="Monsoon seasonal ban ended July 31",
            valid_from="2026-06-01T00:00:00Z",
            valid_to="2026-07-31T23:59:59Z",
            is_hard_block=True,
        )
        # Reference time is 2026-09-12 (after window)
        res = evaluate_zone_compliance(
            zone_id="ZONE_EXPIRED",
            restrictions=[expired],
            reference_time="2026-09-12T12:00:00Z",
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)
        self.assertEqual(len(res.blocking_restrictions), 0)

    # 7. Future closure -> not blocking (ELIGIBLE)
    def test_07_future_closure_not_blocking(self):
        future = Restriction(
            restriction_id="FUTURE_CLOSURE_01",
            restriction_type=RestrictionType.TEMPORARY_CLOSURE.value,
            name="Winter Nursery Rest Period Dec 2026",
            status="scheduled",
            zone_id="ZONE_FUTURE",
            reason="Winter ban begins Dec 1",
            valid_from="2026-12-01T00:00:00Z",
            valid_to="2026-12-31T23:59:59Z",
            is_hard_block=True,
        )
        # Reference time is 2026-09-12 (before window)
        res = evaluate_zone_compliance(
            zone_id="ZONE_FUTURE",
            restrictions=[future],
            reference_time="2026-09-12T12:00:00Z",
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)

    # 8. Permanent restriction -> BLOCKED
    def test_08_permanent_restriction_blocked(self):
        perm = Restriction(
            restriction_id="PERM_MPA_01",
            restriction_type=RestrictionType.MPA.value,
            name="Permanent Coral Island Marine Park",
            status="active",
            zone_id="ZONE_PERM",
            reason="Permanent national marine park",
            valid_from="2015-01-01T00:00:00Z",
            valid_to=None,  # Permanent
            is_hard_block=True,
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_PERM",
            restrictions=[perm],
            reference_time="2026-09-12T12:00:00Z",
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)

    # 9. Shipping lane warning -> ELIGIBLE + WARNING
    def test_09_shipping_lane_warning(self):
        shipping = Restriction(
            restriction_id="TSS_CHANNEL_01",
            restriction_type=RestrictionType.SHIPPING_LANE.value,
            name="Deep Draft Vessel Approach Route",
            status="active",
            zone_id="ZONE_SHIPPING",
            reason="High container traffic. Maintain lookout; do not obstruct channel.",
            is_hard_block=False,
            severity="WARNING",
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_SHIPPING",
            restrictions=[shipping],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)
        self.assertEqual(len(res.blocking_restrictions), 0)
        self.assertEqual(len(res.warnings), 1)
        self.assertIn("ADVISORY", res.warnings[0])

    # 10. Unknown jurisdiction -> UNKNOWN
    def test_10_unknown_jurisdiction(self):
        res = evaluate_zone_compliance(
            zone_id="ZONE_UNRESOLVED",
            latitude=8.00,
            longitude=65.00,
            jurisdiction_known=False,
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.UNKNOWN.value)
        self.assertFalse(res.eligible)
        self.assertFalse(res.hard_block)
        self.assertIn("Unresolved", res.warnings[0])

    # 11. Missing regulatory data -> INSUFFICIENT_DATA
    def test_11_missing_regulatory_data(self):
        analysis = evaluate_regulatory_compliance_from_p4_results(
            restrictions_result=None,
            candidate_zones=None,
            location=None,
        )
        self.assertEqual(analysis.status, ComplianceStatus.INSUFFICIENT_DATA.value)
        self.assertEqual(len(analysis.zones), 0)

    # 12. Point inside polygon spatial check
    def test_12_point_inside_polygon(self):
        poly = [
            [74.0, 12.0],
            [75.0, 12.0],
            [75.0, 13.0],
            [74.0, 13.0],
            [74.0, 12.0],
        ]
        # (12.5, 74.5) is dead center
        self.assertTrue(is_point_in_polygon(12.5, 74.5, poly))

    # 13. Point outside polygon spatial check
    def test_13_point_outside_polygon(self):
        poly = [
            [74.0, 12.0],
            [75.0, 12.0],
            [75.0, 13.0],
            [74.0, 13.0],
            [74.0, 12.0],
        ]
        # (13.5, 74.5) is north of polygon
        self.assertFalse(is_point_in_polygon(13.5, 74.5, poly))
        # (12.5, 73.5) is west of polygon
        self.assertFalse(is_point_in_polygon(12.5, 73.5, poly))

    # 14. Boundary / polygon vertex edge behavior
    def test_14_boundary_vertex_edge_behavior(self):
        poly = [
            [74.0, 12.0],
            [75.0, 12.0],
            [75.0, 13.0],
            [74.0, 13.0],
            [74.0, 12.0],
        ]
        # Exactly on vertex (12.0, 74.0)
        self.assertTrue(is_point_in_polygon(12.0, 74.0, poly))

    # 15. Multiple overlapping restrictions
    def test_15_multiple_overlapping_restrictions(self):
        r1 = Restriction(
            restriction_id="MPA_OVERLAP",
            restriction_type=RestrictionType.MPA.value,
            name="Turtle Nesting MPA",
            status="active",
            zone_id="ZONE_MULTI",
            reason="Turtle conservation",
            is_hard_block=True,
        )
        r2 = Restriction(
            restriction_id="NAVAL_OVERLAP",
            restriction_type=RestrictionType.NAVAL_ZONE.value,
            name="Naval Radar Corridor",
            status="active",
            zone_id="ZONE_MULTI",
            reason="Electronic warfare test sector",
            is_hard_block=True,
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_MULTI",
            restrictions=[r1, r2],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertEqual(len(res.restrictions_found), 2)
        self.assertEqual(len(res.blocking_restrictions), 2)
        self.assertEqual(len(res.reasons), 2)

    # 16. Blocking + warning combination
    def test_16_blocking_plus_warning_combination(self):
        hard_r = Restriction(
            restriction_id="MPA_HARD",
            restriction_type=RestrictionType.MPA.value,
            name="Sanctuary Core",
            status="active",
            zone_id="ZONE_COMBO",
            reason="Strict no-take zone",
            is_hard_block=True,
        )
        soft_r = Restriction(
            restriction_id="SHIPPING_SOFT",
            restriction_type=RestrictionType.SHIPPING_LANE.value,
            name="Outer Ferry Corridor",
            status="active",
            zone_id="ZONE_COMBO",
            reason="Ferry crossing caution",
            is_hard_block=False,
            severity="WARNING",
        )
        res = evaluate_zone_compliance(
            zone_id="ZONE_COMBO",
            restrictions=[hard_r, soft_r],
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)
        self.assertEqual(len(res.blocking_restrictions), 1)
        self.assertEqual(len(res.warnings), 1)

    # 17. Deterministic repeated calculation
    def test_17_deterministic_repeated_calculation(self):
        res1 = evaluate_zone_compliance(
            zone_id="ZONE_C",
            latitude=12.82,
            longitude=75.05,
            reference_time=self.ref_time,
        )
        for _ in range(50):
            res_k = evaluate_zone_compliance(
                zone_id="ZONE_C",
                latitude=12.82,
                longitude=75.05,
                reference_time=self.ref_time,
            )
            self.assertEqual(res1.status, res_k.status)
            self.assertEqual(res1.eligible, res_k.eligible)
            self.assertEqual(res1.hard_block, res_k.hard_block)
            self.assertEqual(len(res1.blocking_restrictions), len(res_k.blocking_restrictions))

    # 18. Synthetic provenance and metadata verification
    def test_18_synthetic_provenance_and_metadata(self):
        analysis = evaluate_regulatory_compliance_from_p4_results(
            candidate_zones=[{"zone_id": "ZONE_A", "latitude": 12.95, "longitude": 74.80}]
        )
        self.assertIn("synthetic regulatory fixture", analysis.disclaimer.lower())
        self.assertEqual(analysis.source, "P6_ANALYTICS_REGULATORY")
        self.assertEqual(analysis.zones[0].provenance, "synthetic_regulatory_fixture")

    # 19. P4 ToolResult integration (check_restrictions)
    def test_19_p4_tool_result_integration(self):
        restr_p4 = self.restrictions_adapter.check_restrictions(self.location)

        tool_output = calculate_regulatory_compliance_tool_entrypoint(
            parameters={"location": self.location},
            dependencies={"restrictions": restr_p4},
        )
        self.assertEqual(tool_output["status"], "success")
        self.assertEqual(tool_output["source"], "P6_ANALYTICS_REGULATORY")
        self.assertTrue(tool_output["data"]["regulatory_evaluated"])
        self.assertIn("ZONE_A", tool_output["data"]["zone_compliance"])
        self.assertIn("ZONE_B", tool_output["data"]["zone_compliance"])
        self.assertIn("ZONE_C", tool_output["data"]["zone_compliance"])
        self.assertTrue(tool_output["data"]["zone_compliance"]["ZONE_A"]["is_legal"])
        self.assertTrue(tool_output["data"]["zone_compliance"]["ZONE_B"]["is_legal"])
        self.assertFalse(tool_output["data"]["zone_compliance"]["ZONE_C"]["is_legal"])

    # 20. Mangalore Zone A -> ELIGIBLE
    def test_20_mangalore_zone_a_eligible(self):
        res = evaluate_zone_compliance(
            zone_id="ZONE_A",
            latitude=12.95,
            longitude=74.80,
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)

    # 21. Mangalore Zone B -> ELIGIBLE
    def test_21_mangalore_zone_b_eligible(self):
        res = evaluate_zone_compliance(
            zone_id="ZONE_B",
            latitude=12.90,
            longitude=74.95,
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.ELIGIBLE.value)
        self.assertTrue(res.eligible)
        self.assertFalse(res.hard_block)

    # 22. Mangalore Zone C -> BLOCKED
    def test_22_mangalore_zone_c_blocked(self):
        res = evaluate_zone_compliance(
            zone_id="ZONE_C",
            latitude=12.82,
            longitude=75.05,
            reference_time=self.ref_time,
        )
        self.assertEqual(res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(res.eligible)
        self.assertTrue(res.hard_block)
        self.assertGreaterEqual(len(res.blocking_restrictions), 1)
        self.assertTrue(any("Netravati" in r.name for r in res.blocking_restrictions))

    # 23. Legality independent of Phase 6A opportunity score
    def test_23_legality_independent_of_opportunity_score(self):
        """
        Crucial North-Star Invariant:
        Zone C has the HIGHEST opportunity score (84.5), but Regulatory Engine MUST block it.
        Opportunity score cannot override a hard regulatory restriction.
        """
        raw_opp_c = RawOpportunityFeatures(
            zone_id="ZONE_C",
            pfz_confidence=0.94,
            sst_gradient_delta=1.1,
            chlorophyll_a_mg_m3=3.2,
            distance_nm=18.0,
        )
        opp_res = calculate_zone_opportunity("ZONE_C", raw_opp_c)
        self.assertAlmostEqual(opp_res.opportunity_score, 84.5, places=1)

        # Regulatory evaluation
        reg_res = evaluate_zone_compliance("ZONE_C", 12.82, 75.05, reference_time=self.ref_time)
        self.assertEqual(reg_res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(reg_res.eligible)
        self.assertTrue(reg_res.hard_block)

    # 24. Legality independent of Phase 6B physical risk score
    def test_24_legality_independent_of_physical_risk_score(self):
        """
        Crucial North-Star Invariant:
        Zone C has LOW physical risk (30.8, calm wave 1.0m, wind 9.5 kts), but Regulatory Engine MUST block it.
        Physical safety cannot override a legal prohibition.
        """
        raw_risk_c = RawRiskFeatures(
            zone_id="ZONE_C",
            wave_height_m=1.0,
            wind_speed_knots=9.5,
            wind_gust_knots=12.0,
            swell_height_m=0.6,
        )
        risk_res = calculate_zone_risk("ZONE_C", raw_risk_c)
        self.assertTrue(risk_res.is_safe_heuristic)

        # Regulatory evaluation
        reg_res = evaluate_zone_compliance("ZONE_C", 12.82, 75.05, reference_time=self.ref_time)
        self.assertEqual(reg_res.status, ComplianceStatus.BLOCKED.value)
        self.assertFalse(reg_res.eligible)
        self.assertTrue(reg_res.hard_block)

    # 25. Zero external network/API dependencies
    def test_25_zero_external_network_dependencies(self):
        # Fully runs offline in memory
        catalog = get_synthetic_restrictions()
        self.assertGreaterEqual(len(catalog), 5)
        for r in catalog:
            self.assertEqual(r.source, "synthetic")


if __name__ == "__main__":
    unittest.main()
