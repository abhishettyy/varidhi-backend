"""P6 Marine Opportunity Scoring Engine.

Calculates deterministic multicriteria opportunity scores (0-100) for candidate marine zones
based on oceanographic convergence features (PFZ, SST thermal fronts, Chlorophyll-a, Distance).

IMPORTANT SCIENTIFIC BOUNDARY & DISCLAIMER:
The calculated opportunity score is a heuristic decision-support indicator reflecting oceanographic
productivity and thermal boundary alignment. It is NOT a scientifically validated probability of fish presence.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.agents.analytics.schemas import (
    OpportunityAnalysisResult,
    OpportunityComponents,
    OpportunityWeights,
    RawOpportunityFeatures,
    ZoneOpportunityScore,
)

# =====================================================================
# DEFAULT HEURISTIC WEIGHT CONSTANTS
# =====================================================================
# These weights represent multi-criteria oceanographic heuristics:
# - PFZ (40%): Direct multi-sensor satellite convergence product from oceanographic institutes.
# - SST Front (25%): Thermal boundary / upwelling zone where pelagics aggregate.
# - Chlorophyll-a (25%): Ocean color biological primary productivity proxy.
# - Distance (10%): Operational efficiency / accessibility penalty for coastal craft.
DEFAULT_PFZ_WEIGHT: float = 0.40
DEFAULT_SST_FRONT_WEIGHT: float = 0.25
DEFAULT_CHLOROPHYLL_WEIGHT: float = 0.25
DEFAULT_DISTANCE_WEIGHT: float = 0.10

# =====================================================================
# NORMALIZATION BOUNDS
# =====================================================================
MAX_SST_GRADIENT_DELTA_C: float = 1.2     # deg C delta across thermal front
MAX_SST_GRADIENT_C_PER_KM: float = 0.25  # deg C / km
MAX_CHLOROPHYLL_MG_M3: float = 4.0       # mg/m^3 upper coastal productivity threshold
MAX_OPERATIONAL_DISTANCE_NM: float = 30.0 # NM operational radius for coastal vessels


def parse_numeric_gradient(value: Any) -> Optional[float]:
    """
    Extracts a numeric float from either a float/int or descriptive gradient string
    (e.g., 'High thermal front (0.9°C delta)' -> 0.9).
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*°?C", value, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        # Fallback regex for pure numbers in string
        match_num = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
        if match_num:
            try:
                return float(match_num.group(1))
            except (ValueError, TypeError):
                pass
    return None


def normalize_pfz_confidence(confidence: Optional[float]) -> Optional[float]:
    """
    Normalize PFZ advisory confidence [0.0, 1.0] -> [0.0, 100.0].
    Returns None if value is None or invalid type.
    """
    if confidence is None:
        return None
    try:
        val = float(confidence)
    except (ValueError, TypeError):
        return None
    
    # Handle out-of-bounds inputs gracefully
    val = max(0.0, min(1.0, val))
    return round(val * 100.0, 2)


def normalize_sst_gradient(
    gradient_delta: Optional[Union[float, str]] = None,
    gradient_c_per_km: Optional[float] = None,
    max_delta: float = MAX_SST_GRADIENT_DELTA_C,
) -> Optional[float]:
    """
    Normalize SST thermal front gradient [0.0, max_delta] -> [0.0, 100.0].
    Higher thermal front gradients indicate upwelling edges / convergence.
    """
    delta_val = parse_numeric_gradient(gradient_delta)
    if delta_val is not None:
        clamped = max(0.0, min(max_delta, delta_val))
        return round((clamped / max_delta) * 100.0, 2)

    if gradient_c_per_km is not None:
        try:
            g_val = float(gradient_c_per_km)
            clamped = max(0.0, min(MAX_SST_GRADIENT_C_PER_KM, g_val))
            return round((clamped / MAX_SST_GRADIENT_C_PER_KM) * 100.0, 2)
        except (ValueError, TypeError):
            pass

    return None


