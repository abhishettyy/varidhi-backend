"""FastAPI Router for Varidhi Agentic Marine Intelligence Platform (Phase 8).

Implements:
- GET  /health          -> Liveness, service name, active LLM provider (no secrets)
- POST /chat            -> Primary natural-language query endpoint returning ChatResponse
- POST /api/chat/query  -> Backward-compatible alias for existing frontend client
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

from fastapi import APIRouter, HTTPException, status

from backend.agents.graph.workflow import run_marine_agent_state_async
from backend.agents.llm.factory import get_llm_config_from_env
from backend.agents.schemas.response import AgentResponse, RoleType
from backend.agents.state.marine_state import MarineState
from backend.api.schemas import (
    DEFAULT_SYNTHETIC_DISCLAIMER,
    ChatRequest,
    ChatResponse,
    DecisionSummary,
    EvidenceItemResponse,
    HealthResponse,
    QueryContextResponse,
    TelemetryResponse,
    VisualPayloadResponse,
    ZoneSummary,
)

router = APIRouter()


def serialize_marine_state_to_chat_response(
    state: MarineState,
    requested_role: RoleType,
) -> ChatResponse:
    """
    Transforms internal LangGraph MarineState into the authoritative, stable ChatResponse.
    Derives all decisions, scores, and zones from structured state (never LLM prose).
    """
    # 1. Final user-facing message & agent response object
    final_resp = state.get("final_response")
    raw_resp_dict = state.get("response") or {}

    if isinstance(final_resp, AgentResponse):
        message = final_resp.markdown_content
        resp_id = final_resp.response_id
        safety_alert = final_resp.safety_alert
        key_recs = final_resp.key_recommendations
        ev_summary = final_resp.evidence_summary
        resp_status = final_resp.status
        visual_data = final_resp.visual_payload
    else:
        message = raw_resp_dict.get("markdown_content") or "Advisory generated from marine state."
        resp_id = raw_resp_dict.get("response_id") or f"resp_{uuid.uuid4().hex[:8]}"
        safety_alert = raw_resp_dict.get("safety_alert")
        key_recs = raw_resp_dict.get("key_recommendations") or []
        ev_summary = raw_resp_dict.get("evidence_summary") or []
        resp_status = raw_resp_dict.get("status") or "success"
        visual_data = raw_resp_dict.get("visual_payload")

    def _extract_spatial_fields(item: Dict[str, Any]) -> Dict[str, Any]:
        raw_meta = item.get("raw_metadata") or {}
        raw_f = raw_meta.get("raw_features", {}) if isinstance(raw_meta, dict) else {}
        if not isinstance(raw_f, dict):
            raw_f = {}

        lat = item.get("latitude") or item.get("lat") or raw_f.get("latitude") or raw_f.get("lat")
        lon = item.get("longitude") or item.get("lon") or raw_f.get("longitude") or raw_f.get("lon")
        bearing = item.get("bearing") or raw_f.get("bearing")
        species = item.get("species") or raw_f.get("species") or []
        dist = item.get("distance_nm") or raw_f.get("distance_nm")

        return {
            "latitude": lat,
            "longitude": lon,
            "bearing": bearing,
            "species": species,
            "distance_nm": dist,
        }

    # 2. Authoritative P6 Decision Synthesis
    decision_dict = state.get("decision") or {}
    selected_zone = decision_dict.get("selected_zone") or state.get("selected_zone")

    decision_summary: Optional[DecisionSummary] = None
    selected_zone_id: Optional[str] = None
    if selected_zone:
        selected_zone_id = selected_zone.get("zone_id")
        sp = _extract_spatial_fields(selected_zone)
        decision_summary = DecisionSummary(
            selected_zone_id=selected_zone_id,
            status="SELECTED",
            opportunity_score=selected_zone.get("opportunity_score"),
            risk_score=selected_zone.get("risk_score"),
            regulatory_status=selected_zone.get("regulatory_status", "ELIGIBLE"),
            ranking_score=selected_zone.get("ranking_score"),
            distance_nm=sp["distance_nm"],
            bearing=sp["bearing"],
            species=sp["species"],
            latitude=sp["latitude"],
            longitude=sp["longitude"],
            reasons=selected_zone.get("reasons") or ["Top-ranked eligible candidate."],
            safety_level=decision_dict.get("safety_level"),
            action_advice=decision_dict.get("action_advice"),
        )

    # 3. Structured Candidate Zones List
    zones_list: List[ZoneSummary] = []
    seen_zone_ids = set()

    # Prioritize all_evaluations if available
    all_evals = decision_dict.get("all_evaluations")
    if all_evals and isinstance(all_evals, list):
        for ev in all_evals:
            zid = ev.get("zone_id")
            if zid and zid not in seen_zone_ids:
                seen_zone_ids.add(zid)
                sp = _extract_spatial_fields(ev)
                zones_list.append(
                    ZoneSummary(
                        zone_id=zid,
                        status=ev.get("status", "EVALUATED"),
                        opportunity_score=ev.get("opportunity_score"),
                        risk_score=ev.get("risk_score"),
                        regulatory_status=ev.get("regulatory_status"),
                        ranking_score=ev.get("ranking_score"),
                        distance_nm=sp["distance_nm"],
                        bearing=sp["bearing"],
                        species=sp["species"],
                        latitude=sp["latitude"],
                        longitude=sp["longitude"],
                        reasons=ev.get("reasons") or [],
                    )
                )

    # Fallback to combining selected, ranked, and rejected zones
    if not zones_list:
        if selected_zone and selected_zone_id:
            seen_zone_ids.add(selected_zone_id)
            sp = _extract_spatial_fields(selected_zone)
            zones_list.append(
                ZoneSummary(
                    zone_id=selected_zone_id,
                    status="SELECTED",
                    opportunity_score=selected_zone.get("opportunity_score"),
                    risk_score=selected_zone.get("risk_score"),
                    regulatory_status=selected_zone.get("regulatory_status", "ELIGIBLE"),
                    ranking_score=selected_zone.get("ranking_score"),
                    distance_nm=sp["distance_nm"],
                    bearing=sp["bearing"],
                    species=sp["species"],
                    latitude=sp["latitude"],
                    longitude=sp["longitude"],
                    reasons=selected_zone.get("reasons") or [],
                )
            )

        for rz in (decision_dict.get("ranked_zones") or state.get("ranked_zones") or []):
            zid = rz.get("zone_id")
            if zid and zid not in seen_zone_ids:
                seen_zone_ids.add(zid)
                sp = _extract_spatial_fields(rz)
                zones_list.append(
                    ZoneSummary(
                        zone_id=zid,
                        status=rz.get("status", "ELIGIBLE"),
                        opportunity_score=rz.get("opportunity_score"),
                        risk_score=rz.get("risk_score"),
                        regulatory_status=rz.get("regulatory_status", "ELIGIBLE"),
                        ranking_score=rz.get("ranking_score"),
                        distance_nm=sp["distance_nm"],
                        bearing=sp["bearing"],
                        species=sp["species"],
                        latitude=sp["latitude"],
                        longitude=sp["longitude"],
                        reasons=rz.get("reasons") or [],
                    )
                )

        for rj in (decision_dict.get("rejected_zones") or state.get("rejected_zones") or []):
            zid = rj.get("zone_id")
            if zid and zid not in seen_zone_ids:
                seen_zone_ids.add(zid)
                sp = _extract_spatial_fields(rj)
                zones_list.append(
                    ZoneSummary(
                        zone_id=zid,
                        status=rj.get("status", "REJECTED"),
                        opportunity_score=rj.get("opportunity_score"),
                        risk_score=rj.get("risk_score"),
                        regulatory_status=rj.get("regulatory_status", "BLOCKED"),
                        ranking_score=rj.get("ranking_score"),
                        distance_nm=sp["distance_nm"],
                        bearing=sp["bearing"],
                        species=sp["species"],
                        latitude=sp["latitude"],
                        longitude=sp["longitude"],
                        reasons=rj.get("reasons") or [],
                    )
                )

    # 4. Provenance-Preserving Evidence Items
    evidence_items: List[EvidenceItemResponse] = []
    raw_ev = state.get("evidence") or []
    if not raw_ev and state.get("evidence_bundle"):
        raw_ev = [item.model_dump() for item in state["evidence_bundle"].items]

    for ev in raw_ev:
        if isinstance(ev, dict):
            ts = ev.get("timestamp")
            if isinstance(ts, datetime):
                ts_str = ts.isoformat()
            elif ts:
                ts_str = str(ts)
            else:
                ts_str = None

            ev_type_val = ev.get("evidence_type")
            if hasattr(ev_type_val, "value"):
                ev_type_str = str(ev_type_val.value)
            elif ev_type_val is not None:
                ev_type_str = str(ev_type_val)
                if "." in ev_type_str:
                    ev_type_str = ev_type_str.split(".")[-1].lower()
            else:
                ev_type_str = "general_observation"

            evidence_items.append(
                EvidenceItemResponse(
                    evidence_id=ev.get("evidence_id") or f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=ev_type_str,
                    source=str(ev.get("source") or "SYSTEM"),
                    summary=str(ev.get("summary") or ""),
                    metrics=ev.get("metrics") or {},
                    confidence=float(ev.get("confidence", 1.0)),
                    spatial_tag=ev.get("spatial_tag"),
                    timestamp=ts_str,
                    raw_payload=ev.get("raw_payload"),
                )
            )

    # 5. Visual Payload (GeoJSON, charts, badges)
    visual_payload_resp: Optional[VisualPayloadResponse] = None
    if visual_data:
        if hasattr(visual_data, "model_dump"):
            v_dict = visual_data.model_dump()
        elif isinstance(visual_data, dict):
            v_dict = dict(visual_data)
        else:
            v_dict = {}

        # Ensure focus_zone_id is populated if selected zone exists
        focus_id = v_dict.get("focus_zone_id") or selected_zone_id
        highlight = v_dict.get("highlight_layer") or ("zones" if selected_zone_id else "weather")

        visual_payload_resp = VisualPayloadResponse(
            map_features_geojson=v_dict.get("map_features_geojson"),
            charts_data=v_dict.get("charts_data"),
            metric_badges=v_dict.get("metric_badges"),
            focus_zone_id=focus_id,
            highlight_layer=highlight,
        )

    # 6. Structured Query Context
    query_context = QueryContextResponse(
        intent=str(state.get("intent") or "GENERAL_MARINE_QUERY"),
        confidence=float(state.get("confidence", 1.0)),
        location=state.get("location"),
        time_range=state.get("time_range"),
        variables=state.get("variables") or [],
        vessel=state.get("vessel"),
        route=state.get("route"),
        constraints=state.get("constraints") or {},
    )

    # 7. Telemetry Breakdown
    lat_telem = state.get("latency_telemetry") or {}
    total_pipeline_ms = float(lat_telem.get("total_pipeline_ms") or 0.0)

    cfg = get_llm_config_from_env()
    telemetry = TelemetryResponse(
        total_pipeline_ms=round(total_pipeline_ms, 2),
        understand_query_ms=lat_telem.get("understand_query_ms"),
        planner_ms=lat_telem.get("planner_ms"),
        tool_selection_ms=lat_telem.get("tool_selection_ms"),
        executor_ms=lat_telem.get("executor_ms"),
        evidence_assembly_ms=lat_telem.get("evidence_assembly_ms"),
        response_generation_ms=lat_telem.get("response_generation_ms"),
        tool_timings_ms=lat_telem.get("tool_timings_ms") or {},
        llm_used=bool(state.get("llm_used", False)),
        llm_fallback=bool(state.get("llm_fallback", False)),
        llm_fallback_reason=state.get("llm_fallback_reason"),
        llm_provider=state.get("llm_provider") or cfg.provider,
        llm_model=state.get("llm_model") or cfg.model,
    )

    return ChatResponse(
        message=message,
        decision=decision_summary,
        zones=zones_list,
        evidence=evidence_items,
        visual_payload=visual_payload_resp,
        query_context=query_context,
        telemetry=telemetry,
        disclaimer=DEFAULT_SYNTHETIC_DISCLAIMER,
        # Backwards-compatibility fields
        response_id=resp_id,
        role=requested_role,
        markdown_content=message,
        safety_alert=safety_alert,
        key_recommendations=key_recs,
        evidence_summary=ev_summary,
        status=resp_status,
        execution_time_seconds=round(total_pipeline_ms / 1000.0, 3) if total_pipeline_ms > 0 else 0.25,
    )


# =============================================================================
# 4. HTTP ROUTE HANDLERS
# =============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check and service status",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Returns platform liveness and configured LLM provider (no secrets)."""
    cfg = get_llm_config_from_env()
    return HealthResponse(
        status="ok",
        service="Varidhi Marine Intelligence Platform",
        version="1.0.0",
        llm_provider=cfg.provider,
        llm_model=cfg.model,
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process natural language marine query",
    description="Submits a marine query to the LangGraph agent and returns authoritative decision analytics and persona-tailored response.",
    tags=["Agent"],
)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Primary agent endpoint for Fisherman and Researcher portals.
    Executes LangGraph pipeline and transforms internal state to the stable ChatResponse schema.
    """
    try:
        final_state = await run_marine_agent_state_async(
            query=request.query,
            role=request.role,
            session_id=request.session_id,
        )
        return serialize_marine_state_to_chat_response(final_state, request.role)
    except HTTPException:
        raise
    except Exception as e:
        # Never leak secrets or raw internal exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal agent execution error: {type(e).__name__}",
        ) from e


@router.post(
    "/api/chat/query",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def legacy_chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Backward-compatible endpoint alias matching frontend/services/api/chatApi.ts."""
    return await chat_endpoint(request)
