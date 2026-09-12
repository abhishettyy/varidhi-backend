"""Comprehensive test suite for Phase 8: FastAPI HTTP Service & Frontend Contract.

Verifies:
1. GET /health returns 200 with platform status and active LLM provider (zero secrets leaked).
2. POST /chat with valid Fisherman query returns 200 with authoritative structured decision and candidate zones.
3. POST /chat with valid Researcher query returns 200 with researcher persona presentation.
4. Validation failures on empty query or invalid persona return HTTP 422.
5. Structured data authority: selected zone and candidate evaluations match P6 analytics directly.
6. Visual payload (GeoJSON, forecast charts, metric badges) is present and structured.
7. LLM fallback still returns HTTP 200 with structured response and categorical fallback telemetry.
8. No API keys or credentials appear anywhere in response bodies or headers.
9. Phase 6 canonical scores remain unchanged (Zone B: 66.9/34.9, Zone A: 76.6/75.2, Zone C: 84.5/30.8).
10. Backward-compatible /api/chat/query alias works identically.
11. P5 data service routes (/p5/v1/health, /p5/v1/zones) are accessible on the unified app.
"""

import os
import sys
import unittest

# Ensure vendor directory and root are in sys.path
_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from fastapi.testclient import TestClient

from backend.api.main import create_app
from backend.agents.llm.base import LLMConfig
from backend.agents.llm.factory import (
    reset_global_llm_provider,
    set_global_llm_provider,
)
from backend.agents.llm.providers.fake_provider import FakeLLMProvider
from backend.agents.schemas.intent import (
    QueryIntent,
    StructuredLocation,
    StructuredTimeRange,
)


