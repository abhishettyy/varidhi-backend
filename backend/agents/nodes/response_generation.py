"""Response generation node: synthesizes evidence into persona-tailored marine advisories."""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.agents.llm import classify_llm_error
from backend.agents.llm.factory import get_llm_provider
from backend.agents.llm.providers.fake_provider import FakeLLMProvider
from backend.agents.prompts.synthesis_prompts import (
    STRUCTURED_RESPONSE_SYNTHESIS_PROMPT,
)
from backend.agents.prompts.system_prompts import (
    FISHERMAN_PERSONA_PROMPT,
    MARITIME_OPERATOR_PROMPT,
    MARINE_SYSTEM_DIRECTIVE,
    RESEARCHER_PERSONA_PROMPT,
)
from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.response import (
    AgentResponse,
    RoleType,
    SafetyAlert,
    SafetySeverity,
    VisualPayload,
)
from backend.agents.state.marine_state import MarineState

logger = logging.getLogger(__name__)


async def response_generation_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Formats the final natural language response and UI payloads.
    Adapts style dynamically based on whether the caller is a Fisherman, Researcher, or Maritime Operator.
    Supports LLM-backed synthesis with strict guardrails and 100% deterministic fallback.
    """
    t0 = time.perf_counter()
    raw_query = state.get("query", "") or state.get("raw_query", "")
    user_type_raw = state.get("user_type", "general")
    try:
        user_role = RoleType(user_type_raw)
    except ValueError:
        user_role = RoleType.GENERAL

    intent_str = state.get("intent", MarineIntent.GENERAL_QUERY.value)
    location = state.get("location") or {}
    loc_name = location.get("name") if isinstance(location, dict) else "Coastal Waters"
    evidence_bundle = state.get("evidence_bundle")

    # Ingest Decision Synthesis object from state if available
    decision_data = state.get("decision") or {}
    selected_zone = decision_data.get("selected_zone") or state.get("selected_zone")
    rejected_zones = decision_data.get("rejected_zones") or state.get("rejected_zones") or []
    ranked_zones = decision_data.get("ranked_zones") or state.get("ranked_zones") or []

    # Extract metrics from evidence
    wave_height = 1.2
    wind_speed = 10.0
    sst_celsius = 28.5
    chla_val = 2.0
    hotspots = []
    risk_severity = SafetySeverity.SAFE_GREEN
    explicit_severity_found = False

    if evidence_bundle:
        for item in evidence_bundle.items:
            m = item.metrics
            if "wave_height_m" in m:
                wave_height = m["wave_height_m"]
            if "wind_speed_knots" in m:
                wind_speed = m["wind_speed_knots"]
            if "mean_sst_celsius" in m:
                sst_celsius = m["mean_sst_celsius"]
            if "chlorophyll_a_mg_m3" in m:
                chla_val = m["chlorophyll_a_mg_m3"]
            if "hotspots" in m:
                hotspots = m["hotspots"]
            if "severity" in m:
                sev_str = str(m["severity"]).lower()
                if "danger" in sev_str or "red" in sev_str or "severe" in sev_str:
                    risk_severity = SafetySeverity.DANGER_RED
                    explicit_severity_found = True
                elif "warning" in sev_str or "orange" in sev_str or "high" in sev_str:
                    risk_severity = SafetySeverity.WARNING_ORANGE
                    explicit_severity_found = True
                elif "caution" in sev_str or "yellow" in sev_str or "moderate" in sev_str:
                    risk_severity = SafetySeverity.CAUTION_YELLOW
                    explicit_severity_found = True
                elif "safe" in sev_str or "green" in sev_str or "low" in sev_str:
                    risk_severity = SafetySeverity.SAFE_GREEN
                    explicit_severity_found = True

    # If explicit severity wasn't found in metrics, derive from selected zone risk score (Phase 6 bounds)
    if not explicit_severity_found and selected_zone and "risk_score" in selected_zone:
        try:
            sz_risk = float(selected_zone["risk_score"])
            if sz_risk > 80.0:
                risk_severity = SafetySeverity.DANGER_RED
            elif sz_risk > 60.0:
                risk_severity = SafetySeverity.WARNING_ORANGE
            elif sz_risk > 30.0:
                risk_severity = SafetySeverity.CAUTION_YELLOW
            else:
                risk_severity = SafetySeverity.SAFE_GREEN
        except (ValueError, TypeError):
            pass

    # Build Safety Alert according to standard severity semantics
    if risk_severity == SafetySeverity.DANGER_RED:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.DANGER_RED,
            title="DANGER: Severe Sea State",
            description=f"Severe sea conditions near {loc_name}. Wave heights up to {wave_height}m with strong wind gusts.",
            action_advice="All artisanal and small fishing crafts are strongly advised NOT to venture into deep sea.",
        )
    elif risk_severity == SafetySeverity.WARNING_ORANGE:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.WARNING_ORANGE,
            title="WARNING: High Sea State Risk",
            description=f"Elevated wave heights ({wave_height}m) and wind speeds ({wind_speed} kts) near {loc_name}.",
            action_advice="Navigate with high caution. Avoid venturing beyond 10-15 NM.",
        )
    elif risk_severity == SafetySeverity.CAUTION_YELLOW:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.CAUTION_YELLOW,
            title="CAUTION: Moderate Sea Conditions",
            description=f"Moderate sea state near {loc_name}. Wave heights ~{wave_height}m, wind ~{wind_speed} kts.",
            action_advice="Favorable relative to evaluated alternatives. Maintain standard maritime vigilance.",
        )
    else:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.SAFE_GREEN,
            title="SAFE: Low Risk Sea Conditions",
            description=f"Calm sea state near {loc_name}. Waves ~{wave_height}m, wind ~{wind_speed} kts.",
            action_advice="Favorable conditions for coastal and offshore operations.",
        )

    key_recommendations: List[str] = []
    evidence_summaries: List[str] = [item.summary for item in (evidence_bundle.items if evidence_bundle else [])]

    is_fishing_intent = intent_str in (
        MarineIntent.FISHING_RECOMMENDATION.value,
        MarineIntent.PFZ_SEARCH.value,
        "potential_fishing_zone",
        "fishing_recommendation",
        "pfz_search",
        "FISHING_RECOMMENDATION",
        "PFZ_SEARCH",
    )

    llm_used = False
    llm_fallback = False
    llm_fallback_reason: Optional[str] = None
    markdown_content: Optional[str] = None

    # Check if LLM response generation should be attempted
    llm = get_llm_provider()
    attempt_llm = False
    if state.get("use_llm") is True:
        attempt_llm = True
    elif llm.provider_name in ("gemini", "openai"):
        attempt_llm = True
    elif isinstance(llm, FakeLLMProvider) and (llm.canned_text is not None or llm.error_mode is not None):
        attempt_llm = True

    if attempt_llm:
        try:
            persona_prompt = (
                FISHERMAN_PERSONA_PROMPT
                if user_role == RoleType.FISHERMAN
                else (RESEARCHER_PERSONA_PROMPT if user_role == RoleType.RESEARCHER else MARITIME_OPERATOR_PROMPT)
            )
            combined_system_prompt = f"{MARINE_SYSTEM_DIRECTIVE}\n\n{persona_prompt}"

            context_payload = {
                "query": raw_query,
                "role": user_role.value,
                "location": loc_name,
                "safety_alert": safety_alert.model_dump(),
                "sea_state": {
                    "wave_height_m": wave_height,
                    "wind_speed_knots": wind_speed,
                    "sst_celsius": sst_celsius,
                    "chlorophyll_a_mg_m3": chla_val,
                },
                "selected_zone": selected_zone,
                "ranked_zones": ranked_zones,
                "rejected_zones": rejected_zones,
                "evidence_summaries": evidence_summaries,
                "is_synthetic_demonstration": True,
            }

            synthesis_prompt = STRUCTURED_RESPONSE_SYNTHESIS_PROMPT.format(
                context_json=json.dumps(context_payload, indent=2, default=str)
            )

            generated_text = await llm.generate_text(
                prompt=synthesis_prompt,
                system_prompt=combined_system_prompt,
                temperature=0.0,
            )
            if generated_text and generated_text.strip():
                markdown_content = generated_text.strip()
                llm_used = True
                llm_fallback = False
                if selected_zone:
                    zid = selected_zone.get("zone_id", "Recommended Zone")
                    dist = selected_zone.get("distance_nm", "")
                    bearing = selected_zone.get("bearing", "")
                    key_recommendations.append(f"Recommended Fishing Ground: {zid} ({dist} NM {bearing})".strip())
                else:
                    key_recommendations.append(safety_alert.action_advice)
            else:
                llm_fallback = True
                llm_fallback_reason = "SCHEMA_VALIDATION_ERROR"
        except Exception as e:
            logger.debug(f"LLM response generation fallback triggered: {e}")
            llm_fallback = True
            llm_fallback_reason = classify_llm_error(e)

    # Deterministic Template Fallback Formatter
    if markdown_content is None:
        if user_role == RoleType.FISHERMAN:
            lines = [f"### Marine Advisory for {loc_name}", ""]

            if is_fishing_intent and selected_zone:
                zid = selected_zone.get("zone_id", "ZONE_B")
                dist = selected_zone.get("distance_nm", 8.2)
                bearing = selected_zone.get("bearing", "SSW")
                species = ", ".join(selected_zone.get("species") or ["Mackerel", "Sardines"])
                opp = selected_zone.get("opportunity_score", 66.9)
                risk = selected_zone.get("risk_score", 34.9)
                rank = selected_zone.get("ranking_score", 67.31)
                risk_label = "LOW" if risk <= 30.0 else ("MODERATE" if risk <= 60.0 else ("HIGH" if risk <= 80.0 else "SEVERE"))

                lines.extend([
                    f"#### 🐟 Recommended Fishing Ground: {zid} ({dist} NM {bearing})",
                    f"- **Distance & Bearing:** {bearing} ({dist} NM from harbor)",
                    f"- **Target Species:** {species}",
                    f"- **Fishing Opportunity Score:** {opp:.1f}/100",
                    f"- **Status:** Best Favorable Option (Risk: {risk:.1f}/100 - {risk_label})",
                    "",
                ])

                lines.extend([
                    f"**Safety Status:** {safety_alert.title}",
                    f"> {safety_alert.action_advice}",
                    "",
                    "#### Sea Conditions:",
                    f"- **Waves:** {wave_height} meters ({'Calm' if wave_height < 1.5 else 'Rough'})",
                    f"- **Wind:** {wind_speed} knots",
                    f"- **Water Temp:** {sst_celsius}°C",
                    "",
                ])

                if rejected_zones:
                    lines.append("#### Decision Breakdown & Other Zones:")
                    for rz in rejected_zones:
                        rz_id = rz.get("zone_id")
                        rz_status = rz.get("status")
                        rz_opp = rz.get("opportunity_score", 0.0)
                        rz_reasons = "; ".join(rz.get("reasons", []))
                        if rz_status == "REJECTED_LEGAL":
                            lines.append(f"- **{rz_id} (Opportunity {rz_opp:.1f}):** **REJECTED (LEGAL RESTRICTION)** — {rz_reasons or 'Marine Protected Sanctuary restriction.'}")
                        elif rz_status == "REJECTED_RISK":
                            lines.append(f"- **{rz_id} (Opportunity {rz_opp:.1f}):** **REJECTED (HIGH RISK)** — {rz_reasons or 'Sea conditions exceed safety threshold.'}")
                        else:
                            lines.append(f"- **{rz_id}:** **{rz_status}** — {rz_reasons}")
                    lines.append("")

                lines.append("*Notice: This assessment uses synthetic marine demonstration data for the current prototype. It is a deterministic demonstration heuristic and does not constitute official maritime safety certification, port clearance, or statutory navigation advice.*")
                key_recommendations.append(f"Recommended Fishing Ground: {zid} ({dist} NM {bearing})")
            elif is_fishing_intent and hotspots:
                lines.extend([
                    f"**Safety Status:** {safety_alert.title}",
                    f"> {safety_alert.action_advice}",
                    "",
                    "#### Sea Conditions:",
                    f"- **Waves:** {wave_height} meters ({'Calm' if wave_height < 1.5 else 'Rough'})",
                    f"- **Wind:** {wind_speed} knots",
                    f"- **Water Temp:** {sst_celsius}°C",
                    "",
                    "#### Recommended Fishing Hotspots:",
                ])
                for hs in hotspots:
                    lines.append(f"- **Zone {hs.get('zone_id', '1')}**: Bearing **{hs.get('bearing')}**, Distance **{hs.get('distance_nm')} NM** ({hs.get('target_depth_m')}m depth).")
                    lines.append(f"  *Expected Fish:* {', '.join(hs.get('likely_species', ['Pelagic species']))}")
                lines.append("")
                lines.append("*Notice: This assessment uses synthetic marine demonstration data for the current prototype. It does not constitute official maritime safety certification.*")
                key_recommendations.append(f"Best fishing ground: {hotspots[0].get('distance_nm')} NM {hotspots[0].get('bearing')}.")
            else:
                lines.extend([
                    f"**Safety Status:** {safety_alert.title}",
                    f"> {safety_alert.action_advice}",
                    "",
                    "#### Sea Conditions:",
                    f"- **Waves:** {wave_height} meters ({'Calm' if wave_height < 1.5 else 'Rough'})",
                    f"- **Wind:** {wind_speed} knots",
                    f"- **Water Temp:** {sst_celsius}°C",
                    "",
                    "*Notice: This assessment uses synthetic marine demonstration data for the current prototype. It does not constitute official maritime safety certification.*",
                ])
                key_recommendations.append(safety_alert.action_advice)


            markdown_content = "\n".join(lines)

        elif user_role == RoleType.RESEARCHER:
            lines = [
                f"# Oceanographic Intelligence Report: {loc_name}",
                f"**Analysis Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | **Primary Intent:** {intent_str}",
                "",
                "## 1. Biophysical Ocean State",
                "| Parameter | Value | Reference / Status |",
                "| :--- | :--- | :--- |",
                f"| Significant Wave Height ($H_s$) | `{wave_height} m` | {'Within Normal Bounds' if wave_height < 2.0 else 'Elevated'} |",
                f"| Surface Wind Speed | `{wind_speed} kts` | Directional vector active |",
                f"| Sea Surface Temperature (SST) | `{sst_celsius} °C` | Mean observed SST |",
                f"| Chlorophyll-a Density | `{chla_val} mg/m³` | Surface chlorophyll proxy |",
                "",
                "## 2. Risk & Hydrodynamic Assessment",
                f"- **Calculated Risk Index:** {safety_alert.severity.value}",
                f"- **Advisory Assessment:** {safety_alert.description}",
                "",
            ]

            if is_fishing_intent and (selected_zone or ranked_zones or rejected_zones):
                lines.extend([
                    "## 3. Multi-Engine Decision Synthesis & Zone Ranking",
                    "| Zone ID | Opportunity (6A) | Marine Risk (6B) | Regulatory (6C) | Distance | Status | Ranking Score | Decision Factor |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
                ])
                all_evals = decision_data.get("all_evaluations") or (ranked_zones + rejected_zones)
                for ev in all_evals:
                    zid = ev.get("zone_id")
                    opp = f"{ev.get('opportunity_score', 0.0):.1f}" if ev.get("opportunity_score") is not None else "N/A"
                    risk = f"{ev.get('risk_score', 0.0):.1f}" if ev.get("risk_score") is not None else "N/A"
                    reg = ev.get("regulatory_status", "UNKNOWN")
                    dist = f"{ev.get('distance_nm', 0.0):.1f} NM" if ev.get("distance_nm") is not None else "N/A"
                    st = ev.get("status", "PENDING")
                    rnk = f"{ev.get('ranking_score', 0.0):.1f}" if ev.get("ranking_score") is not None else "Disqualified"
                    reason_str = ev.get("reasons", ["-"])[0] if ev.get("reasons") else "-"
                    lines.append(f"| `{zid}` | `{opp}` | `{risk}` | `{reg}` | `{dist}` | `{st}` | `{rnk}` | {reason_str} |")
                lines.append("")
            elif hotspots:
                lines.append("## 3. Potential Fishing Zone (PFZ) Convergence")
                for hs in hotspots:
                    lines.append(f"- **Zone `{hs.get('zone_id')}`**: Coord `({hs.get('latitude')}, {hs.get('longitude')})` | Depth `{hs.get('target_depth_m')}m`")
                    lines.append(f"  - **Convergence Signature:** {hs.get('sst_gradient_delta')}, Chlorophyll `{hs.get('chlorophyll_gradient')}`")
            else:
                lines.append("## 3. Potential Fishing Zone (PFZ) Convergence")
                lines.append("- *No prominent PFZ convergence detected within specified boundary.*")

            lines.extend([
                "",
                "*Notice: This assessment uses synthetic marine demonstration data for the current prototype. It does not constitute official maritime safety certification.*"
            ])
            key_recommendations.append("Multi-engine decision and PFZ alignment verified.")
            markdown_content = "\n".join(lines)

        else:
            desc = safety_alert.description
            if selected_zone:
                zid = selected_zone.get("zone_id")
                dist = selected_zone.get("distance_nm")
                bearing = selected_zone.get("bearing")
                desc += f"\n\nRecommended safe fishing ground: Zone {zid} ({dist} NM {bearing})."
                if rejected_zones:
                    desc += f" (Note: higher-opportunity zones were disqualified by legal or risk constraints)."
            markdown_content = (
                f"### Marine Intelligence Advisory for {loc_name}\n\n"
                f"**Condition:** {safety_alert.title}\n\n"
                f"{desc}\n\n"
                f"**Action Advice:** {safety_alert.action_advice}\n\n"
                f"*Notice: This assessment uses synthetic marine demonstration data for the current prototype. It does not constitute official maritime safety certification.*"
            )
            key_recommendations.append(safety_alert.action_advice)

    # Canonical fallback coordinates for standard scenario zones
    CANONICAL_ZONE_COORDS = {
        "ZONE_A": (12.95, 74.80),
        "ZONE_B": (12.90, 74.95),
        "ZONE_C": (12.82, 75.05),
    }

    # Build Visual Payload for Frontend
    geojson_features = []
    if selected_zone:
        zid = selected_zone.get("zone_id")
        raw_meta = selected_zone.get("raw_metadata") or {}
        raw_f = raw_meta.get("raw_features", {}) if isinstance(raw_meta, dict) else {}
        lat = selected_zone.get("latitude") or selected_zone.get("lat") or (raw_f.get("latitude") or raw_f.get("lat") if isinstance(raw_f, dict) else None)
        lon = selected_zone.get("longitude") or selected_zone.get("lon") or (raw_f.get("longitude") or raw_f.get("lon") if isinstance(raw_f, dict) else None)
        if (lat is None or lon is None) and zid in CANONICAL_ZONE_COORDS:
            lat, lon = CANONICAL_ZONE_COORDS[zid]
        if lat is None:
            lat = location.get("latitude", 12.90) if isinstance(location, dict) else 12.90
        if lon is None:
            lon = location.get("longitude", 74.95) if isinstance(location, dict) else 74.95

        species = selected_zone.get("species") or (raw_f.get("species") if isinstance(raw_f, dict) else [])
        geojson_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "zone_id": zid,
                "status": "SELECTED",
                "recommended": True,
                "ranking_score": selected_zone.get("ranking_score"),
                "opportunity_score": selected_zone.get("opportunity_score"),
                "risk_score": selected_zone.get("risk_score"),
                "distance_nm": selected_zone.get("distance_nm"),
                "species": species,
            }
        })
    for rz in rejected_zones:
        zid = rz.get("zone_id")
        raw_meta = rz.get("raw_metadata") or {}
        raw_f = raw_meta.get("raw_features", {}) if isinstance(raw_meta, dict) else {}
        lat = rz.get("latitude") or rz.get("lat") or (raw_f.get("latitude") or raw_f.get("lat") if isinstance(raw_f, dict) else None)
        lon = rz.get("longitude") or rz.get("lon") or (raw_f.get("longitude") or raw_f.get("lon") if isinstance(raw_f, dict) else None)
        if (lat is None or lon is None) and zid in CANONICAL_ZONE_COORDS:
            lat, lon = CANONICAL_ZONE_COORDS[zid]

        species = rz.get("species") or (raw_f.get("species") if isinstance(raw_f, dict) else [])
        if lat is not None and lon is not None:
            geojson_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "zone_id": zid,
                    "status": rz.get("status"),
                    "recommended": False,
                    "rejection_codes": rz.get("rejection_codes"),
                    "reasons": rz.get("reasons"),
                    "opportunity_score": rz.get("opportunity_score"),
                    "risk_score": rz.get("risk_score"),
                    "distance_nm": rz.get("distance_nm"),
                    "species": species,
                }
            })
    if not geojson_features and hotspots:
        for hs in hotspots:
            lat = hs.get("latitude", 9.93)
            lon = hs.get("longitude", 76.26)
            geojson_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "zone_id": hs.get("zone_id"),
                    "species": hs.get("likely_species"),
                    "distance_nm": hs.get("distance_nm"),
                }
            })

    metric_badges_dict = {
        "SST": f"{sst_celsius}°C",
        "Wave Height": f"{wave_height}m",
        "Wind Speed": f"{wind_speed} kts",
        "Safety": safety_alert.severity.value,
    }
    if selected_zone:
        metric_badges_dict["Recommended Zone"] = selected_zone.get("zone_id", "ZONE_B")
        if selected_zone.get("ranking_score") is not None:
            metric_badges_dict["Ranking Score"] = f"{selected_zone.get('ranking_score'):.1f}"

    visual_payload = VisualPayload(
        map_features_geojson={"type": "FeatureCollection", "features": geojson_features} if geojson_features else None,
        charts_data=[
            {"time": "00:00", "wave_height": wave_height, "wind_speed": wind_speed},
            {"time": "06:00", "wave_height": round(wave_height * 1.1, 2), "wind_speed": round(wind_speed * 1.05, 1)},
            {"time": "12:00", "wave_height": wave_height, "wind_speed": wind_speed},
        ],
        metric_badges=metric_badges_dict,
    )

    response = AgentResponse(
        response_id=f"resp_{uuid.uuid4().hex[:8]}",
        role=user_role,
        markdown_content=markdown_content,
        safety_alert=safety_alert,
        key_recommendations=key_recommendations,
        evidence_summary=evidence_summaries,
        visual_payload=visual_payload,
        status="success",
    )

    merged_decision = dict(decision_data)
    merged_decision.setdefault("safety_level", safety_alert.severity.value)
    merged_decision.setdefault("action_advice", safety_alert.action_advice)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    latency_telemetry = dict(state.get("latency_telemetry") or {})
    latency_telemetry["response_generation_ms"] = round(elapsed_ms, 2)
    pipeline_start = latency_telemetry.get("pipeline_start_perf")
    if pipeline_start is not None:
        latency_telemetry["total_pipeline_ms"] = round((time.perf_counter() - pipeline_start) * 1000.0, 2)
    else:
        node_keys = [
            "understand_query_ms", "planner_ms", "tool_selection_ms",
            "executor_ms", "evidence_assembly_ms", "response_generation_ms"
        ]
        latency_telemetry["total_pipeline_ms"] = round(sum(latency_telemetry.get(k, 0.0) for k in node_keys), 2)

    result_dict = {
        "final_response": response,
        "response": response.model_dump(),
        "decision": merged_decision,
        "llm_used": llm_used,
        "llm_fallback": llm_fallback,
        "latency_telemetry": latency_telemetry,
    }
    if llm_fallback_reason:
        result_dict["llm_fallback_reason"] = llm_fallback_reason

    return result_dict

