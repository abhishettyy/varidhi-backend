"""End-to-End LangGraph integration tests for Phase 6E: P6 Analytics & Decision Engine Integration.

Tests verify the complete compiled LangGraph workflow:
understand_query -> planner -> tool_selection -> executor (P4 Tools + P6 Analytics + Decision) -> evidence_assembly -> response_generation
"""

import asyncio
import unittest
from typing import Any, Dict

from backend.agents.graph.builder import build_marine_agent_graph
from backend.agents.graph.workflow import (
    get_marine_agent_graph,
    run_marine_agent,
    run_marine_agent_state,
    run_marine_agent_state_async,
)
from backend.agents.mocks.tool_registry import get_tool_registry
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.plan import PlanStep, StepType
from backend.agents.schemas.response import RoleType
from backend.agents.state.marine_state import MarineState


class TestPhase6ELangGraphIntegration(unittest.TestCase):
    """End-to-End verification of the compiled LangGraph orchestration pipeline."""

    def setUp(self):
        self.graph = get_marine_agent_graph()

    # 1. North-star fishing recommendation query
    def test_01_mangalore_north_star_e2e(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)

        # 1. Verify understanding
        self.assertEqual(state["intent"], MarineIntent.FISHING_RECOMMENDATION.value)
        self.assertEqual(state["location"]["name"], "Mangalore")
        self.assertEqual(state["time_range"]["relative_day"], "tomorrow")

        # 2. Verify P4 Tool Results
        tool_res = state["tool_results"]
        op_names = [t["operation"] for t in tool_res]
        self.assertIn("get_pfz", op_names)
        self.assertIn("get_sst", op_names)
        self.assertIn("get_chlorophyll", op_names)
        self.assertIn("get_wind", op_names)
        self.assertIn("get_wave", op_names)
        self.assertIn("check_restrictions", op_names)

        # 3. Verify P6 Analytics Results
        analytics_res = state["analytics_results"]
        a_ops = [a["operation"] for a in analytics_res]
        self.assertIn("calculate_opportunity", a_ops)
        self.assertIn("calculate_marine_risk", a_ops)
        self.assertIn("rank_zones", a_ops)
        self.assertIn("select_safe_fishing_zone", a_ops)

        # 4. Verify Decision State
        decision = state.get("decision")
        self.assertIsNotNone(decision)
        selected = decision.get("selected_zone")
        self.assertIsNotNone(selected)
        self.assertEqual(selected["zone_id"], "ZONE_B")
        self.assertEqual(selected["status"], "SELECTED")
        self.assertTrue(selected["is_legal"])
        self.assertTrue(selected["is_safe"])
        self.assertAlmostEqual(selected["ranking_score"], 67.31, places=1)
        self.assertAlmostEqual(selected["opportunity_score"], 66.9, places=1)
        self.assertAlmostEqual(selected["risk_score"], 34.9, places=1)

        # 5. Verify Rejected Zones
        rejected = decision.get("rejected_zones", [])
        rej_ids = [r["zone_id"] for r in rejected]
        self.assertIn("ZONE_C", rej_ids)
        self.assertIn("ZONE_A", rej_ids)

        zone_c_eval = [r for r in rejected if r["zone_id"] == "ZONE_C"][0]
        self.assertEqual(zone_c_eval["status"], "REJECTED_LEGAL")

        zone_a_eval = [r for r in rejected if r["zone_id"] == "ZONE_A"][0]
        self.assertEqual(zone_a_eval["status"], "REJECTED_RISK")

        # 6. Verify Evidence Bundle
        self.assertIsNotNone(state.get("evidence_bundle"))
        self.assertGreater(len(state.get("evidence", [])), 5)

        # 7. Verify Response Generation
        resp = state.get("final_response")
        self.assertIsNotNone(resp)
        self.assertEqual(resp.status, "success")
        self.assertIn("ZONE_B", resp.markdown_content)
        self.assertIn("ZONE_C", resp.markdown_content)
        self.assertIn("REJECTED", resp.markdown_content)

    # 2. PFZ Search query flow
    def test_02_pfz_search_query(self):
        query = "Show me potential fishing zones near Kochi."
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        self.assertIn("pfz", [t["operation"] for t in state["tool_results"]] + [a["operation"] for a in state["analytics_results"]] + state.get("plan", []))
        self.assertEqual(state["location"]["name"], "Kochi")

    # 3. Marine safety query flow
    def test_03_marine_safety_query(self):
        query = "Is it safe for a small boat to go out from Mangalore right now?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        self.assertIn(state["intent"], [MarineIntent.MARINE_SAFETY.value, MarineIntent.WEATHER_QUERY.value])
        self.assertIsNotNone(state.get("final_response"))

    # 4. Weather query flow
    def test_04_weather_query(self):
        query = "What is the wind speed and wave height near Chennai today evening?"
        state = run_marine_agent_state(query, role=RoleType.MARITIME_OPERATOR)
        self.assertEqual(state["intent"], MarineIntent.WEATHER_QUERY.value)
        self.assertEqual(state["location"]["name"], "Chennai")
        self.assertIsNotNone(state.get("final_response"))

    # 5. Geofence query flow
    def test_05_geofence_query(self):
        query = "Am I inside the Indian EEZ or a restricted marine sanctuary near Goa?"
        state = run_marine_agent_state(query, role=RoleType.RESEARCHER)
        self.assertEqual(state["intent"], MarineIntent.GEOFENCE_QUERY.value)
        self.assertEqual(state["location"]["name"], "Goa")

    # 6. Historical analysis query flow
    def test_06_historical_analysis_query(self):
        query = "How has sea surface temperature in Mangalore varied over the last 5 years?"
        state = run_marine_agent_state(query, role=RoleType.RESEARCHER)
        self.assertEqual(state["intent"], MarineIntent.HISTORICAL_ANALYSIS.value)
        self.assertIsNotNone(state.get("final_response"))

    # 7. Missing location query flow
    def test_07_missing_location_query(self):
        query = "Where should I fish tomorrow?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        plan = state.get("execution_plan")
        self.assertTrue(plan.requires_clarification or "location" in plan.missing or len(state["errors"]) > 0 or state.get("location") is None)

    # 8. Missing required data in DAG handling
    def test_08_missing_required_data_handling(self):
        registry = get_tool_registry()

        def custom_failing_pfz(parameters, dependencies):
            return {"status": "failed", "source": "mock", "error": "Satellite feed unavailable"}

        registry.register("op_failing_pfz_test", custom_failing_pfz)

        # Plan where mandatory data step fails
        step_bad = PlanStep(id="pfz", type=StepType.DATA.value, operation="op_failing_pfz_test", depends_on=[])
        step_opp = PlanStep(id="opportunity", type=StepType.ANALYTICS.value, operation="calculate_opportunity", depends_on=["pfz"])

        initial_state: MarineState = {
            "query": "Where should I fish?",
            "user_type": "fisherman",
            "execution_steps": [step_bad, step_opp],
            "tool_results": [],
            "analytics_results": [],
            "errors": [],
        }

        final_state = asyncio.run(self.graph.ainvoke(initial_state))
        self.assertGreater(len(final_state["errors"]), 0)

    # 9. Blocked regulatory zone is never recommended
    def test_09_blocked_regulatory_zone_never_recommended(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.RESEARCHER)

        decision = state.get("decision", {})
        selected = decision.get("selected_zone", {})
        self.assertNotEqual(selected.get("zone_id"), "ZONE_C", "Zone C is in Netravati MPA and MUST NOT be recommended")

    # 10. Analytics failure handling in decision
    def test_10_analytics_failure_in_decision(self):
        registry = get_tool_registry()

        def failing_risk(parameters, dependencies):
            return {"status": "failed", "source": "mock", "error": "Wave sensor data corrupt"}

        registry.register("op_failing_risk_test", failing_risk)

        step_pfz = PlanStep(id="pfz", type=StepType.DATA.value, operation="get_pfz", depends_on=[])
        step_opp = PlanStep(id="opportunity", type=StepType.ANALYTICS.value, operation="calculate_opportunity", depends_on=["pfz"])
        step_risk = PlanStep(id="risk", type=StepType.ANALYTICS.value, operation="op_failing_risk_test", depends_on=[])
        step_decision = PlanStep(id="decision", type=StepType.DECISION.value, operation="select_safe_fishing_zone", depends_on=["opportunity", "risk"])

        initial_state: MarineState = {
            "query": "Fishing advice",
            "user_type": "fisherman",
            "execution_steps": [step_pfz, step_opp, step_risk, step_decision],
            "tool_results": [],
            "analytics_results": [],
            "errors": [],
        }

        final_state = asyncio.run(self.graph.ainvoke(initial_state))
        self.assertGreater(len(final_state["errors"]), 0)

    # 11. Final response contains selected zone and rejected zones explanation
    def test_11_final_response_contains_selected_and_rejected_zones(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        resp = state.get("final_response")
        self.assertIn("ZONE_B", resp.markdown_content)
        self.assertIn("ZONE_C", resp.markdown_content)
        self.assertIn("ZONE_A", resp.markdown_content)

    # 12. Legal block cannot be overridden by opportunity
    def test_12_legal_block_cannot_be_overridden_by_opportunity(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        decision = state.get("decision", {})
        all_evals = decision.get("all_evaluations", [])
        zone_c = [e for e in all_evals if e.get("zone_id") == "ZONE_C"][0]

        self.assertGreater(zone_c["opportunity_score"], 75.0)
        self.assertEqual(zone_c["status"], "REJECTED_LEGAL")
        self.assertFalse(zone_c["eligible"])

    # 13. Risk threshold cannot be bypassed
    def test_13_risk_threshold_cannot_be_bypassed(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        decision = state.get("decision", {})
        all_evals = decision.get("all_evaluations", [])
        zone_a = [e for e in all_evals if e.get("zone_id") == "ZONE_A"][0]

        self.assertGreater(zone_a["risk_score"], 50.0)
        self.assertEqual(zone_a["status"], "REJECTED_RISK")
        self.assertFalse(zone_a["eligible"])

    # 14. Dynamic policy change behavior (verifies no hardcoded conclusion)
    def test_14_dynamic_policy_behavior_no_hardcoding(self):
        from backend.agents.analytics.decision import synthesize_decision_from_p6_results
        from backend.agents.analytics.schemas import DecisionPolicy

        opp_result = {"data": {"scored_zones": [
            {"zone_id": "ZONE_A", "opportunity_score": 76.6, "raw_features": {"distance_nm": 14.5}},
            {"zone_id": "ZONE_B", "opportunity_score": 66.9, "raw_features": {"distance_nm": 8.2}},
            {"zone_id": "ZONE_C", "opportunity_score": 84.5, "raw_features": {"distance_nm": 18.0}},
        ]}}
        risk_result = {"data": {"scored_zones": [
            {"zone_id": "ZONE_A", "risk_score": 75.2},
            {"zone_id": "ZONE_B", "risk_score": 34.9},
            {"zone_id": "ZONE_C", "risk_score": 30.8},
        ]}}
        reg_result = {"data": {"scored_checks": [
            {"zone_id": "ZONE_A", "status": "ELIGIBLE"},
            {"zone_id": "ZONE_B", "status": "ELIGIBLE"},
            {"zone_id": "ZONE_C", "status": "BLOCKED"},
        ]}}

        # Policy 1: Default (max_risk=50) -> Zone B selected
        pol1 = DecisionPolicy(max_risk_score=50.0, max_distance_nm=30.0)
        res1 = synthesize_decision_from_p6_results(opp_result, risk_result, reg_result, policy=pol1)
        self.assertEqual(res1.selected_zone.zone_id, "ZONE_B")

        # Policy 2: Lenient risk (max_risk=80) -> Zone A competes and wins due to higher opportunity
        pol2 = DecisionPolicy(max_risk_score=80.0, max_distance_nm=30.0)
        res2 = synthesize_decision_from_p6_results(opp_result, risk_result, reg_result, policy=pol2)
        # Zone A ranking: 0.6*76.6 + 0.25*(100-75.2) + 0.15*(100*(1-14.5/30)) = 45.96 + 6.2 + 7.75 = 59.91
        # Zone B ranking: 67.31
        # Zone B still wins on total ranking, but Zone A is ELIGIBLE!
        self.assertTrue(any(z.zone_id == "ZONE_A" for z in res2.ranked_zones))

        # Policy 3: Strict distance cutoff (max_distance=5.0 NM) -> All candidate zones rejected
        pol3 = DecisionPolicy(max_distance_nm=5.0)
        res3 = synthesize_decision_from_p6_results(opp_result, risk_result, reg_result, policy=pol3)
        self.assertIsNone(res3.selected_zone)
        self.assertEqual(res3.status, "no_eligible_zones")
        self.assertEqual(len(res3.rejected_zones), 3)

    # 15. Researcher role persona formatting
    def test_15_researcher_role_persona_formatting(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.RESEARCHER)
        resp = state.get("final_response")
        self.assertIn("Multi-Engine Decision Synthesis & Zone Ranking", resp.markdown_content)
        self.assertIn("ZONE_B", resp.markdown_content)
        self.assertIn("ZONE_C", resp.markdown_content)

    # 16. Regression invariant: Direct P6 == LangGraph P6 under canonical Mangalore inputs
    def test_16_p6_canonical_input_and_score_consistency_regression(self):
        from backend.agents.analytics.opportunity import calculate_zone_opportunity
        from backend.agents.analytics.risk import calculate_zone_risk
        from backend.agents.analytics.schemas import RawOpportunityFeatures, RawRiskFeatures

        # Direct P6 calculations
        direct_opp = {
            "ZONE_A": calculate_zone_opportunity("ZONE_A", RawOpportunityFeatures(
                zone_id="ZONE_A", pfz_confidence=0.88, sst_gradient_delta=0.9, chlorophyll_a_mg_m3=2.8, distance_nm=14.5
            )),
            "ZONE_B": calculate_zone_opportunity("ZONE_B", RawOpportunityFeatures(
                zone_id="ZONE_B", pfz_confidence=0.82, sst_gradient_delta=0.6, chlorophyll_a_mg_m3=2.3, distance_nm=8.2
            )),
            "ZONE_C": calculate_zone_opportunity("ZONE_C", RawOpportunityFeatures(
                zone_id="ZONE_C", pfz_confidence=0.94, sst_gradient_delta=1.1, chlorophyll_a_mg_m3=3.2, distance_nm=18.0
            )),
        }

        direct_risk = {
            "ZONE_A": calculate_zone_risk("ZONE_A", RawRiskFeatures(
                zone_id="ZONE_A", wave_height_m=2.4, wave_period_sec=8.0, wind_speed_knots=22.0, wind_gust_knots=28.0, swell_height_m=1.8, swell_period_sec=11.0
            )),
            "ZONE_B": calculate_zone_risk("ZONE_B", RawRiskFeatures(
                zone_id="ZONE_B", wave_height_m=1.1, wave_period_sec=6.5, wind_speed_knots=11.0, wind_gust_knots=14.0, swell_height_m=0.7, swell_period_sec=7.5
            )),
            "ZONE_C": calculate_zone_risk("ZONE_C", RawRiskFeatures(
                zone_id="ZONE_C", wave_height_m=1.0, wave_period_sec=6.0, wind_speed_knots=9.5, wind_gust_knots=12.0, swell_height_m=0.6, swell_period_sec=7.0
            )),
        }

        # LangGraph end-to-end execution
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        state = run_marine_agent_state(query, role=RoleType.FISHERMAN)

        opp_res = [a for a in state.get("analytics_results", []) if a.get("operation") == "calculate_opportunity"][0]
        risk_res = [a for a in state.get("analytics_results", []) if a.get("operation") == "calculate_marine_risk"][0]

        opp_data = opp_res.get("result", {}).get("data") or opp_res.get("data", {})
        risk_data = risk_res.get("result", {}).get("data") or risk_res.get("data", {})

        lg_opp = {z["zone_id"]: z for z in opp_data["scored_zones"]}
        lg_risk = {z["zone_id"]: z for z in risk_data["scored_zones"]}

        for zid in ["ZONE_A", "ZONE_B", "ZONE_C"]:
            d_opp_raw = direct_opp[zid].raw_features
            d_risk_raw = direct_risk[zid].raw_features

            lg_opp_raw = lg_opp[zid]["raw_features"]
            lg_risk_raw = lg_risk[zid]["raw_features"]

            # 1. Assert raw Opportunity features match identically
            self.assertEqual(lg_opp_raw["pfz_confidence"], d_opp_raw.pfz_confidence)
            self.assertEqual(lg_opp_raw["sst_gradient_delta"], d_opp_raw.sst_gradient_delta)
            self.assertEqual(lg_opp_raw["chlorophyll_a_mg_m3"], d_opp_raw.chlorophyll_a_mg_m3)
            self.assertEqual(lg_opp_raw["distance_nm"], d_opp_raw.distance_nm)

            # 2. Assert raw Marine Risk features match identically
            self.assertEqual(lg_risk_raw["wave_height_m"], d_risk_raw.wave_height_m)
            self.assertEqual(lg_risk_raw["wind_speed_knots"], d_risk_raw.wind_speed_knots)
            self.assertEqual(lg_risk_raw["wind_gust_knots"], d_risk_raw.wind_gust_knots)
            self.assertEqual(lg_risk_raw["swell_height_m"], d_risk_raw.swell_height_m)

            # 3. Assert calculated opportunity and risk scores match identically
            self.assertAlmostEqual(lg_opp[zid]["opportunity_score"], direct_opp[zid].opportunity_score, places=1)
            self.assertEqual(len(lg_opp[zid]["missing_features"]), 0)

            self.assertAlmostEqual(lg_risk[zid]["risk_score"], direct_risk[zid].risk_score, places=1)
            self.assertEqual(len(lg_risk[zid]["missing_features"]), 0)

    # 17. Determinism test: 10 consecutive identical runs
    def test_17_ten_iteration_end_to_end_determinism(self):
        query = "I'm near Mangalore. Where should I fish tomorrow morning?"
        first_state = run_marine_agent_state(query, role=RoleType.FISHERMAN)
        first_decision = first_state.get("decision")
        first_selected = first_decision.get("selected_zone", {}).get("zone_id")
        first_rank_score = first_decision.get("selected_zone", {}).get("ranking_score")

        for _ in range(9):
            st = run_marine_agent_state(query, role=RoleType.FISHERMAN)
            dec = st.get("decision")
            sel = dec.get("selected_zone", {}).get("zone_id")
            rnk = dec.get("selected_zone", {}).get("ranking_score")
            self.assertEqual(sel, first_selected)
            self.assertAlmostEqual(rnk, first_rank_score, places=2)


if __name__ == "__main__":
    unittest.main()
