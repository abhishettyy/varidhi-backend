"""Evidence assembly node: structures multi-source tool and analytic outputs into verifiable evidence."""

import uuid
from typing import Any, Dict, List

from backend.agents.schemas.evidence import (
    EvidenceBundle,
    EvidenceItem,
    EvidenceType,
)
from backend.agents.state.agent_state import AgentState


async def evidence_assembly_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Normalizes and structures results from P4 tools and P6 analytics into a coherent EvidenceBundle.
    """
    raw_query = state.get("raw_query", "")
    tool_results = state.get("tool_results", [])
    analytics_results = state.get("analytics_results", [])
    spatiotemporal = state.get("spatiotemporal_context")
    spatial_tag = spatiotemporal.spatial.place_name if spatiotemporal else None

    evidence_items: List[EvidenceItem] = []
    missing_indicators: List[str] = []

    # 1. Process P4 Tool Results
    for entry in tool_results:
        op = entry.get("operation")
        res = entry.get("result", {})
        data = res.get("data", {})
        source = res.get("source", "P4_TOOL_INTEGRATION")

        if op == "fetch_ocean_weather":
            wave = data.get("wave_height_m")
            wind = data.get("wind_speed_knots")
            vis = data.get("visibility_km")
            summary = f"Wave height {wave}m, Wind {wind} kts, Visibility {vis}km"
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.WEATHER_OBSERVATION,
                    source=source,
                    summary=summary,
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op == "fetch_sst_data":
            sst = data.get("mean_sst_celsius")
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.OCEAN_TEMPERATURE_SST,
                    source=source,
                    summary=f"Mean Sea Surface Temperature: {sst}°C",
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op == "fetch_chlorophyll_data":
            chla = data.get("chlorophyll_a_mg_m3")
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.CHLOROPHYLL_DENSITY,
                    source=source,
                    summary=f"Chlorophyll-a density: {chla} mg/m³",
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op == "fetch_hazard_bulletins":
            alerts = data.get("active_alerts", [])
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.HAZARD_BULLETIN,
                    source=source,
                    summary=f"{len(alerts)} active meteorological hazard alerts.",
                    metrics={"alert_count": len(alerts)},
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )

    # 2. Process P6 Analytics Results
    for entry in analytics_results:
        op = entry.get("operation")
        res = entry.get("result", {})
        data = res.get("data", {})
        source = res.get("source", "P6_MARINE_ANALYTICS")

        if op == "calculate_sea_state_risk":
            score = data.get("risk_score")
            severity = data.get("severity")
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.RISK_INDEX_CALCULATION,
                    source=source,
                    summary=f"Sea state risk score {score}/100 ({severity})",
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op == "compute_pfz_zones":
            hotspots = data.get("recommended_hotspots", [])
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.PFZ_ZONE_ANALYTICS,
                    source=source,
                    summary=f"PFZ analysis: {len(hotspots)} active biological convergence hotspot(s).",
                    metrics={"hotspot_count": len(hotspots), "hotspots": hotspots},
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op == "detect_algal_bloom_risk":
            risk = data.get("hab_risk_level")
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.RISK_INDEX_CALCULATION,
                    source=source,
                    summary=f"Harmful Algal Bloom risk: {risk}",
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )

    bundle = EvidenceBundle(
        bundle_id=f"bundle_{uuid.uuid4().hex[:8]}",
        query=raw_query,
        items=evidence_items,
        data_quality_score=1.0 if evidence_items else 0.5,
        missing_indicators=missing_indicators,
    )

    return {"evidence_bundle": bundle}
