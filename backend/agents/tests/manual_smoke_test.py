"""Manual Smoke Test Runner for Phase 8 FastAPI HTTP Endpoints."""

import os
import sys

_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from fastapi.testclient import TestClient
from backend.api.main import app


def run_smoke_tests():
    client = TestClient(app)

    print("======================================================================")
    print("  PHASE 8 MANUAL API SMOKE TEST")
    print("======================================================================")

    # 1. Health
    h_resp = client.get("/health")
    print(f"\n[1] GET /health -> Status {h_resp.status_code}")
    print(f"    Payload: {h_resp.json()}")
    assert h_resp.status_code == 200

    # 2. Fisherman Query
    fish_payload = {
        "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
        "role": "fisherman",
    }
    f_resp = client.post("/chat", json=fish_payload)
    print(f"\n[2] POST /chat (Fisherman) -> Status {f_resp.status_code}")
    assert f_resp.status_code == 200
    f_data = f_resp.json()

    print(f"    Selected Zone:       {f_data['decision']['selected_zone_id']}")
    print(f"    Decision Status:     {f_data['decision']['status']}")
    print(f"    Opportunity (6A):    {f_data['decision']['opportunity_score']:.1f}/100")
    print(f"    Marine Risk (6B):    {f_data['decision']['risk_score']:.1f}/100")
    print(f"    Ranking Score (6D):  {f_data['decision']['ranking_score']:.1f}/100")
    print(f"    Regulatory Status:   {f_data['decision']['regulatory_status']}")
    print(f"    Bearing / Distance:  {f_data['decision']['bearing']} ({f_data['decision']['distance_nm']} NM)")
    print(f"    Evaluated Zones:     {len(f_data['zones'])}")
    for z in f_data['zones']:
        print(f"      * {z['zone_id']:<8} | Status: {z['status']:<16} | Opp: {z['opportunity_score']:>5.1f} | Risk: {z['risk_score']:>5.1f} | Rank: {z.get('ranking_score') or 'N/A'}")
    print(f"    Evidence Items:      {len(f_data['evidence'])}")
    print(f"    Total Pipeline ms:   {f_data['telemetry']['total_pipeline_ms']:.2f} ms")

    # 3. Researcher Query
    res_payload = {
        "query": "Analyze oceanographic conditions and PFZ convergence near Mangalore",
        "role": "researcher",
    }
    r_resp = client.post("/chat", json=res_payload)
    print(f"\n[3] POST /chat (Researcher) -> Status {r_resp.status_code}")
    assert r_resp.status_code == 200
    r_data = r_resp.json()
    print(f"    Persona Role:        {r_data['role']}")
    print(f"    Message Preview:     {r_data['message'][:80]}...")
    print(f"    Visual Badges:       {r_data['visual_payload']['metric_badges']}")
    print(f"    Total Pipeline ms:   {r_data['telemetry']['total_pipeline_ms']:.2f} ms")

    # 4. Legacy Route Alias
    leg_resp = client.post("/api/chat/query", json=fish_payload)
    print(f"\n[4] POST /api/chat/query (Legacy Alias) -> Status {leg_resp.status_code}")
    assert leg_resp.status_code == 200

    print("\n======================================================================")
    print("  ALL MANUAL API SMOKE TESTS PASSED CLEANLY")
    print("======================================================================")


if __name__ == "__main__":
    run_smoke_tests()
