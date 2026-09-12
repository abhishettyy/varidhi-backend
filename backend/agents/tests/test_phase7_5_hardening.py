"""Comprehensive test suite for Phase 7.5 Hardening Pass.

Verifies:
1. Categorical error classification and sanitization (no leaked API keys).
2. Explicit LLM status and fallback telemetry across the pipeline.
3. Monotonic latency telemetry at node and tool levels.
4. Risk severity boundaries (0-30 LOW, >30-60 MODERATE, >60-80 HIGH, >80-100 SEVERE).
5. Zone B (34.9) presents as MODERATE risk and favorable relative to alternatives (no certified safety claim).
6. Synthetic marine demonstration disclaimer on all persona responses.
7. Unaltered P6 deterministic numerical parity through full LangGraph pipeline.
"""

import asyncio
import unittest
from typing import Any, Dict

from backend.agents.graph.builder import build_marine_agent_graph
from backend.agents.llm.base import (
    LLMConfig,
    LLMAPIKeyMissingError,
    LLMTimeoutError,
    LLMResponseParsingError,
    LLMSchemaValidationError,
    classify_llm_error,
)
from backend.agents.llm.factory import (
    get_llm_provider,
    set_global_llm_provider,
    reset_global_llm_provider,
)
from backend.agents.llm.providers.fake_provider import FakeLLMProvider
from backend.agents.nodes.evidence_assembly import evidence_assembly_node
from backend.agents.nodes.response_generation import response_generation_node
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.schemas.intent import QueryIntent, StructuredLocation, StructuredTimeRange
from backend.agents.schemas.response import AgentResponse, RoleType, SafetySeverity