def normalize_chlorophyll(
    chla_mg_m3: Optional[Union[float, str]] = None,
    max_chla: float = MAX_CHLOROPHYLL_MG_M3,
) -> Optional[float]:
    """
    Normalize Chlorophyll-a ocean color concentration [0.0, max_chla] -> [0.0, 100.0].
    Chlorophyll is a biological primary productivity proxy (phytoplankton biomass).
    """
    if chla_mg_m3 is None:
        return None
    try:
        val = float(chla_mg_m3)
    except (ValueError, TypeError):
        return None

    if val < 0.0:
        return 0.0
    clamped = min(max_chla, val)
    return round((clamped / max_chla) * 100.0, 2)


def normalize_distance(
    distance_nm: Optional[Union[float, str]],
    max_distance_nm: float = MAX_OPERATIONAL_DISTANCE_NM,
) -> Optional[float]:
    """
    Normalize distance from vessel/harbor [0.0, max_distance_nm] -> [100.0, 0.0].
    Closer zones receive higher operational proximity score.
    """
    if distance_nm is None:
        return None
    try:
        dist = float(distance_nm)
    except (ValueError, TypeError):
        return None

    if dist < 0.0:
        return 100.0  # Zero distance equivalent
    if dist >= max_distance_nm:
        return 0.0
    
    score = (1.0 - (dist / max_distance_nm)) * 100.0
    return round(score, 2)


def derive_convergence_grade(opportunity_score: float) -> str:
    """Classify overall opportunity score into standard convergence tiers."""
    if opportunity_score >= 85.0:
        return "High"
    elif opportunity_score >= 70.0:
        return "Moderate-High"
    elif opportunity_score >= 50.0:
        return "Moderate"
    else:
        return "Low"


def generate_explanation_factors(
    raw: RawOpportunityFeatures,
    components: OpportunityComponents,
    missing_features: List[str],
) -> List[str]:
    """Generate machine-readable explanatory factors for downstream evidence and reasoning."""
    factors: List[str] = []

    # 1. PFZ Factor
    if components.pfz is not None and raw.pfz_confidence is not None:
        if components.pfz >= 85.0:
            factors.append(f"strong PFZ advisory confidence ({raw.pfz_confidence:.2f})")
        elif components.pfz >= 70.0:
            factors.append(f"good PFZ advisory confidence ({raw.pfz_confidence:.2f})")
        elif components.pfz >= 50.0:
            factors.append(f"moderate PFZ advisory confidence ({raw.pfz_confidence:.2f})")
        else:
            factors.append(f"low PFZ advisory confidence ({raw.pfz_confidence:.2f})")

    # 2. SST Front Factor
    if components.sst_front is not None:
        delta_str = f"{raw.sst_gradient_delta:.1f}°C delta" if raw.sst_gradient_delta is not None else "detected"
        if components.sst_front >= 75.0:
            factors.append(f"strong thermal-front gradient ({delta_str})")
        elif components.sst_front >= 50.0:
            factors.append(f"moderate thermal-front gradient ({delta_str})")
        else:
            factors.append(f"weak thermal gradient ({delta_str})")

    # 3. Chlorophyll Factor
    if components.chlorophyll is not None and raw.chlorophyll_a_mg_m3 is not None:
        if components.chlorophyll >= 70.0:
            factors.append(f"high chlorophyll-a concentration ({raw.chlorophyll_a_mg_m3:.1f} mg/m³)")
        elif components.chlorophyll >= 50.0:
            factors.append(f"moderate-high chlorophyll-a ({raw.chlorophyll_a_mg_m3:.1f} mg/m³)")
        else:
            factors.append(f"low chlorophyll concentration ({raw.chlorophyll_a_mg_m3:.1f} mg/m³)")

    # 4. Distance Factor
    if components.distance is not None and raw.distance_nm is not None:
        if components.distance >= 70.0:
            factors.append(f"favorable proximity ({raw.distance_nm:.1f} NM)")
        elif components.distance >= 40.0:
            factors.append(f"moderate operational distance ({raw.distance_nm:.1f} NM)")
        else:
            factors.append(f"extended distance ({raw.distance_nm:.1f} NM)")

    # 5. Missing features indicators
    for feat in missing_features:
        factors.append(f"missing {feat} (weights dynamically renormalized)")

    return factors


