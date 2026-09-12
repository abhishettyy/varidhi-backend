"""Comprehensive test suite for Phase 7: Real LLM Integration & Evidence-Grounded Response.

Verifies:
1. LLM-backed query understanding with Pydantic/schema validation.
2. 100% deterministic fallback on invalid JSON, schema mismatch, timeouts, and missing credentials.
3. Provenance and structured evidence assembly.
4. Persona-tailored response generation (Fisherman vs Researcher).
5. Guardrail preservation of P6 multi-criteria decision and safety alert.
6. Full end-to-end LangGraph execution with Mock LLM provider and error simulation.
7. Zero network dependency during testing.
"""

import asyncio
import unittest
from typing import Any, Dict

from backend.agents.graph.builder import build_marine_agent_graph
from backend.agents.llm.base import (
    LLMConfig,
    LLMError,
    LLMAPIKeyMissingError,
    LLMTimeoutError,
    LLMResponseParsingError,
    LLMSchemaValidationError,
)
from backend.agents.llm.factory import (
    get_llm_provider,
    set_global_llm_provider,
    reset_global_llm_provider,
)
from backend.agents.llm.providers.fake_provider import FakeLLMProvider, MockLLMProvider
from backend.agents.llm.providers.gemini_provider import GeminiLLMProvider
from backend.agents.llm.providers.openai_provider import OpenAILLMProvider
from backend.agents.nodes.evidence_assembly import evidence_assembly_node
from backend.agents.nodes.response_generation import response_generation_node
from backend.agents.nodes.understand_query import understand_query_node
from backend.agents.schemas.intent import QueryIntent, StructuredLocation, StructuredTimeRange
from backend.agents.schemas.response import AgentResponse, RoleType, SafetySeverity


class TestPhase7LLMProviderFactory(unittest.TestCase):
    """Unit tests for LLM provider abstractions, factory, and error hierarchy."""

    def tearDown(self):
        reset_global_llm_provider()

    def test_default_mock_provider_creation(self):
        """Factory creates MockLLMProvider by default."""
        provider = get_llm_provider(LLMConfig(provider="mock"))
        self.assertIsInstance(provider, FakeLLMProvider)
        self.assertEqual(provider.provider_name, "mock")

    def test_global_provider_override(self):
        """Global provider override is respected by get_llm_provider."""
        custom_mock = FakeLLMProvider(canned_text="Custom Output")
        set_global_llm_provider(custom_mock)
        retrieved = get_llm_provider()
        self.assertIs(retrieved, custom_mock)
        reset_global_llm_provider()
        self.assertIsNot(get_llm_provider(), custom_mock)

    def test_gemini_missing_api_key_raises_error(self):
        """GeminiLLMProvider raises LLMAPIKeyMissingError if API key is not set."""
        cfg = LLMConfig(provider="gemini", model="gemini-1.5-flash", api_key=None)
        gemini = GeminiLLMProvider(cfg)
        gemini.config.api_key = None

        with self.assertRaises(LLMAPIKeyMissingError):
            gemini._get_api_key()

    def test_openai_missing_api_key_raises_error(self):
        """OpenAILLMProvider raises LLMAPIKeyMissingError if API key is not set."""
        cfg = LLMConfig(provider="openai", model="gpt-4o-mini", api_key=None)
        openai = OpenAILLMProvider(cfg)
        openai.config.api_key = None

        with self.assertRaises(LLMAPIKeyMissingError):
            openai._get_api_key()

    def test_fake_provider_error_modes(self):
        """FakeLLMProvider raises expected error types for each configured error mode."""
        loop = asyncio.new_event_loop()
        try:
            # Timeout
            p_timeout = FakeLLMProvider(error_mode="timeout")
            with self.assertRaises(LLMTimeoutError):
                loop.run_until_complete(p_timeout.generate_text("test"))

            # Invalid JSON
            p_json = FakeLLMProvider(error_mode="invalid_json")
            with self.assertRaises(LLMResponseParsingError):
                loop.run_until_complete(p_json.generate_structured("test", QueryIntent))

            # Schema Error
            p_schema = FakeLLMProvider(error_mode="schema_error")
            with self.assertRaises(LLMSchemaValidationError):
                loop.run_until_complete(p_schema.generate_structured("test", QueryIntent))

            # Missing Key
            p_key = FakeLLMProvider(error_mode="missing_key")
            with self.assertRaises(LLMAPIKeyMissingError):
                loop.run_until_complete(p_key.generate_text("test"))
        finally:
            loop.close()


