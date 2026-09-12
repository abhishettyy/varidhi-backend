"""CLI Runner & Telemetry Inspector for Varidhi Marine Intelligence Platform.

Usage:
    python run_marine_query.py
    python run_marine_query.py "Where can I fish near Mangalore tomorrow morning?" --role fisherman
    python run_marine_query.py "Analyze oceanographic conditions and PFZ convergence near Mangalore" --role researcher
"""

import argparse
import asyncio
import json
import os
import sys
import time

# Handle UTF-8 encoding on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.agents.graph.builder import build_marine_agent_graph
from backend.agents.llm.factory import get_llm_config_from_env, get_llm_provider
from backend.agents.schemas.response import AgentResponse, RoleType


def format_header(title: str) -> str:
    line = "=" * 70
    return f"\n{line}\n  {title}\n{line}"


def format_sub_header(title: str) -> str:
    line = "-" * 50
    return f"\n{title}\n{line}"


async def run_query(query_text: str, role: str, verbose: bool = True):
    print(format_header("VARIDHI MARINE INTELLIGENCE PLATFORM - AGENT TELEMETRY"))

    # 1. Configuration & LLM Provider Status
    cfg = get_llm_config_from_env()
    provider = get_llm_provider()
    has_key = bool(cfg.api_key and cfg.api_key.strip())
    masked_key = (cfg.api_key[:4] + "..." + cfg.api_key[-4:]) if has_key else "None (Mock/Offline)"

    print(format_sub_header("[SYSTEM CONFIGURATION & LLM PROVIDER]"))
    print(f"* Configured Provider: {cfg.provider.upper()}")
    print(f"* Configured Model:    {cfg.model}")
    print(f"* API Key Loaded:      {'YES (' + masked_key + ')' if has_key else 'NO (Running in offline/mock fallback)'}")
    print(f"* Target Persona:      {role.upper()}")
    print(f"* Query:               \"{query_text}\"")

    # 2. Build & Execute LangGraph Workflow
    print(format_sub_header("[EXECUTING LANGGRAPH PIPELINE]"))
    start_time = time.perf_counter()

    graph = build_marine_agent_graph()
    initial_state = {
        "query": query_text,
        "user_type": role,
    }

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        print(f"\n[!] Execution Error: {e}")
        import traceback
        traceback.print_exc()
        return

    wall_duration_ms = (time.perf_counter() - start_time) * 1000

    # 3. Telemetry: Phase 7A Query Understanding & LLM Status
    print(format_sub_header("[PHASE 7A: QUERY UNDERSTANDING & LLM EXTRACTION]"))
    llm_used = final_state.get("llm_used", False)
    llm_fallback = final_state.get("llm_fallback", False)
    fallback_reason = final_state.get("llm_fallback_reason")

    if llm_used:
        llm_status_badge = f"LLM SUCCESS (Provider: {cfg.provider.upper()}, Model: {cfg.model})"
    elif llm_fallback:
        llm_status_badge = f"LLM FALLBACK (Reason: {fallback_reason or 'UNKNOWN'}, Parser: Rule-Based Fallback)"
    else:
        llm_status_badge = "RULE-BASED DETERMINISTIC PARSER"

    print(f"* LLM Status:      {llm_status_badge}")
    print(f"* Detected Intent: {final_state.get('intent')} (Confidence: {final_state.get('confidence')})")

    loc = final_state.get("location") or {}
    if loc:
        coords_str = f"({loc.get('latitude')}, {loc.get('longitude')})" if loc.get("latitude") else "Unresolved"
        harbor_str = f" | Harbor: {loc.get('harbor')}" if loc.get("harbor") else ""
        print(f"* Location Entity: {loc.get('name')} {coords_str}{harbor_str}")
    else:
        print("* Location Entity: None detected in query")

    time_range = final_state.get("time_range") or {}
    if time_range:
        print(f"* Temporal Scope:  {time_range.get('raw')} (Relative: {time_range.get('relative_day')}, Period: {time_range.get('period')}, Horizon: {time_range.get('forecast_horizon_hours')}h)")

    vars_list = final_state.get("variables") or []
    if vars_list:
        print(f"* Target Variables:{', '.join(vars_list)}")

    constraints = final_state.get("constraints") or {}
    if constraints:
        print(f"* Constraints:     {json.dumps(constraints)}")

    # 4. Telemetry: Phase 3 Planner
    plan = final_state.get("execution_plan")
    if plan:
        print(format_sub_header("[PHASE 3: DAG EXECUTION PLAN]"))
        print(f"* Plan ID:         {plan.plan_id}")
        print(f"* Summary:         {plan.summary}")
        print(f"* Total Steps:     {len(plan.steps)}")
        if verbose:
            for s in plan.steps:
                dep = f" <- depends on [{', '.join(s.depends_on)}]" if s.depends_on else " (independent)"
                print(f"  [{s.type}] {s.id:<25} ({s.operation}){dep}")

    # 5. Telemetry: Phase 4 Tools & Phase 6 Analytics
    print(format_sub_header("[PHASE 4 DATA & PHASE 6 MULTI-ENGINE DECISION]"))
    tool_results = final_state.get("tool_results", [])
    print(f"* P4 Tools Run:    {len(tool_results)} operations completed")

    decision = final_state.get("decision") or {}
    selected = decision.get("selected_zone") or final_state.get("selected_zone")
    ranked = decision.get("ranked_zones") or final_state.get("ranked_zones") or []
    rejected = decision.get("rejected_zones") or final_state.get("rejected_zones") or []

    if selected:
        sz_risk = selected.get("risk_score", 0.0)
        risk_tag = "LOW" if sz_risk <= 30.0 else ("MODERATE" if sz_risk <= 60.0 else ("HIGH" if sz_risk <= 80.0 else "SEVERE"))
        print(f"* SELECTED ZONE:   {selected.get('zone_id')} ({selected.get('distance_nm')} NM {selected.get('bearing')})")
        print(f"  - Opportunity Score (6A): {selected.get('opportunity_score', 0.0):.1f}/100")
        print(f"  - Marine Risk Score (6B): {sz_risk:.1f}/100 ({risk_tag} — favorable relative to alternatives)")
        print(f"  - Regulatory Status (6C): ELIGIBLE (No active spatial prohibitions)")
        print(f"  - Ranking Score (6D):     {selected.get('ranking_score', 0.0):.1f}/100")
        if selected.get("species"):
            print(f"  - Target Species:         {', '.join(selected.get('species'))}")

    if ranked:
        print("\n* Eligible Ranked Zones:")
        for r in ranked:
            print(f"  - {r.get('zone_id'):<8} | Opp: {r.get('opportunity_score', 0.0):>5.1f} | Risk: {r.get('risk_score', 0.0):>5.1f} | Rank Score: {r.get('ranking_score', 0.0):>5.1f}")

    if rejected:
        print("\n* Disqualified / Rejected Zones:")
        for rj in rejected:
            reasons_str = "; ".join(rj.get("reasons", []))
            print(f"  - {rj.get('zone_id'):<8} | Status: {rj.get('status'):<16} | Opp: {rj.get('opportunity_score', 0.0):>5.1f} | Reasons: {reasons_str}")

    # 6. Telemetry: Phase 7B & 7C Final Response
    print(format_sub_header("[PHASE 7C: GENERATED ADVISORY (USER-FACING)]"))
    final_resp = final_state.get("final_response")
    if isinstance(final_resp, AgentResponse):
        print(final_resp.markdown_content)
    elif isinstance(final_resp, dict):
        print(final_resp.get("markdown_content", ""))

    # 7. Frontend UI Visual Payload Summary
    if isinstance(final_resp, AgentResponse) and final_resp.visual_payload:
        vp = final_resp.visual_payload
        print(format_sub_header("[FRONTEND VISUAL PAYLOAD (MAP & CHARTS UI)]"))
        if vp.metric_badges:
            print(f"* Metric Badges:   {json.dumps(vp.metric_badges)}")
        if vp.map_features_geojson:
            features = vp.map_features_geojson.get("features", [])
            print(f"* Map GeoJSON:     {len(features)} spatial feature(s) ready for UI render")
        if vp.charts_data:
            print(f"* Chart Timeseries:{len(vp.charts_data)} forecast datapoint(s)")

    # 8. Execution Telemetry Summary & Latency Breakdown
    lat_telem = final_state.get("latency_telemetry") or {}
    print(format_sub_header("[PIPELINE LATENCY BREAKDOWN]"))
    print(f"  * understand_query:      {lat_telem.get('understand_query_ms', 0.0):>7.2f} ms")
    print(f"  * planner:               {lat_telem.get('planner_ms', 0.0):>7.2f} ms")
    print(f"  * tool_selection:        {lat_telem.get('tool_selection_ms', 0.0):>7.2f} ms")
    print(f"  * executor (DAG & tools):{lat_telem.get('executor_ms', 0.0):>7.2f} ms")

    tool_timings = lat_telem.get("tool_timings_ms") or {}
    if tool_timings and verbose:
        for t_op, t_ms in tool_timings.items():
            print(f"    - {t_op:<30}: {t_ms:>6.2f} ms")

    print(f"  * evidence_assembly:     {lat_telem.get('evidence_assembly_ms', 0.0):>7.2f} ms")
    print(f"  * response_generation:   {lat_telem.get('response_generation_ms', 0.0):>7.2f} ms")
    print(f"  -----------------------------------------------")
    print(f"  * Total Tracked Pipeline: {lat_telem.get('total_pipeline_ms', 0.0):>7.2f} ms")
    print(f"  * Overall Wall-Clock:     {wall_duration_ms:>7.2f} ms")
    print(f"* State Transitions:      START -> understand_query -> planner -> tool_selection -> executor -> evidence_assembly -> response_generation -> END")
    print(format_header("RUN COMPLETE"))


def main():
    parser = argparse.ArgumentParser(description="Varidhi Marine Intelligence Agent Runner")
    parser.add_argument(
        "query",
        nargs="?",
        default="I am near Mangalore. Where should I fish tomorrow morning?",
        help="Natural language marine query"
    )
    parser.add_argument(
        "--role",
        choices=["fisherman", "researcher", "general"],
        default="fisherman",
        help="Persona style for generated advisory"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Hide detailed DAG steps"
    )
    args = parser.parse_args()

    asyncio.run(run_query(args.query, args.role, verbose=not args.compact))


if __name__ == "__main__":
    main()