def calculate_zone_opportunity(
    zone_id: str,
    raw_features: Union[RawOpportunityFeatures, Dict[str, Any]],
    weights: Optional[OpportunityWeights] = None,
    max_distance_nm: float = MAX_OPERATIONAL_DISTANCE_NM,
) -> ZoneOpportunityScore:
    """
    Calculate deterministic opportunity score for a single candidate zone.
    
    Handles missing features via dynamic weight renormalization across available components.
    """
    if isinstance(raw_features, dict):
        # Extract and parse dictionary features safely
        delta_val = parse_numeric_gradient(raw_features.get("sst_gradient_delta") or raw_features.get("gradient_delta") or raw_features.get("gradient"))
        raw = RawOpportunityFeatures(
            zone_id=zone_id,
            pfz_confidence=raw_features.get("pfz_confidence") or raw_features.get("confidence"),
            sst_celsius=raw_features.get("sst_celsius") or raw_features.get("sst"),
            sst_gradient_delta=delta_val,
            sst_gradient_c_per_km=raw_features.get("sst_gradient_c_per_km"),
            chlorophyll_a_mg_m3=raw_features.get("chlorophyll_a_mg_m3") or raw_features.get("chla_mg_m3") or raw_features.get("chlorophyll"),
            chlorophyll_density=raw_features.get("chlorophyll_density") or raw_features.get("density"),
            distance_nm=raw_features.get("distance_nm") or raw_features.get("distance"),
            depth_m=raw_features.get("depth_m"),
            species=raw_features.get("species"),
            latitude=raw_features.get("latitude") or raw_features.get("lat"),
            longitude=raw_features.get("longitude") or raw_features.get("lon"),
        )
    else:
        raw = raw_features

    w = weights or OpportunityWeights()
    base_weights = {
        "pfz": w.pfz,
        "sst_front": w.sst_front,
        "chlorophyll": w.chlorophyll,
        "distance": w.distance,
    }

    # Normalize each feature
    c_pfz = normalize_pfz_confidence(raw.pfz_confidence)
    c_sst = normalize_sst_gradient(raw.sst_gradient_delta, raw.sst_gradient_c_per_km)
    c_chl = normalize_chlorophyll(raw.chlorophyll_a_mg_m3)
    c_dist = normalize_distance(raw.distance_nm, max_distance_nm=max_distance_nm)

    components = OpportunityComponents(
        pfz=c_pfz,
        sst_front=c_sst,
        chlorophyll=c_chl,
        distance=c_dist,
    )

    available_components: Dict[str, float] = {}
    missing_features: List[str] = []

    if c_pfz is not None:
        available_components["pfz"] = c_pfz
    else:
        missing_features.append("pfz")

    if c_sst is not None:
        available_components["sst_front"] = c_sst
    else:
        missing_features.append("sst_front")

    if c_chl is not None:
        available_components["chlorophyll"] = c_chl
    else:
        missing_features.append("chlorophyll")

    if c_dist is not None:
        available_components["distance"] = c_dist
    else:
        missing_features.append("distance")

    # Dynamic Weight Renormalization
    active_weights: Dict[str, float] = {}
    total_active_weight = sum(base_weights[k] for k in available_components.keys())

    if total_active_weight > 0.0:
        for k in available_components.keys():
            active_weights[k] = round(base_weights[k] / total_active_weight, 4)
        
        weighted_score = sum(active_weights[k] * available_components[k] for k in available_components.keys())
        final_score = round(max(0.0, min(100.0, weighted_score)), 1)
    else:
        final_score = 0.0

    grade = derive_convergence_grade(final_score)
    explanation = generate_explanation_factors(raw, components, missing_features)

    return ZoneOpportunityScore(
        zone_id=zone_id,
        opportunity_score=final_score,
        convergence_grade=grade,
        components=components,
        raw_features=raw,
        weights_used=active_weights,
        missing_features=missing_features,
        explanation_factors=explanation,
        source="derived",
        method="heuristic_weighted_multicriteria",
    )