class TestPhase8FastAPIContract(unittest.TestCase):
    """Test suite validating the Phase 8 FastAPI HTTP contract."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def setUp(self):
        reset_global_llm_provider()

    def tearDown(self):
        reset_global_llm_provider()

    # =========================================================================
    # 1. HEALTH ENDPOINT
    # =========================================================================

    def test_01_health_endpoint(self):
        """GET /health returns 200 with status ok and no secret credentials."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "Varidhi Marine Intelligence Platform")
        self.assertIn("version", data)
        self.assertIn("llm_provider", data)

        # Ensure no secrets leak
        raw_text = response.text
        self.assertNotIn("AIza", raw_text)
        self.assertNotIn("sk-", raw_text)
        self.assertNotIn("Bearer", raw_text)

    # =========================================================================
    # 2. VALID FISHERMAN QUERY & STRUCTURED DECISION
    # =========================================================================

    def test_02_post_chat_fisherman_query_success(self):
        """POST /chat with fisherman query returns 200 and authoritative Zone B recommendation."""
        payload = {
            "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
            "role": "fisherman",
        }
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 1. Presentation message
        self.assertIn("message", data)
        self.assertIn("ZONE_B", data["message"])
        self.assertIn("MODERATE", data["message"])

        # 2. Authoritative decision object
        decision = data.get("decision")
        self.assertIsNotNone(decision, "Decision object must be populated")
        self.assertEqual(decision["selected_zone_id"], "ZONE_B")
        self.assertEqual(decision["status"], "SELECTED")
        self.assertAlmostEqual(decision["opportunity_score"], 66.9, places=1)
        self.assertAlmostEqual(decision["risk_score"], 34.9, places=1)
        self.assertAlmostEqual(decision["ranking_score"], 67.31, places=1)
        self.assertEqual(decision["regulatory_status"], "ELIGIBLE")
        self.assertEqual(decision["bearing"], "SSW")
        self.assertIn("Mackerel", decision["species"])

        # 3. Evaluated candidate zones list
        zones = data.get("zones", [])
        self.assertGreaterEqual(len(zones), 3)
        zone_map = {z["zone_id"]: z for z in zones}

        # Check Zone B
        self.assertIn("ZONE_B", zone_map)
        self.assertEqual(zone_map["ZONE_B"]["status"], "SELECTED")

        # Check Zone A (High Risk rejection)
        self.assertIn("ZONE_A", zone_map)
        self.assertEqual(zone_map["ZONE_A"]["status"], "REJECTED_RISK")
        self.assertAlmostEqual(zone_map["ZONE_A"]["opportunity_score"], 76.6, places=1)
        self.assertAlmostEqual(zone_map["ZONE_A"]["risk_score"], 75.2, places=1)

        # Check Zone C (Sanctuary rejection)
        self.assertIn("ZONE_C", zone_map)
        self.assertEqual(zone_map["ZONE_C"]["status"], "REJECTED_LEGAL")
        self.assertAlmostEqual(zone_map["ZONE_C"]["opportunity_score"], 84.5, places=1)
        self.assertAlmostEqual(zone_map["ZONE_C"]["risk_score"], 30.8, places=1)

        # 4. Provenance-preserving evidence
        evidence = data.get("evidence", [])
        self.assertGreater(len(evidence), 0)
        self.assertTrue(any(e["evidence_type"] == "weather_observation" for e in evidence))

        # 5. Visual payload
        vp = data.get("visual_payload")
        self.assertIsNotNone(vp)
        self.assertIsNotNone(vp.get("metric_badges"))
        self.assertEqual(vp.get("focus_zone_id"), "ZONE_B")

        # 6. Query context
        qc = data.get("query_context")
        self.assertIsNotNone(qc)
        self.assertEqual(qc["location"]["name"], "Mangalore")

        # 7. Telemetry & Disclaimer
        telem = data.get("telemetry")
        self.assertIsNotNone(telem)
        self.assertGreater(telem["total_pipeline_ms"], 0.0)

        disclaimer = data.get("disclaimer")
        self.assertIn("synthetic marine demonstration data", disclaimer.lower())

    # =========================================================================
    # 3. VALID RESEARCHER QUERY
    # =========================================================================

    def test_03_post_chat_researcher_query(self):
        """POST /chat with researcher query returns detailed biophysical table and telemetry."""
        payload = {
            "query": "Analyze oceanographic conditions and PFZ convergence near Mangalore",
            "role": "researcher",
        }
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("Biophysical Ocean State", data["message"])
        self.assertIn("Chlorophyll-a Density", data["message"])
        self.assertEqual(data["role"], "researcher")

    # =========================================================================
    # 4. REQUEST VALIDATION FAILURES
    # =========================================================================

    def test_04_validation_error_empty_query(self):
        """POST /chat with empty query string returns 422 Unprocessable Entity."""
        response = self.client.post("/chat", json={"query": "", "role": "fisherman"})
        self.assertEqual(response.status_code, 422)

    def test_05_validation_error_missing_query(self):
        """POST /chat with missing query field returns 422 Unprocessable Entity."""
        response = self.client.post("/chat", json={"role": "fisherman"})
        self.assertEqual(response.status_code, 422)

    def test_06_validation_error_invalid_role(self):
        """POST /chat with unsupported role returns 422 Unprocessable Entity."""
        response = self.client.post("/chat", json={"query": "Where to fish?", "role": "unsupported_role"})
        self.assertEqual(response.status_code, 422)

    # =========================================================================
    # 5. LLM FALLBACK DOES NOT BREAK API
    # =========================================================================

    def test_07_llm_fallback_returns_200_with_telemetry(self):
        """When LLM encounters timeout/error, API gracefully returns 200 with deterministic response."""
        failing_provider = FakeLLMProvider(error_mode="timeout")
        set_global_llm_provider(failing_provider)

        payload = {
            "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
            "role": "fisherman",
        }
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        telem = data.get("telemetry", {})
        self.assertFalse(telem.get("llm_used"))
        self.assertTrue(telem.get("llm_fallback"))
        self.assertEqual(telem.get("llm_fallback_reason"), "API_TIMEOUT")

        # Deterministic outcome is preserved
        self.assertEqual(data["decision"]["selected_zone_id"], "ZONE_B")

    # =========================================================================
    # 6. ZERO CREDENTIAL LEAKAGE
    # =========================================================================

    def test_08_no_credentials_leaked_in_response(self):
        """Verify API response body and headers never leak sensitive API tokens."""
        response = self.client.post("/chat", json={
            "query": "Where should I fish near Mangalore tomorrow?",
            "role": "fisherman",
        })
        self.assertEqual(response.status_code, 200)
        raw_body = response.text

        self.assertNotIn("AIza", raw_body)
        self.assertNotIn("sk-", raw_body)

        for header_name, header_value in response.headers.items():
            self.assertNotIn("AIza", header_value)
            self.assertNotIn("sk-", header_value)

    # =========================================================================
    # 7. BACKWARD COMPATIBILITY ENDPOINT ALIAS
    # =========================================================================

    def test_09_legacy_api_chat_query_alias(self):
        """POST /api/chat/query endpoint alias works identically for existing frontend client."""
        payload = {
            "query": "Where should I fish tomorrow morning near Mangalore?",
            "role": "fisherman",
            "context_zone_id": "ZONE_B",
        }
        response = self.client.post("/api/chat/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check that both new and legacy fields exist
        self.assertIn("message", data)
        self.assertIn("markdown_content", data)
        self.assertEqual(data["message"], data["markdown_content"])
        self.assertEqual(data["decision"]["selected_zone_id"], "ZONE_B")

    # =========================================================================
    # 8. P5 DATA SERVICE ROUTES MOUNTED ON UNIFIED APP
    # =========================================================================

    def test_10_p5_data_service_routes_accessible(self):
        """P5 normalized data routes (/p5/v1/health, /p5/v1/zones) are accessible on unified app."""
        # /p5/v1/health
        resp_p5_health = self.client.get("/p5/v1/health")
        self.assertEqual(resp_p5_health.status_code, 200)
        self.assertEqual(resp_p5_health.json()["status"], "ok")

        # /p5/v1/zones
        resp_p5_zones = self.client.get("/p5/v1/zones")
        self.assertEqual(resp_p5_zones.status_code, 200)
        zones_data = resp_p5_zones.json()
        self.assertIn("zones", zones_data)
        self.assertGreaterEqual(len(zones_data["zones"]), 3)

    # =========================================================================
    # 9. CANONICAL SCENARIO FIXTURE CONSISTENCY REGRESSION
    # =========================================================================

    def test_11_canonical_mangalore_fixture_consistency_regression(self):
        """
        Verifies exact 1-to-1 consistency between the canonical Mangalore fixture
        and API serialization across:
        - decision
        - zones[]
        - visual_payload.map_features_geojson
        """
        payload = {
            "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
            "role": "fisherman",
        }
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 1. Canonical Expected Dictionary (Single Source of Truth)
        CANONICAL_ZONES = {
            "ZONE_A": {
                "latitude": 12.95,
                "longitude": 74.80,
                "distance_nm": 14.5,
                "bearing": "WNW",
                "opportunity_score": 76.6,
                "risk_score": 75.2,
                "regulatory_status": "ELIGIBLE",
                "status": "REJECTED_RISK",
                "ranking_score": None,
                "species": ["Pelagic Tuna", "Kingfish"],
            },
            "ZONE_B": {
                "latitude": 12.90,
                "longitude": 74.95,
                "distance_nm": 8.2,
                "bearing": "SSW",
                "opportunity_score": 66.9,
                "risk_score": 34.9,
                "regulatory_status": "ELIGIBLE",
                "status": "SELECTED",
                "ranking_score": 67.31,
                "species": ["Mackerel", "Sardines"],
            },
            "ZONE_C": {
                "latitude": 12.82,
                "longitude": 75.05,
                "distance_nm": 18.0,
                "bearing": "SSE",
                "opportunity_score": 84.5,
                "risk_score": 30.8,
                "regulatory_status": "BLOCKED",
                "status": "REJECTED_LEGAL",
                "ranking_score": None,
                "species": ["Yellowfin Tuna", "Barracuda"],
            },
        }

        # 2. Verify zones[] array consistency
        zones_list = data.get("zones", [])
        self.assertEqual(len(zones_list), 3, "Must return exactly 3 evaluated scenario zones")
        zone_map = {z["zone_id"]: z for z in zones_list}

        for zid, exp in CANONICAL_ZONES.items():
            self.assertIn(zid, zone_map, f"Missing candidate zone {zid}")
            act = zone_map[zid]

            # Coordinates
            self.assertAlmostEqual(act["latitude"], exp["latitude"], places=2, msg=f"{zid} latitude mismatch")
            self.assertAlmostEqual(act["longitude"], exp["longitude"], places=2, msg=f"{zid} longitude mismatch")

            # Distance & Bearing
            self.assertAlmostEqual(act["distance_nm"], exp["distance_nm"], places=1, msg=f"{zid} distance mismatch")
            self.assertEqual(act["bearing"], exp["bearing"], f"{zid} bearing mismatch")

            # Opportunity & Risk Scores
            self.assertAlmostEqual(act["opportunity_score"], exp["opportunity_score"], places=1, msg=f"{zid} opp score mismatch")
            self.assertAlmostEqual(act["risk_score"], exp["risk_score"], places=1, msg=f"{zid} risk score mismatch")

            # Regulatory & Decision Status
            self.assertEqual(act["regulatory_status"], exp["regulatory_status"], f"{zid} regulatory status mismatch")
            self.assertEqual(act["status"], exp["status"], f"{zid} decision status mismatch")

            # Ranking Score
            if exp["ranking_score"] is not None:
                self.assertAlmostEqual(act["ranking_score"], exp["ranking_score"], places=1, msg=f"{zid} ranking score mismatch")
            else:
                self.assertIsNone(act["ranking_score"], f"{zid} must have null ranking score")

            # Species
            for sp in exp["species"]:
                self.assertIn(sp, act["species"], f"{zid} species missing {sp}")

        # 3. Verify decision object consistency with Zone B
        decision = data["decision"]
        self.assertEqual(decision["selected_zone_id"], "ZONE_B")
        self.assertEqual(decision["status"], "SELECTED")
        self.assertAlmostEqual(decision["latitude"], 12.90, places=2)
        self.assertAlmostEqual(decision["longitude"], 74.95, places=2)
        self.assertAlmostEqual(decision["distance_nm"], 8.2, places=1)
        self.assertEqual(decision["bearing"], "SSW")
        self.assertAlmostEqual(decision["opportunity_score"], 66.9, places=1)
        self.assertAlmostEqual(decision["risk_score"], 34.9, places=1)
        self.assertAlmostEqual(decision["ranking_score"], 67.31, places=1)
        self.assertEqual(decision["regulatory_status"], "ELIGIBLE")

        # 4. Verify visual_payload.map_features_geojson consistency
        geojson = data["visual_payload"]["map_features_geojson"]
        self.assertIsNotNone(geojson)
        self.assertEqual(geojson["type"], "FeatureCollection")
        features = geojson["features"]
        self.assertEqual(len(features), 3)

        feat_map = {f["properties"]["zone_id"]: f for f in features}
        for zid, exp in CANONICAL_ZONES.items():
            self.assertIn(zid, feat_map, f"GeoJSON missing feature {zid}")
            f = feat_map[zid]
            coords = f["geometry"]["coordinates"]
            # GeoJSON coordinates are [longitude, latitude]
            self.assertAlmostEqual(coords[0], exp["longitude"], places=2, msg=f"{zid} GeoJSON lon mismatch")
            self.assertAlmostEqual(coords[1], exp["latitude"], places=2, msg=f"{zid} GeoJSON lat mismatch")

            props = f["properties"]
            self.assertEqual(props["status"], exp["status"])
            self.assertEqual(props["recommended"], (zid == "ZONE_B"))
            self.assertAlmostEqual(props["opportunity_score"], exp["opportunity_score"], places=1)
            self.assertAlmostEqual(props["risk_score"], exp["risk_score"], places=1)
            self.assertAlmostEqual(props["distance_nm"], exp["distance_nm"], places=1)


if __name__ == "__main__":
    unittest.main()