class TestPhase7QueryUnderstandingLLM(unittest.TestCase):
    """Unit tests for LLM-backed query understanding and deterministic fallback."""

    def tearDown(self):
        reset_global_llm_provider()

    def test_llm_query_understanding_success(self):
        """Valid LLM structured extraction successfully extracts QueryIntent and enriches coordinates."""
        loop = asyncio.new_event_loop()
        try:
            canned_data = {
                "intent": "FISHING_RECOMMENDATION",
                "confidence": 0.98,
                "location": {
                    "name": "Mangalore",
                    "latitude": None,  # Will be enriched by node
                    "longitude": None,
                },
                "time_range": {
                    "raw": "tomorrow morning",
                    "relative_day": "tomorrow",
                    "period": "morning",
                    "forecast_horizon_hours": 36,
                },
                "variables": ["SST", "CHLOROPHYLL", "PFZ", "WIND", "WAVE"],
                "vessel": {"type": "motorized boat"},
                "route": None,
                "constraints": {"max_wave_height_m": 2.0},
            }
            mock_llm = FakeLLMProvider(canned_structured=canned_data)
            set_global_llm_provider(mock_llm)

            state = {"query": "Where can I fish near Mangalore tomorrow morning with my motorized boat?"}
            result = loop.run_until_complete(understand_query_node(state))

            self.assertTrue(result["llm_used"])
            self.assertFalse(result["llm_fallback"])
            self.assertEqual(result["intent"], "FISHING_RECOMMENDATION")
            self.assertEqual(result["location"]["name"], "Mangalore")
            self.assertEqual(result["location"]["latitude"], 12.8681)
            self.assertEqual(result["location"]["longitude"], 74.8427)
            self.assertEqual(result["location"]["harbor"], "Mangalore Old Port")
            self.assertEqual(result["vessel"]["type"], "motorized boat")
            self.assertEqual(result["constraints"]["max_wave_height_m"], 2.0)
        finally:
            loop.close()

    def test_llm_query_understanding_invalid_json_fallback(self):
        """LLM malformed JSON triggers automatic fallback to deterministic parser."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(error_mode="invalid_json")
            set_global_llm_provider(mock_llm)

            state = {"query": "I am near Mangalore. Where should I fish tomorrow morning?"}
            result = loop.run_until_complete(understand_query_node(state))

            self.assertFalse(result["llm_used"])
            self.assertTrue(result["llm_fallback"])
            self.assertIn("llm_fallback_reason", result)
            # Deterministic results should still be correct
            self.assertEqual(result["intent"], "FISHING_RECOMMENDATION")
            self.assertEqual(result["location"]["name"], "Mangalore")
            self.assertEqual(result["location"]["latitude"], 12.8681)
        finally:
            loop.close()

    def test_llm_query_understanding_timeout_fallback(self):
        """LLM timeout triggers automatic fallback to deterministic parser."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(error_mode="timeout")
            set_global_llm_provider(mock_llm)

            state = {"query": "Is this point inside a restricted marine zone?"}
            result = loop.run_until_complete(understand_query_node(state))

            self.assertFalse(result["llm_used"])
            self.assertTrue(result["llm_fallback"])
            self.assertEqual(result["intent"], "GEOFENCE_QUERY")
        finally:
            loop.close()

    def test_llm_query_understanding_missing_key_fallback(self):
        """Missing API key triggers smooth fallback without unhandled exception."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(error_mode="missing_key")
            set_global_llm_provider(mock_llm)

            state = {"query": "What is the sea surface temperature near Kochi?"}
            result = loop.run_until_complete(understand_query_node(state))

            self.assertFalse(result["llm_used"])
            self.assertTrue(result["llm_fallback"])
            self.assertEqual(result["location"]["name"], "Kochi")
        finally:
            loop.close()


class TestPhase7ResponseGeneration(unittest.TestCase):
    """Unit tests for evidence assembly and persona-tailored response generation."""

    def tearDown(self):
        reset_global_llm_provider()

    def test_fisherman_response_generation(self):
        """Fisherman persona generates concise actionable advice."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(
                canned_text="### Marine Advisory for Mangalore\n\n**Safety Status:** SAFE\n\nRecommended: ZONE_B (8.2 NM SSW)"
            )
            set_global_llm_provider(mock_llm)

            state = {
                "query": "Where to fish near Mangalore tomorrow morning?",
                "user_type": "fisherman",
                "intent": "FISHING_RECOMMENDATION",
                "location": {"name": "Mangalore"},
                "decision": {
                    "selected_zone": {
                        "zone_id": "ZONE_B",
                        "distance_nm": 8.2,
                        "bearing": "SSW",
                        "opportunity_score": 66.9,
                        "risk_score": 34.9,
                        "ranking_score": 67.31,
                    },
                    "rejected_zones": [
                        {"zone_id": "ZONE_C", "status": "REJECTED_LEGAL", "reasons": ["Sanctuary"]},
                        {"zone_id": "ZONE_A", "status": "REJECTED_RISK", "reasons": ["Wave height"]},
                    ],
                },
            }

            result = loop.run_until_complete(response_generation_node(state))
            final_resp: AgentResponse = result["final_response"]

            self.assertIsInstance(final_resp, AgentResponse)
            self.assertEqual(final_resp.role, RoleType.FISHERMAN)
            self.assertTrue(result["llm_used"])
            self.assertIn("ZONE_B", final_resp.markdown_content)
            self.assertIsNotNone(final_resp.visual_payload)
            self.assertIsNotNone(final_resp.visual_payload.map_features_geojson)
        finally:
            loop.close()

    def test_researcher_response_template_fallback(self):
        """Researcher persona fallback generates comprehensive markdown tables."""
        loop = asyncio.new_event_loop()
        try:
            # Force fallback mode
            mock_llm = FakeLLMProvider(error_mode="timeout")
            set_global_llm_provider(mock_llm)

            state = {
                "query": "Analyze Mangalore fishing zones",
                "user_type": "researcher",
                "intent": "FISHING_RECOMMENDATION",
                "location": {"name": "Mangalore"},
                "decision": {
                    "selected_zone": {
                        "zone_id": "ZONE_B",
                        "opportunity_score": 66.9,
                        "risk_score": 34.9,
                        "ranking_score": 67.31,
                    },
                    "ranked_zones": [
                        {"zone_id": "ZONE_B", "opportunity_score": 66.9, "risk_score": 34.9, "ranking_score": 67.31, "status": "ELIGIBLE"},
                    ],
                    "rejected_zones": [
                        {"zone_id": "ZONE_C", "opportunity_score": 84.5, "risk_score": 30.8, "status": "REJECTED_LEGAL", "reasons": ["Sanctuary"]},
                        {"zone_id": "ZONE_A", "opportunity_score": 76.6, "risk_score": 75.2, "status": "REJECTED_RISK", "reasons": ["Wave > 2.0m"]},
                    ],
                },
            }

            result = loop.run_until_complete(response_generation_node(state))
            final_resp: AgentResponse = result["final_response"]

            self.assertEqual(final_resp.role, RoleType.RESEARCHER)
            self.assertFalse(result["llm_used"])
            self.assertTrue(result["llm_fallback"])
            # Verify markdown table generation
            self.assertIn("## 1. Biophysical Ocean State", final_resp.markdown_content)
            self.assertIn("## 3. Multi-Engine Decision Synthesis & Zone Ranking", final_resp.markdown_content)
            self.assertIn("| `ZONE_B` |", final_resp.markdown_content)
            self.assertIn("| `ZONE_C` |", final_resp.markdown_content)
        finally:
            loop.close()

    def test_p6_decision_invariants_preserved(self):
        """P6 selected zone is never overridden by response node regardless of LLM mode."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(canned_text="LLM Generated Summary")
            set_global_llm_provider(mock_llm)

            state = {
                "query": "Fishing advice",
                "decision": {
                    "selected_zone": {"zone_id": "ZONE_B", "ranking_score": 67.31},
                },
            }

            result = loop.run_until_complete(response_generation_node(state))
            self.assertEqual(result["decision"]["selected_zone"]["zone_id"], "ZONE_B")
            self.assertIn("ZONE_B", result["final_response"].visual_payload.metric_badges["Recommended Zone"])
        finally:
            loop.close()


class TestPhase7EndToEndLangGraphIntegration(unittest.TestCase):
    """End-to-end integration tests through the full LangGraph pipeline."""

    def tearDown(self):
        reset_global_llm_provider()

    def test_full_graph_with_mock_llm_provider(self):
        """Executes full LangGraph pipeline with MockLLMProvider and verifies full execution."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider()
            set_global_llm_provider(mock_llm)

            graph = build_marine_agent_graph()
            initial_state = {
                "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                "user_type": "fisherman",
            }

            final_state = loop.run_until_complete(graph.ainvoke(initial_state))

            # Verify entire pipeline execution
            self.assertIn("final_response", final_state)
            self.assertIn("decision", final_state)
            self.assertIn("evidence_bundle", final_state)

            # Verify deterministic P6 decision
            decision = final_state["decision"]
            selected = decision["selected_zone"]
            self.assertEqual(selected["zone_id"], "ZONE_B")
            self.assertAlmostEqual(selected["opportunity_score"], 66.9, places=1)
            self.assertAlmostEqual(selected["risk_score"], 34.9, places=1)
            self.assertAlmostEqual(selected["ranking_score"], 67.31, places=1)

            # Verify rejected zones
            rejected_ids = [z["zone_id"] for z in decision["rejected_zones"]]
            self.assertIn("ZONE_A", rejected_ids)
            self.assertIn("ZONE_C", rejected_ids)
        finally:
            loop.close()

    def test_full_graph_with_simulated_llm_timeout_fallback(self):
        """Executes full LangGraph pipeline when LLM times out, ensuring 100% resilient fallback."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider(error_mode="timeout")
            set_global_llm_provider(mock_llm)

            graph = build_marine_agent_graph()
            initial_state = {
                "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                "user_type": "fisherman",
            }

            final_state = loop.run_until_complete(graph.ainvoke(initial_state))

            # Pipeline must complete successfully with fallback
            self.assertIn("final_response", final_state)
            self.assertTrue(final_state.get("llm_fallback", True))
            decision = final_state["decision"]
            self.assertEqual(decision["selected_zone"]["zone_id"], "ZONE_B")
        finally:
            loop.close()

    def test_full_graph_10_run_determinism(self):
        """Verifies 10 consecutive full graph runs produce identical deterministic decisions."""
        loop = asyncio.new_event_loop()
        try:
            mock_llm = FakeLLMProvider()
            set_global_llm_provider(mock_llm)

            graph = build_marine_agent_graph()
            initial_state = {
                "query": "I am near Mangalore. Where should I fish tomorrow morning?",
                "user_type": "fisherman",
            }

            results = []
            for _ in range(10):
                res = loop.run_until_complete(graph.ainvoke(dict(initial_state)))
                sel = res["decision"]["selected_zone"]
                results.append((sel["zone_id"], round(sel["opportunity_score"], 2), round(sel["risk_score"], 2), round(sel["ranking_score"], 2)))

            # All 10 runs must match
            self.assertEqual(len(set(results)), 1)
            self.assertEqual(results[0], ("ZONE_B", 66.9, 34.9, 67.31))
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()