def calculate_opportunity_from_p4_results(
    pfz_result: Optional[Dict[str, Any]] = None,
    sst_result: Optional[Dict[str, Any]] = None,
    chlorophyll_result: Optional[Dict[str, Any]] = None,
    location: Optional[Dict[str, Any]] = None,
    weights: Optional[OpportunityWeights] = None,
    max_distance_nm: float = MAX_OPERATIONAL_DISTANCE_NM,
) -> OpportunityAnalysisResult:
    """
    Compute multi-zone opportunity scores from canonical P4 ToolResults.
    
    Correlates candidate zones across PFZ, SST, and Chlorophyll observations.
    """
    # 1. Discover all candidate zone IDs
    candidate_zones: Dict[str, Dict[str, Any]] = {}

    # Ingest PFZ zones
    if pfz_result and isinstance(pfz_result, dict):
        pfz_data = pfz_result.get("data", {})
        zones_list = pfz_data.get("zones", [])
        for z in zones_list:
            zid = z.get("zone_id")
            if zid:
                candidate_zones.setdefault(zid, {})
                candidate_zones[zid]["zone_id"] = zid
                candidate_zones[zid]["pfz_confidence"] = z.get("confidence")
                candidate_zones[zid]["distance_nm"] = z.get("distance_nm")
                candidate_zones[zid]["bearing"] = z.get("bearing")
                candidate_zones[zid]["depth_m"] = z.get("depth_m")
                candidate_zones[zid]["species"] = z.get("species")
                candidate_zones[zid]["latitude"] = z.get("latitude") or z.get("lat")
                candidate_zones[zid]["longitude"] = z.get("longitude") or z.get("lon")

    # Ingest SST zone gradients
    if sst_result and isinstance(sst_result, dict):
        sst_data = sst_result.get("data", {})
        zg = sst_data.get("zone_gradients") or sst_data.get("zone_data") or {}
        for zid, zd in zg.items():
            candidate_zones.setdefault(zid, {})
            candidate_zones[zid]["zone_id"] = zid
            candidate_zones[zid]["sst_celsius"] = zd.get("sst_celsius")
            delta_val = parse_numeric_gradient(zd.get("gradient") or zd.get("gradient_delta"))
            candidate_zones[zid]["sst_gradient_delta"] = delta_val
            if "latitude" in zd and "latitude" not in candidate_zones[zid]:
                candidate_zones[zid]["latitude"] = zd.get("latitude")
                candidate_zones[zid]["longitude"] = zd.get("longitude")

    # Ingest Chlorophyll zone data
    if chlorophyll_result and isinstance(chlorophyll_result, dict):
        chl_data = chlorophyll_result.get("data", {})
        zc = chl_data.get("zone_chlorophyll") or chl_data.get("zone_data") or {}
        for zid, zd in zc.items():
            candidate_zones.setdefault(zid, {})
            candidate_zones[zid]["zone_id"] = zid
            candidate_zones[zid]["chlorophyll_a_mg_m3"] = zd.get("chla_mg_m3") or zd.get("chlorophyll_a_mg_m3")
            candidate_zones[zid]["chlorophyll_density"] = zd.get("density")
            if "latitude" in zd and "latitude" not in candidate_zones[zid]:
                candidate_zones[zid]["latitude"] = zd.get("latitude")
                candidate_zones[zid]["longitude"] = zd.get("longitude")

    # Fallback if no zones found in dependencies
    if not candidate_zones:
        return OpportunityAnalysisResult(
            status="partial",
            zones=[],
            best_opportunity_zone_id=None,
            highest_opportunity_score=None,
            disclaimer="Heuristic fishing opportunity indicator based on oceanographic convergence; not a validated probability of fish presence.",
            source="P6_ANALYTICS_OPPORTUNITY",
        )

    # 2. Score each candidate zone
    scored_zones: List[ZoneOpportunityScore] = []
    for zid in sorted(candidate_zones.keys()):
        raw_feat = candidate_zones[zid]
        zone_score = calculate_zone_opportunity(
            zone_id=zid,
            raw_features=raw_feat,
            weights=weights,
            max_distance_nm=max_distance_nm,
        )
        scored_zones.append(zone_score)

    # 3. Identify best opportunity zone (purely based on opportunity; risk/legal filtering happens in P6 ranking)
    best_zone = max(scored_zones, key=lambda x: x.opportunity_score) if scored_zones else None

    return OpportunityAnalysisResult(
        status="success",
        zones=scored_zones,
        best_opportunity_zone_id=best_zone.zone_id if best_zone else None,
        highest_opportunity_score=best_zone.opportunity_score if best_zone else None,
        disclaimer="Heuristic fishing opportunity indicator based on oceanographic convergence; not a validated probability of fish presence.",
        source="P6_ANALYTICS_OPPORTUNITY",
    )


