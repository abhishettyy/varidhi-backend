"""Evidence assembly node: structures multi-source tool and analytic outputs into verifiable evidence."""

import uuid
from typing import Any, Dict, List

from backend.agents.schemas.evidence import (
    EvidenceBundle,
    EvidenceItem,
    EvidenceType,
)
from backend.agents.state.marine_state import MarineState


async def evidence_assembly_node(state: MarineState) -> Dict[str, Any]:
    """
    LangGraph node: Normalizes and structures results from P4 tools and P6 analytics into a coherent EvidenceBundle.
    """
    raw_query = state.get("query", "") or state.get("raw_query", "")
    tool_results = state.get("tool_results", [])
    analytics_results = state.get("analytics_results", [])
    location = state.get("location") or {}
    spatial_tag = location.get("name") if isinstance(location, dict) else "Coastal Waters"

    evidence_items: List[EvidenceItem] = []
    missing_indicators: List[str] = []

    # 1. Process P4 Tool Results
    for entry in tool_results:
        op = entry.get("operation", "")
        res = entry.get("result", {})
        data = res.get("data", {})
        source = res.get("source", "P4_TOOL_INTEGRATION")

        if op in ("fetch_ocean_weather", "get_wind", "get_wave", "get_swell", "get_tide", "get_currents"):
            wave = data.get("wave_height_m") or data.get("significant_wave_height_m") or data.get("swell_height_m")
            wind = data.get("wind_speed_knots") or data.get("speed_knots")
            vis = data.get("visibility_km")
            summary_parts = []
            if wave is not None:
                summary_parts.append(f"Wave height {wave}m")
            if wind is not None:
                summary_parts.append(f"Wind {wind} kts")
            if vis is not None:
                summary_parts.append(f"Visibility {vis}km")
            summary = ", ".join(summary_parts) if summary_parts else f"Marine weather observation ({op})"

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
        elif op in ("get_sst", "fetch_sst_data"):
            sst = data.get("mean_sst_celsius") or data.get("value")
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
        elif op in ("get_chlorophyll", "fetch_chlorophyll_data"):
            chla = data.get("chlorophyll_a_mg_m3") or data.get("value")
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
        elif op in ("get_pfz", "fetch_pfz"):
            zones = data.get("zones", [])
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.PFZ_ZONE_ANALYTICS,
                    source=source,
                    summary=f"PFZ feed: {len(zones)} potential candidate zone(s) identified.",
                    metrics={"zone_count": len(zones), "zones": zones},
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )
        elif op in ("check_restrictions", "check_geofence"):
            restricted = data.get("restricted", False)
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.GENERAL_OBSERVATION,
                    source=source,
                    summary=f"Maritime restrictions check: {'Restricted' if restricted else 'Clear'}",
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
        else:
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_{uuid.uuid4().hex[:6]}",
                    evidence_type=EvidenceType.GENERAL_OBSERVATION,
                    source=source,
                    summary=f"Data retrieved for {op}",
                    metrics=data,
                    spatial_tag=spatial_tag,
                    raw_payload=data,
                )
            )

    # 2. Process P6 Analytics Results
    for entry in analytics_results:
        op = entry.get("operation", "")
        res = entry.get("result", {})
        data = res.get("data", {})
        source = res.get("source", "P6_MARINE_ANALYTICS")

        if op in ("calculate_sea_state_risk", "calculate_marine_risk"):
            score = data.get("risk_score") or data.get("score")
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
        elif op in ("compute_pfz_zones", "calculate_opportunity", "rank_zones"):
            hotspots = data.get("recommended_hotspots") or data.get("ranked_zones") or data.get("zones", [])
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

    return {
        "evidence_bundle": bundle,
        "evidence": [item.model_dump() for item in evidence_items],
    }