class TestPhase75Hardening(unittest.TestCase):
    """Test suite verifying all Phase 7.5 hardening invariants."""

    def setUp(self):
        reset_global_llm_provider()

    def tearDown(self):
        reset_global_llm_provider()

    # =========================================================================
    # 1. ERROR CLASSIFICATION & SANITIZATION
    # =========================================================================

    def test_classify_llm_error_categories(self):
        """classify_llm_error maps exception types to safe categorical codes."""
        self.assertEqual(classify_llm_error(LLMAPIKeyMissingError("Missing key")), "AUTHENTICATION_ERROR")
        self.assertEqual(classify_llm_error(LLMTimeoutError("Request timed out")), "API_TIMEOUT")
        self.assertEqual(classify_llm_error(LLMResponseParsingError("Bad json")), "MALFORMED_OUTPUT")
        self.assertEqual(classify_llm_error(LLMSchemaValidationError("Missing field")), "SCHEMA_VALIDATION_ERROR")
        self.assertEqual(classify_llm_error(ConnectionError("getaddrinfo failed")), "NETWORK_UNREACHABLE")
        self.assertEqual(classify_llm_error(RuntimeError("Unknown internal failure")), "UPSTREAM_API_ERROR")

    def test_classify_llm_error_sanitizes_secrets(self):
        """classify_llm_error never leaks raw error strings or embedded API keys."""
        leaky_error = Exception("Failed call with key AIzaSyA1234567890abcdef and secret sk-1234567890abcdef")
        code = classify_llm_error(leaky_error)
        self.assertNotIn("AIza", code)
        self.assertNotIn("sk-", code)
        self.assertIn(code, ["AUTHENTICATION_ERROR", "NETWORK_UNREACHABLE", "API_TIMEOUT", "SCHEMA_VALIDATION_ERROR", "MALFORMED_OUTPUT", "UPSTREAM_API_ERROR"])

    # =========================================================================
    # 2. EXPLICIT LLM STATUS & TELEMETRY
    # =========================================================================

    def test_understand_query_llm_fallback_telemetry(self):
        """When LLM provider raises error, understand_query records fallback and safe code."""
        fake_failing_llm = FakeLLMProvider(error_mode="timeout")
        set_global_llm_provider(fake_failing_llm)

        state: Dict[str, Any] = {
            "query": "Where should I fish near Mangalore tomorrow morning?",
            "use_llm": True,
        }

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(understand_query_node(state))
        finally:
            loop.close()

        self.assertFalse(result["llm_used"])
        self.assertTrue(result["llm_fallback"])
        self.assertEqual(result["llm_fallback_reason"], "API_TIMEOUT")
        self.assertEqual(str(result["intent"]).lower(), "fishing_recommendation")
        self.assertEqual(result["location"]["name"], "Mangalore")

    def test_understand_query_llm_success_telemetry(self):
        """When structured LLM extraction succeeds, understand_query records llm_used=True."""
        canned_intent = QueryIntent(
            intent="fishing_recommendation",
            confidence=0.98,
            location=StructuredLocation(name="Mangalore", latitude=12.8681, longitude=74.8427),
            time_range=StructuredTimeRange(raw="tomorrow morning", relative_day="tomorrow", period="morning"),
            variables=["sea_surface_temperature", "chlorophyll"],
        )
        fake_success_llm = FakeLLMProvider(canned_structured=canned_intent.model_dump())
        set_global_llm_provider(fake_success_llm)

        state: Dict[str, Any] = {
            "query": "Where should I fish near Mangalore tomorrow morning?",
            "use_llm": True,
        }

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(understand_query_node(state))
        finally:
            loop.close()

        self.assertTrue(result["llm_used"])
        self.assertFalse(result["llm_fallback"])
        self.assertEqual(str(result["intent"]).lower(), "fishing_recommendation")
        self.assertEqual(result["location"]["name"], "Mangalore")

    # =========================================================================
    # 3. LATENCY TELEMETRY
    # =========================================================================

    def test_full_pipeline_latency_telemetry(self):
        """End-to-end LangGraph execution populates complete latency telemetry breakdown."""
        graph = build_marine_agent_graph()
        loop = asyncio.new_event_loop()
        try:
            final_state = loop.run_until_complete(
                graph.ainvoke({
                    "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                    "user_type": "fisherman",
                })
            )
        finally:
            loop.close()

        telem = final_state.get("latency_telemetry")
        self.assertIsNotNone(telem, "latency_telemetry must be present in final state")
        self.assertIn("understand_query_ms", telem)
        self.assertIn("planner_ms", telem)
        self.assertIn("tool_selection_ms", telem)
        self.assertIn("executor_ms", telem)
        self.assertIn("evidence_assembly_ms", telem)
        self.assertIn("response_generation_ms", telem)
        self.assertIn("total_pipeline_ms", telem)

        self.assertGreater(telem["total_pipeline_ms"], 0.0)
        self.assertGreaterEqual(telem["understand_query_ms"], 0.0)
        self.assertGreaterEqual(telem["executor_ms"], 0.0)

        # Step-level tool timings
        tool_timings = telem.get("tool_timings_ms")
        self.assertIsNotNone(tool_timings, "tool_timings_ms dictionary must be present")
        self.assertGreater(len(tool_timings), 0)

    # =========================================================================
    # 4. RISK SEVERITY BOUNDS & SEMANTICS
    # =========================================================================

    def test_risk_severity_boundary_mapping(self):
        """Verify risk score mappings: 0-30 LOW, >30-60 MODERATE, >60-80 HIGH, >80-100 SEVERE."""
        loop = asyncio.new_event_loop()
        try:
            # Score 25.0 -> LOW (SAFE_GREEN)
            state_low = {
                "query": "Test low risk",
                "user_type": "fisherman",
                "decision": {"selected_zone": {"zone_id": "ZONE_LOW", "risk_score": 25.0}},
            }
            res_low = loop.run_until_complete(response_generation_node(state_low))
            self.assertEqual(res_low["final_response"].safety_alert.severity, SafetySeverity.SAFE_GREEN)

            # Score 34.9 (Zone B) -> MODERATE (CAUTION_YELLOW)
            state_mod = {
                "query": "Test moderate risk",
                "user_type": "fisherman",
                "decision": {"selected_zone": {"zone_id": "ZONE_B", "risk_score": 34.9}},
            }
            res_mod = loop.run_until_complete(response_generation_node(state_mod))
            self.assertEqual(res_mod["final_response"].safety_alert.severity, SafetySeverity.CAUTION_YELLOW)

            # Score 75.2 (Zone A) -> HIGH (WARNING_ORANGE)
            state_high = {
                "query": "Test high risk",
                "user_type": "fisherman",
                "decision": {"selected_zone": {"zone_id": "ZONE_A", "risk_score": 75.2}},
            }
            res_high = loop.run_until_complete(response_generation_node(state_high))
            self.assertEqual(res_high["final_response"].safety_alert.severity, SafetySeverity.WARNING_ORANGE)

            # Score 88.0 -> SEVERE (DANGER_RED)
            state_sev = {
                "query": "Test severe risk",
                "user_type": "fisherman",
                "decision": {"selected_zone": {"zone_id": "ZONE_SEV", "risk_score": 88.0}},
            }
            res_sev = loop.run_until_complete(response_generation_node(state_sev))
            self.assertEqual(res_sev["final_response"].safety_alert.severity, SafetySeverity.DANGER_RED)
        finally:
            loop.close()

    def test_zone_b_moderate_risk_presentation(self):
        """Zone B (34.9) response presents as MODERATE risk and favorable relative to alternatives."""
        loop = asyncio.new_event_loop()
        try:
            graph = build_marine_agent_graph()
            final_state = loop.run_until_complete(
                graph.ainvoke({
                    "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                    "user_type": "fisherman",
                })
            )
        finally:
            loop.close()

        resp: AgentResponse = final_state["final_response"]
        self.assertEqual(resp.safety_alert.severity, SafetySeverity.CAUTION_YELLOW)
        self.assertIn("Moderate", resp.safety_alert.title)

        md = resp.markdown_content
        self.assertIn("MODERATE", md)
        self.assertIn("favorable relative to evaluated alternatives", md)
        # Verify no certified safety claim
        self.assertNotIn("officially cleared", md.lower())
        self.assertNotIn("statutory clearance", md.lower())

    # =========================================================================
    # 5. SYNTHETIC DATA DISCLOSURE
    # =========================================================================

    def test_synthetic_data_disclosure_in_all_personas(self):
        """All persona responses (fisherman, researcher, general) include synthetic data disclosure."""
        graph = build_marine_agent_graph()
        loop = asyncio.new_event_loop()
        try:
            for role in ["fisherman", "researcher", "general"]:
                state = loop.run_until_complete(
                    graph.ainvoke({
                        "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                        "user_type": role,
                    })
                )
                resp: AgentResponse = state["final_response"]
                self.assertIn(
                    "synthetic marine demonstration data",
                    resp.markdown_content.lower(),
                    f"Persona {role} must include synthetic data disclosure"
                )
        finally:
            loop.close()

    # =========================================================================
    # 6. P6 NUMERICAL PARITY PRESERVATION
    # =========================================================================

    def test_p6_canonical_numerical_parity_preserved(self):
        """Hardened pipeline maintains exact Phase 6 canonical values for Mangalore fixture."""
        graph = build_marine_agent_graph()
        loop = asyncio.new_event_loop()
        try:
            state = loop.run_until_complete(
                graph.ainvoke({
                    "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                    "user_type": "fisherman",
                })
            )
        finally:
            loop.close()

        decision = state["decision"]
        selected = decision["selected_zone"]
        self.assertEqual(selected["zone_id"], "ZONE_B")
        self.assertAlmostEqual(selected["opportunity_score"], 66.9, places=1)
        self.assertAlmostEqual(selected["risk_score"], 34.9, places=1)

        ranked = decision["ranked_zones"]
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["zone_id"], "ZONE_B")

        rejected = decision["rejected_zones"]
        rej_map = {r["zone_id"]: r for r in rejected}
        self.assertIn("ZONE_A", rej_map)
        self.assertIn("ZONE_C", rej_map)
        self.assertAlmostEqual(rej_map["ZONE_A"]["opportunity_score"], 76.6, places=1)
        self.assertAlmostEqual(rej_map["ZONE_A"]["risk_score"], 75.2, places=1)
        self.assertAlmostEqual(rej_map["ZONE_C"]["opportunity_score"], 84.5, places=1)
        self.assertAlmostEqual(rej_map["ZONE_C"]["risk_score"], 30.8, places=1)


if __name__ == "__main__":
    unittest.main()
