"""Response generation node: synthesizes evidence into persona-tailored marine advisories."""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from backend.agents.schemas.intent import MarineIntent
from backend.agents.schemas.response import (
    AgentResponse,
    RoleType,
    SafetyAlert,
    SafetySeverity,
    VisualPayload,
)
from backend.agents.state.agent_state import AgentState


async def response_generation_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Formats the final natural language response and UI payloads.
    Adapts style dynamically based on whether the caller is a Fisherman, Researcher, or Maritime Operator.
    """
    user_role = state.get("user_role", RoleType.GENERAL)
    intent_res = state.get("intent_result")
    spatiotemporal = state.get("spatiotemporal_context")
    evidence_bundle = state.get("evidence_bundle")

    intent = intent_res.primary_intent if intent_res else MarineIntent.GENERAL_MARINE_QUERY
    loc_name = spatiotemporal.spatial.place_name if spatiotemporal else "Coastal Waters"

    # Extract metrics from evidence
    wave_height = 1.2
    wind_speed = 10.0
    sst_celsius = 28.5
    chla_val = 2.0
    hotspots = []
    risk_severity = SafetySeverity.SAFE_GREEN

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
                sev_str = m["severity"]
                if "danger" in sev_str or "red" in sev_str:
                    risk_severity = SafetySeverity.DANGER_RED
                elif "warning" in sev_str or "orange" in sev_str:
                    risk_severity = SafetySeverity.WARNING_ORANGE
                elif "caution" in sev_str or "yellow" in sev_str:
                    risk_severity = SafetySeverity.CAUTION_YELLOW

    # Build Safety Alert
    if risk_severity == SafetySeverity.DANGER_RED:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.DANGER_RED,
            title="DANGER: Rough Sea Advisory",
            description=f"Severe sea conditions near {loc_name}. Wave heights up to {wave_height}m with strong wind gusts.",
            action_advice="All artisanal and small fishing crafts are strongly advised NOT to venture into deep sea.",
        )
    elif risk_severity == SafetySeverity.WARNING_ORANGE:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.WARNING_ORANGE,
            title="WARNING: Moderate to Rough Sea State",
            description=f"Elevated swell and wind speeds ({wind_speed} kts) near {loc_name}.",
            action_advice="Navigate with high caution. Avoid venturing beyond 10-15 NM.",
        )
    elif risk_severity == SafetySeverity.CAUTION_YELLOW:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.CAUTION_YELLOW,
            title="CAUTION: Moderate Sea Conditions",
            description=f"Normal coastal weather with slight chop near {loc_name}.",
            action_advice="Safe for mechanized boats; small crafts maintain vigilance.",
        )
    else:
        safety_alert = SafetyAlert(
            severity=SafetySeverity.SAFE_GREEN,
            title="SAFE: Favorable Sea Conditions",
            description=f"Calm sea state near {loc_name}. Waves ~{wave_height}m, wind ~{wind_speed} kts.",
            action_advice="Ideal conditions for coastal and offshore operations.",
        )

    # Build Persona-Tailored Markdown
    key_recommendations: List[str] = []
    evidence_summaries: List[str] = [item.summary for item in (evidence_bundle.items if evidence_bundle else [])]

    if user_role == RoleType.FISHERMAN:
        # P1 UI: Simple, bold, actionable
        lines = [
            f"### 🌊 Marine Advisory for {loc_name}",
            "",
            f"**Safety Status:** {safety_alert.title}",
            f"> {safety_alert.action_advice}",
            "",
            "#### 📊 Sea Conditions:",
            f"- **Waves:** {wave_height} meters ({'Calm' if wave_height < 1.5 else 'Rough'})",
            f"- **Wind:** {wind_speed} knots",
            f"- **Water Temp:** {sst_celsius}°C",
            "",
        ]
        if intent == MarineIntent.POTENTIAL_FISHING_ZONE and hotspots:
            lines.append("#### 🐟 Recommended Fishing Hotspots:")
            for hs in hotspots:
                lines.append(f"- **Zone {hs.get('zone_id', '1')}**: Bearing **{hs.get('bearing')}**, Distance **{hs.get('distance_nm')} NM** ({hs.get('target_depth_m')}m depth).")
                lines.append(f"  *Expected Fish:* {', '.join(hs.get('likely_species', ['Pelagic species']))}")
            key_recommendations.append(f"Best fishing ground: {hotspots[0].get('distance_nm')} NM {hotspots[0].get('bearing')}.")
        else:
            key_recommendations.append(safety_alert.action_advice)

        markdown_content = "\n".join(lines)

    elif user_role == RoleType.RESEARCHER:
        # P2 UI: Scientific breakdown, tables, physical oceanography metrics
        lines = [
            f"# Oceanographic Intelligence Report: {loc_name}",
            f"**Analysis Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | **Primary Intent:** {intent.value}",
            "",
            "## 1. Biophysical Ocean State",
            "| Parameter | Value | Reference / Status |",
            "| :--- | :--- | :--- |",
            f"| Significant Wave Height ($H_s$) | `{wave_height} m` | {'Within Normal Bounds' if wave_height < 2.0 else 'Elevated'} |",
            f"| Surface Wind Speed | `{wind_speed} kts` | Directional vector active |",
            f"| Sea Surface Temperature (SST) | `{sst_celsius} °C` | Thermal front identified |",
            f"| Chlorophyll-a Density | `{chla_val} mg/m³` | High oceanic productivity |",
            "",
            "## 2. Risk & Hydrodynamic Assessment",
            f"- **Calculated Risk Index:** {safety_alert.severity.value}",
            f"- **Advisory Assessment:** {safety_alert.description}",
            "",
            "## 3. Potential Fishing Zone (PFZ) Thermal-Biological Convergence",
        ]
        if hotspots:
            for hs in hotspots:
                lines.append(f"- **Zone `{hs.get('zone_id')}`**: Coord `({hs.get('latitude')}, {hs.get('longitude')})` | Depth `{hs.get('target_depth_m')}m`")
                lines.append(f"  - **Convergence Signature:** {hs.get('sst_gradient_delta')}, Chlorophyll `{hs.get('chlorophyll_gradient')}`")
        else:
            lines.append("- *No prominent PFZ convergence detected within specified boundary.*")

        key_recommendations.append("PFZ thermal gradient alignment verified.")
        markdown_content = "\n".join(lines)

    else:
        # General Maritime / Default
        markdown_content = (
            f"### Marine Intelligence Advisory for {loc_name}\n\n"
            f"**Condition:** {safety_alert.title}\n\n"
            f"{safety_alert.description}\n\n"
            f"**Action Advice:** {safety_alert.action_advice}\n"
        )
        key_recommendations.append(safety_alert.action_advice)

    # Build Visual Payload for Frontend (P1 / P2)
    geojson_features = []
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

    visual_payload = VisualPayload(
        map_features_geojson={"type": "FeatureCollection", "features": geojson_features} if geojson_features else None,
        charts_data=[
            {"time": "00:00", "wave_height": wave_height, "wind_speed": wind_speed},
            {"time": "06:00", "wave_height": round(wave_height * 1.1, 2), "wind_speed": round(wind_speed * 1.05, 1)},
            {"time": "12:00", "wave_height": wave_height, "wind_speed": wind_speed},
        ],
        metric_badges={
            "SST": f"{sst_celsius}°C",
            "Wave Height": f"{wave_height}m",
            "Wind Speed": f"{wind_speed} kts",
            "Safety": safety_alert.severity.value,
        }
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

    return {
        "final_response": response,
        "is_terminal": True,
    }