def calculate_opportunity_tool_entrypoint(
    parameters: Dict[str, Any],
    dependencies: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Tool registry adapter compatible with DAG Executor StepType.ANALYTICS invocation.
    
    Extracts upstream dependencies (pfz, sst, chlorophyll), performs deterministic scoring,
    and returns a canonical ToolResult envelope.
    """
    pfz_res = dependencies.get("pfz")
    sst_res = dependencies.get("sst")
    chl_res = dependencies.get("chlorophyll")
    location = parameters.get("location")

    analysis_res = calculate_opportunity_from_p4_results(
        pfz_result=pfz_res,
        sst_result=sst_res,
        chlorophyll_result=chl_res,
        location=location,
    )

    scored_zones_dict = [z.to_dict() for z in analysis_res.zones]
    
    # Recommended hotspots representation for backward compatibility with evidence assembly
    recommended_hotspots = [
        {
            "zone_id": z.zone_id,
            "latitude": z.raw_features.latitude,
            "longitude": z.raw_features.longitude,
            "bearing": getattr(z.raw_features, "bearing", None),
            "distance_nm": z.raw_features.distance_nm,
            "target_depth_m": z.raw_features.depth_m,
            "likely_species": z.raw_features.species or [],
            "opportunity_score": z.opportunity_score,
            "convergence_grade": z.convergence_grade,
        }
        for z in analysis_res.zones
    ]

    return {
        "status": "success",
        "source": "P6_ANALYTICS_OPPORTUNITY",
        "operation": "calculate_opportunity",
        "observation_time": None,
        "valid_time": None,
        "data": {
            "opportunity_evaluated": True,
            "scored_zones": scored_zones_dict,
            "best_opportunity_zone_id": analysis_res.best_opportunity_zone_id,
            "highest_opportunity_score": analysis_res.highest_opportunity_score,
            "recommended_hotspots": recommended_hotspots,
            "disclaimer": analysis_res.disclaimer,
        },
        "quality": "deterministic_analytical",
        "metadata": {
            "source_type": "derived",
            "model": "P6_MULTICRITERIA_OPPORTUNITY_v1",
            "weights": {
                "pfz": DEFAULT_PFZ_WEIGHT,
                "sst_front": DEFAULT_SST_FRONT_WEIGHT,
                "chlorophyll": DEFAULT_CHLOROPHYLL_WEIGHT,
                "distance": DEFAULT_DISTANCE_WEIGHT,
            },
        },
    }
