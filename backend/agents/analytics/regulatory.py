"""P6 Regulatory & Marine Spatial Restrictions Engine.

Acts as a non-negotiable HARD FILTER to evaluate whether candidate marine zones are legally
and regulatorily permissible for fishing operations.

Evaluates:
- Marine Protected Areas (MPAs)
- Naval / Military Exclusion Zones
- Seasonal & Temporary Biological Closures
- Commercial Shipping Lane Traffic Caution Corridors
- Maritime Jurisdictional Boundaries

IMPORTANT ARCHITECTURAL & LEGAL BOUNDARY:
1. Regulatory restrictions are hard constraints: neither high opportunity scores nor calm sea-state conditions can override an active hard block.
2. Missing or unresolvable jurisdiction yields UNKNOWN (eligible=False, hard_block=False).
3. All spatial geometries and regulations in this engine are synthetic test artifacts for platform architecture verification.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.agents.analytics.schemas import (
    ComplianceStatus,
    RegulatoryAnalysisResult,
    RegulatoryCheck,
    RegulatoryDecision,
    Restriction,
    RestrictionType,
)
from backend.agents.mocks.fixtures.regulatory_mangalore import (
    MANGALORE_REGULATORY_REFERENCE_TIME,
    get_synthetic_restrictions,
)


def is_point_in_polygon(
    lat: float,
    lon: float,
    polygon_coordinates: Union[List[List[float]], List[Tuple[float, float]], List[Any]],
) -> bool:
    """
    Deterministic 2D Ray-Casting algorithm to test if (lat, lon) is inside a polygon.
    Supports GeoJSON coordinates format: [[lon, lat], [lon, lat], ...] or [[[lon, lat], ...]].
    """
    if not polygon_coordinates:
        return False

    # Normalize nested GeoJSON Polygon coordinates: [[[lon, lat], ...]] -> [[lon, lat], ...]
    coords = polygon_coordinates
    if isinstance(coords[0], (list, tuple)) and len(coords[0]) > 0 and isinstance(coords[0][0], (list, tuple)):
        coords = coords[0]

    # Convert coordinates to (px, py) = (lon, lat)
    points: List[Tuple[float, float]] = []
    for pt in coords:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            # Standard GeoJSON is [lon, lat]
            points.append((float(pt[0]), float(pt[1])))

    if len(points) < 3:
        return False

    px, py = float(lon), float(lat)
    inside = False
    n = len(points)
    p1x, p1y = points[0]

    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        # Check if point lies exactly on vertex or horizontal segment
        if (p1x == px and p1y == py) or (p2x == px and p2y == py):
            return True

        if py > min(p1y, p2y):
            if py <= max(p1y, p2y):
                if px <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    else:
                        xinters = p1x
                    if p1x == p2x or px <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def is_restriction_temporally_active(
    restriction: Restriction,
    reference_time: Optional[str] = None,
) -> bool:
    """
    Evaluates whether a restriction is active at the given reference timestamp.
    Handles permanent, active, expired, and scheduled future restrictions.
    """
    if restriction.status in ("inactive", "expired"):
        return False

    ref_time_str = reference_time or MANGALORE_REGULATORY_REFERENCE_TIME

    # Check start validity
    if restriction.valid_from:
        if ref_time_str < restriction.valid_from:
            return False  # Future, not yet active

    # Check end validity
    if restriction.valid_to:
        if ref_time_str > restriction.valid_to:
            return False  # Expired

    return True


def check_spatial_intersection(
    zone_id: Optional[str],
    lat: Optional[float],
    lon: Optional[float],
    restriction: Restriction,
) -> bool:
    """
    Evaluates whether a candidate zone matches a restriction via direct zone ID binding
    or geometric point-in-polygon containment.
    """
    # 1. Direct zone ID binding
    if restriction.zone_id and zone_id:
        if restriction.zone_id.upper() == zone_id.upper():
            return True

    # 2. Geometric containment
    if restriction.geometry and lat is not None and lon is not None:
        geom = restriction.geometry
        geom_type = geom.get("type", "").lower()
        if geom_type == "polygon":
            coords = geom.get("coordinates", [])
            if is_point_in_polygon(lat, lon, coords):
                return True
        elif geom_type == "point":
            # Point + radius buffer check
            pt_lon, pt_lat = geom.get("coordinates", [0, 0])
            radius_nm = geom.get("radius_nm", 1.0)
            # Rough Euclidean degree approximation: 1 deg lat ≈ 60 NM
            dist_nm = (((lat - pt_lat) * 60) ** 2 + ((lon - pt_lon) * 60 * 0.97) ** 2) ** 0.5
            if dist_nm <= radius_nm:
                return True

    return False


def evaluate_zone_compliance(
    zone_id: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    restrictions: Optional[List[Restriction]] = None,
    reference_time: Optional[str] = None,
    jurisdiction_known: bool = True,
) -> RegulatoryCheck:
    """
    Evaluate deterministic compliance for a single candidate zone.
    
    Hard Filter Semantics:
    - Active Hard Restriction -> BLOCKED (eligible=False, hard_block=True)
    - Active Advisory Only -> ELIGIBLE (eligible=True, hard_block=False, warnings=[...])
    - Unresolved Jurisdiction / Missing Data -> UNKNOWN (eligible=False, hard_block=False)
    - Clear -> ELIGIBLE (eligible=True, hard_block=False)
    """
    ref_time = reference_time or MANGALORE_REGULATORY_REFERENCE_TIME
    catalog = restrictions if restrictions is not None else get_synthetic_restrictions()

    # Handle unknown jurisdiction
    if not jurisdiction_known:
        return RegulatoryCheck(
            zone_id=zone_id,
            status=ComplianceStatus.UNKNOWN.value,
            eligible=False,
            hard_block=False,
            restrictions_found=[],
            blocking_restrictions=[],
            warnings=["Unresolved maritime jurisdiction or unmapped coastal buffer"],
            reasons=["Regulatory boundary data is unavailable for this spatial sector"],
            checked_at=ref_time,
            provenance="synthetic_regulatory_fixture",
            method="deterministic_spatial_regulatory_check",
        )

    restrictions_found: List[Restriction] = []
    blocking_restrictions: List[Restriction] = []
    warnings: List[str] = []
    reasons: List[str] = []

    for r in catalog:
        # Check if restriction intersects spatial zone
        if check_spatial_intersection(zone_id, latitude, longitude, r):
            # Check if restriction is currently temporally active
            if is_restriction_temporally_active(r, ref_time):
                restrictions_found.append(r)
                if r.is_hard_block:
                    blocking_restrictions.append(r)
                    reasons.append(f"HARD BLOCK: {r.name} ({r.restriction_type}) - {r.reason}")
                else:
                    warnings.append(f"ADVISORY: {r.name} ({r.restriction_type}) - {r.reason}")

    if blocking_restrictions:
        status = ComplianceStatus.BLOCKED.value
        eligible = False
        hard_block = True
    else:
        status = ComplianceStatus.ELIGIBLE.value
        eligible = True
        hard_block = False
        if not warnings:
            reasons.append("Zone is clear of all active spatial restrictions and conservation closures")

    return RegulatoryCheck(
        zone_id=zone_id,
        status=status,
        eligible=eligible,
        hard_block=hard_block,
        restrictions_found=restrictions_found,
        blocking_restrictions=blocking_restrictions,
        warnings=warnings,
        reasons=reasons,
        checked_at=ref_time,
        provenance="synthetic_regulatory_fixture",
        method="deterministic_spatial_regulatory_check",
    )


def evaluate_regulatory_compliance_from_p4_results(
    restrictions_result: Optional[Dict[str, Any]] = None,
    candidate_zones: Optional[List[Dict[str, Any]]] = None,
    location: Optional[Dict[str, Any]] = None,
    reference_time: Optional[str] = None,
) -> RegulatoryAnalysisResult:
    """
    Batch compliance evaluator across all candidate zones.
    Ingests P4 ToolResults from check_restrictions or candidate zone lists.
    """
    ref_time = reference_time or MANGALORE_REGULATORY_REFERENCE_TIME
    catalog = get_synthetic_restrictions()

    # 1. Discover all candidate zones
    zones_map: Dict[str, Dict[str, Any]] = {}

    # Ingest from candidate_zones parameter if passed
    if candidate_zones:
        for z in candidate_zones:
            zid = z.get("zone_id")
            if zid:
                zones_map[zid] = z

    # Ingest from restrictions_result
    if restrictions_result and isinstance(restrictions_result, dict):
        restr_data = restrictions_result.get("data", {})
        zr = restr_data.get("zone_restrictions", {})
        for zid, zd in zr.items():
            zones_map.setdefault(zid, {})
            zones_map[zid]["zone_id"] = zid
            zones_map[zid]["latitude"] = zd.get("latitude")
            zones_map[zid]["longitude"] = zd.get("longitude")
            zones_map[zid]["restricted_flag"] = zd.get("restricted")

    # Fallback if no zones found
    if not zones_map:
        return RegulatoryAnalysisResult(
            status=ComplianceStatus.INSUFFICIENT_DATA.value,
            zones=[],
            eligible_zone_ids=[],
            blocked_zone_ids=[],
            unknown_zone_ids=[],
            disclaimer="Synthetic regulatory fixture — not an official legal boundary or government navigation advisory.",
            source="P6_ANALYTICS_REGULATORY",
        )

    # 2. Evaluate each zone
    evaluated_zones: List[RegulatoryCheck] = []
    eligible_ids: List[str] = []
    blocked_ids: List[str] = []
    unknown_ids: List[str] = []

    for zid in sorted(zones_map.keys()):
        zd = zones_map[zid]
        lat = zd.get("latitude") or zd.get("lat")
        lon = zd.get("longitude") or zd.get("lon")
        
        check = evaluate_zone_compliance(
            zone_id=zid,
            latitude=lat,
            longitude=lon,
            restrictions=catalog,
            reference_time=ref_time,
        )
        evaluated_zones.append(check)

        if check.status == ComplianceStatus.ELIGIBLE.value:
            eligible_ids.append(zid)
        elif check.status == ComplianceStatus.BLOCKED.value:
            blocked_ids.append(zid)
        else:
            unknown_ids.append(zid)

    return RegulatoryAnalysisResult(
        status="success",
        zones=evaluated_zones,
        eligible_zone_ids=eligible_ids,
        blocked_zone_ids=blocked_ids,
        unknown_zone_ids=unknown_ids,
        disclaimer="Synthetic regulatory fixture — not an official legal boundary or government navigation advisory.",
        source="P6_ANALYTICS_REGULATORY",
    )


def calculate_regulatory_compliance_tool_entrypoint(
    parameters: Dict[str, Any],
    dependencies: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Tool registry adapter compatible with DAG Executor StepType.ANALYTICS and DATA operations.
    
    Provides canonical ToolResult envelope containing zone-by-zone regulatory compliance.
    """
    location = parameters.get("location", {})
    candidate_zones = parameters.get("zones")

    # If upstream dependencies have PFZ zones or restrictions
    if not candidate_zones:
        for dep in dependencies.values():
            if isinstance(dep, dict) and "zones" in dep.get("data", {}):
                candidate_zones = dep["data"]["zones"]
                break

    if not candidate_zones:
        from backend.agents.mocks.fixtures.mangalore_scenario import get_scenario_zones
        candidate_zones = get_scenario_zones(location)

    analysis_res = evaluate_regulatory_compliance_from_p4_results(
        restrictions_result=dependencies.get("restrictions"),
        candidate_zones=candidate_zones,
        location=location,
    )

    # Map for zone_compliance dictionary lookup by downstream decision nodes
    zone_compliance = {
        z.zone_id: {
            "is_legal": z.eligible,
            "status": z.status,
            "hard_block": z.hard_block,
            "protected_area": z.hard_block,
            "reasons": z.reasons,
            "warnings": z.warnings,
            "blocking_count": len(z.blocking_restrictions),
            "notes": "; ".join(z.reasons) if z.reasons else "Zone clear",
        }
        for z in analysis_res.zones
    }

    return {
        "status": "success",
        "source": "P6_ANALYTICS_REGULATORY",
        "operation": "check_restrictions",
        "observation_time": None,
        "valid_time": None,
        "data": {
            "regulatory_evaluated": True,
            "zone_compliance": zone_compliance,
            "eligible_zones": analysis_res.eligible_zone_ids,
            "blocked_zones": analysis_res.blocked_zone_ids,
            "unknown_zones": analysis_res.unknown_zone_ids,
            "scored_checks": [z.to_dict() for z in analysis_res.zones],
            "disclaimer": analysis_res.disclaimer,
        },
        "quality": "deterministic_gazette_fixture",
        "metadata": {
            "source_type": "synthetic",
            "model": "P6_SPATIAL_REGULATORY_FILTER_v1",
            "dataset": "SYNTHETIC_KARNATAKA_MARINE_SANCTUARY_CATALOG",
        },
    }
