"""P6 Marine Risk Engine.

Calculates deterministic multicriteria marine condition risk scores (0-100) and severity tiers
(LOW, MODERATE, HIGH, SEVERE) for candidate marine zones using coastal meteorological and oceanographic data
(significant wave height, sustained wind, wind gusts, swell height, and period context).

IMPORTANT SCIENTIFIC BOUNDARY & SAFETY DISCLAIMER:
This module provides a heuristic marine-condition risk indicator based on coastal meteorological and wave observations.
It is NOT a certified maritime safety system and does NOT constitute an official maritime clearance, port clearance,
or statutory navigation certificate.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from backend.agents.analytics.schemas import (
    RawRiskFeatures,
    RiskAnalysisResult,
    RiskComponents,
    RiskSeverity,
    RiskSeverityThresholds,
    RiskWeights,
    VesselProfile,
    ZoneRiskScore,
)

# =====================================================================
# DEFAULT HEURISTIC RISK WEIGHTS
# =====================================================================
# Weights reflect coastal craft physical hazard priorities:
# - Wave Height (35%): Primary hazard for hull swamping, broaching, and capsizing.
# - Wind Speed (25%): Drives coastal chop, vessel drift, and helm maneuvering difficulty.
# - Wind Gusts (15%): Sudden velocity spikes cause instantaneous roll instability.
# - Swell Height (15%): Long-energy heave adds hull displacement and coastal breaker energy.
DEFAULT_WAVE_WEIGHT: float = 0.35
DEFAULT_WIND_WEIGHT: float = 0.25
DEFAULT_GUST_WEIGHT: float = 0.15
DEFAULT_SWELL_WEIGHT: float = 0.15

# =====================================================================
# NORMALIZATION BOUNDS (DEMO MODEL)
# =====================================================================
MAX_WAVE_HEIGHT_M: float = 3.0       # 0.0 m -> 0, 3.0+ m -> 100
MAX_WIND_SPEED_KNOTS: float = 30.0   # 0 kts -> 0, 30+ kts -> 100
MAX_WIND_GUST_KNOTS: float = 40.0    # 0 kts -> 0, 40+ kts -> 100
MAX_SWELL_HEIGHT_M: float = 2.5      # 0.0 m -> 0, 2.5+ m -> 100

# =====================================================================
# VESSEL PROFILES CATALOG
# =====================================================================
VESSEL_PROFILES: Dict[str, VesselProfile] = {
    "small_traditional": VesselProfile(
        name="small_traditional",
        sensitivity_multiplier=1.25,
        max_safe_wave_m=1.2,
        max_safe_wind_kts=15.0,
        description="Small non-motorized / traditional canoe craft (<8m)"
    ),
    "motorized_traditional": VesselProfile(
        name="motorized_traditional",
        sensitivity_multiplier=1.10,
        max_safe_wave_m=1.5,
        max_safe_wind_kts=18.0,
        description="Motorized traditional fiberglass / dugout craft (8-12m)"
    ),
    "default": VesselProfile(
        name="default",
        sensitivity_multiplier=1.00,
        max_safe_wave_m=2.0,
        max_safe_wind_kts=20.0,
        description="Standard coastal fishing boat (10-15m)"
    ),
    "mechanized": VesselProfile(
        name="mechanized",
        sensitivity_multiplier=0.85,
        max_safe_wave_m=2.5,
        max_safe_wind_kts=25.0,
        description="Mechanized coastal gillnetter / ring-seiner (15-20m)"
    ),
    "trawler": VesselProfile(
        name="trawler",
        sensitivity_multiplier=0.70,
        max_safe_wave_m=3.0,
        max_safe_wind_kts=30.0,
        description="Heavy deep-sea / offshore commercial trawler (>20m)"
    ),
}


def normalize_wave_height(
    wave_m: Optional[Union[float, int, str]],
    max_m: float = MAX_WAVE_HEIGHT_M,
) -> Optional[float]:
    """Normalize significant wave height [0.0, max_m] -> [0.0, 100.0]."""
    if wave_m is None:
        return None
    try:
        val = float(wave_m)
    except (ValueError, TypeError):
        return None

    if val < 0.0:
        val = 0.0
    clamped = min(max_m, val)
    return round((clamped / max_m) * 100.0, 2)


def normalize_wind_speed(
    wind_kts: Optional[Union[float, int, str]],
    max_kts: float = MAX_WIND_SPEED_KNOTS,
) -> Optional[float]:
    """Normalize sustained wind speed [0.0, max_kts] -> [0.0, 100.0]."""
    if wind_kts is None:
        return None
    try:
        val = float(wind_kts)
    except (ValueError, TypeError):
        return None

    if val < 0.0:
        val = 0.0
    clamped = min(max_kts, val)
    return round((clamped / max_kts) * 100.0, 2)


def normalize_wind_gust(
    gust_kts: Optional[Union[float, int, str]],
    max_kts: float = MAX_WIND_GUST_KNOTS,
) -> Optional[float]:
    """Normalize wind gust speed [0.0, max_kts] -> [0.0, 100.0]."""
    if gust_kts is None:
        return None
    try:
        val = float(gust_kts)
    except (ValueError, TypeError):
        return None

    if val < 0.0:
        val = 0.0
    clamped = min(max_kts, val)
    return round((clamped / max_kts) * 100.0, 2)


def normalize_swell_height(
    swell_m: Optional[Union[float, int, str]],
    max_m: float = MAX_SWELL_HEIGHT_M,
) -> Optional[float]:
    """Normalize swell height [0.0, max_m] -> [0.0, 100.0]."""
    if swell_m is None:
        return None
    try:
        val = float(swell_m)
    except (ValueError, TypeError):
        return None

    if val < 0.0:
        val = 0.0
    clamped = min(max_m, val)
    return round((clamped / max_m) * 100.0, 2)


def derive_risk_severity(
    risk_score: float,
    thresholds: Optional[RiskSeverityThresholds] = None,
) -> str:
    """
    Classify aggregated risk score into deterministic severity categories:
    - 0 to 30: LOW
    - >30 to 60: MODERATE
    - >60 to 80: HIGH
    - >80 to 100: SEVERE
    """
    th = thresholds or RiskSeverityThresholds()
    if risk_score <= th.low_max:
        return RiskSeverity.LOW.value
    elif risk_score <= th.moderate_max:
        return RiskSeverity.MODERATE.value
    elif risk_score <= th.high_max:
        return RiskSeverity.HIGH.value
    else:
        return RiskSeverity.SEVERE.value


def evaluate_period_diagnostics(
    wave_height_m: Optional[float],
    wave_period_sec: Optional[float],
    swell_height_m: Optional[float],
    swell_period_sec: Optional[float],
) -> Tuple[Optional[str], List[str]]:
    """
    Physical oceanographic period evaluation.
    Rather than penalizing period monotonically, evaluates steepness and shoaling regimes:
    - Short period + high waves = steep choppy sea state (hull slamming risk).
    - Long period + high swell = groundswell shoaling / coastal breaker hazard.
    """
    warnings: List[str] = []
    context_desc: Optional[str] = None

    if wave_period_sec is not None:
        if wave_height_m is not None and wave_height_m >= 1.8 and wave_period_sec <= 6.0:
            context_desc = f"Steep wave chop ({wave_period_sec:.1f}s period)"
            warnings.append(f"Steep wave chop (period {wave_period_sec:.1f}s <= 6s) creates elevated slamming risk")
        elif wave_period_sec < 6.0:
            context_desc = f"Short wind chop ({wave_period_sec:.1f}s)"
        elif wave_period_sec <= 9.0:
            context_desc = f"Standard coastal sea-state ({wave_period_sec:.1f}s)"
        else:
            context_desc = f"Extended period wave train ({wave_period_sec:.1f}s)"

    if swell_period_sec is not None:
        if swell_height_m is not None and swell_height_m >= 1.5 and swell_period_sec >= 12.0:
            warnings.append(f"Long groundswell (period {swell_period_sec:.1f}s >= 12s) produces enhanced coastal shoaling hazard")
        if context_desc is None:
            context_desc = f"Ocean swell ({swell_period_sec:.1f}s)"

    return context_desc, warnings


def generate_risk_factors(
    raw: RawRiskFeatures,
    components: RiskComponents,
    vessel: VesselProfile,
) -> Tuple[List[str], List[str]]:
    """Generate machine-readable physical factors and operational threshold warnings."""
    factors: List[str] = []
    warnings: List[str] = []

    # 1. Wave Factors & Warnings
    if raw.wave_height_m is not None and components.wave is not None:
        if components.wave >= 66.0:
            factors.append(f"high significant wave height ({raw.wave_height_m:.1f}m)")
        elif components.wave >= 33.0:
            factors.append(f"moderate wave height ({raw.wave_height_m:.1f}m)")
        else:
            factors.append(f"calm sea state ({raw.wave_height_m:.1f}m)")

        if raw.wave_height_m > vessel.max_safe_wave_m:
            warnings.append(
                f"Significant wave height ({raw.wave_height_m:.1f}m) exceeds craft threshold ({vessel.max_safe_wave_m:.1f}m)"
            )

    # 2. Wind Factors & Warnings
    if raw.wind_speed_knots is not None and components.wind is not None:
        if components.wind >= 66.0:
            factors.append(f"strong sustained wind ({raw.wind_speed_knots:.1f} kts)")
        elif components.wind >= 33.0:
            factors.append(f"moderate coastal breeze ({raw.wind_speed_knots:.1f} kts)")
        else:
            factors.append(f"light wind ({raw.wind_speed_knots:.1f} kts)")

        if raw.wind_speed_knots > vessel.max_safe_wind_kts:
            warnings.append(
                f"Sustained wind ({raw.wind_speed_knots:.1f} kts) exceeds craft threshold ({vessel.max_safe_wind_kts:.1f} kts)"
            )

    # 3. Gust Factors
    if raw.wind_gust_knots is not None and components.gust is not None:
        if components.gust >= 60.0:
            factors.append(f"strong wind gusts ({raw.wind_gust_knots:.1f} kts)")
        if raw.wind_speed_knots is not None and (raw.wind_gust_knots - raw.wind_speed_knots) >= 6.0:
            factors.append(f"large gust spread ({raw.wind_gust_knots - raw.wind_speed_knots:.1f} kts delta)")

    # 4. Swell Factors
    if raw.swell_height_m is not None and components.swell is not None:
        if components.swell >= 60.0:
            factors.append(f"heavy ocean swell ({raw.swell_height_m:.1f}m)")
        elif components.swell >= 30.0:
            factors.append(f"moderate ocean swell ({raw.swell_height_m:.1f}m)")
        else:
            factors.append(f"low swell ({raw.swell_height_m:.1f}m)")

    return factors, warnings


def calculate_zone_risk(
    zone_id: str,
    raw_features: Union[RawRiskFeatures, Dict[str, Any]],
    weights: Optional[RiskWeights] = None,
    vessel_type: Optional[str] = "default",
    thresholds: Optional[RiskSeverityThresholds] = None,
) -> ZoneRiskScore:
    """
    Calculate deterministic marine condition risk score for a single candidate zone.
    
    Handles missing features via dynamic weight renormalization across available components.
    Applies craft-specific sensitivity multipliers.
    """
    if isinstance(raw_features, dict):
        raw = RawRiskFeatures(
            zone_id=zone_id,
            wave_height_m=raw_features.get("wave_height_m") or raw_features.get("significant_wave_height_m"),
            wave_period_sec=raw_features.get("wave_period_sec"),
            wave_direction_deg=raw_features.get("wave_direction_deg"),
            wind_speed_knots=raw_features.get("wind_speed_knots") or raw_features.get("speed_knots"),
            wind_gust_knots=raw_features.get("wind_gust_knots") or raw_features.get("gust_knots"),
            wind_direction_deg=raw_features.get("wind_direction_deg") or raw_features.get("direction_deg"),
            wind_direction_cardinal=raw_features.get("wind_direction_cardinal") or raw_features.get("direction_cardinal"),
            swell_height_m=raw_features.get("swell_height_m"),
            swell_period_sec=raw_features.get("swell_period_sec"),
            swell_direction_deg=raw_features.get("swell_direction_deg"),
            tide_height_m=raw_features.get("tide_height_m"),
            current_speed_knots=raw_features.get("current_speed_knots"),
            latitude=raw_features.get("latitude") or raw_features.get("lat"),
            longitude=raw_features.get("longitude") or raw_features.get("lon"),
        )
    else:
        raw = raw_features

    w = weights or RiskWeights()
    base_weights = {
        "wave": w.wave,
        "wind": w.wind,
        "gust": w.gust,
        "swell": w.swell,
    }

    # Normalize individual hazard components
    c_wave = normalize_wave_height(raw.wave_height_m)
    c_wind = normalize_wind_speed(raw.wind_speed_knots)
    c_gust = normalize_wind_gust(raw.wind_gust_knots)
    c_swell = normalize_swell_height(raw.swell_height_m)

    # Physical period diagnosis
    period_context, period_warnings = evaluate_period_diagnostics(
        wave_height_m=raw.wave_height_m,
        wave_period_sec=raw.wave_period_sec,
        swell_height_m=raw.swell_height_m,
        swell_period_sec=raw.swell_period_sec,
    )

    components = RiskComponents(
        wave=c_wave,
        wind=c_wind,
        gust=c_gust,
        swell=c_swell,
        period_context=period_context,
    )

    available_components: Dict[str, float] = {}
    missing_features: List[str] = []

    if c_wave is not None:
        available_components["wave"] = c_wave
    else:
        missing_features.append("wave")

    if c_wind is not None:
        available_components["wind"] = c_wind
    else:
        missing_features.append("wind")

    if c_gust is not None:
        available_components["gust"] = c_gust
    else:
        missing_features.append("gust")

    if c_swell is not None:
        available_components["swell"] = c_swell
    else:
        missing_features.append("swell")

    # Vessel profile lookup
    vprofile_key = vessel_type if vessel_type in VESSEL_PROFILES else "default"
    vessel = VESSEL_PROFILES[vprofile_key]

    # Dynamic Weight Renormalization
    active_weights: Dict[str, float] = {}
    total_active_weight = sum(base_weights[k] for k in available_components.keys())

    if total_active_weight > 0.0:
        for k in available_components.keys():
            active_weights[k] = round(base_weights[k] / total_active_weight, 4)
        
        raw_base_score = sum(active_weights[k] * available_components[k] for k in available_components.keys())
        # Apply vessel sensitivity multiplier
        adjusted_score = raw_base_score * vessel.sensitivity_multiplier
        final_risk_score = round(max(0.0, min(100.0, adjusted_score)), 1)
    else:
        final_risk_score = 0.0

    severity = derive_risk_severity(final_risk_score, thresholds)
    is_safe = final_risk_score < 50.0

    factors, thresh_warnings = generate_risk_factors(raw, components, vessel)
    all_warnings = thresh_warnings + period_warnings

    for feat in missing_features:
        factors.append(f"missing {feat} (weights dynamically renormalized)")

    return ZoneRiskScore(
        zone_id=zone_id,
        risk_score=final_risk_score,
        severity=severity,
        is_safe_heuristic=is_safe,
        components=components,
        raw_features=raw,
        vessel_profile_applied=vprofile_key,
        weights_used=active_weights,
        missing_features=missing_features,
        factors=factors,
        warnings=all_warnings,
        source="derived",
        method="heuristic_weighted_multicriteria",
    )


def calculate_marine_risk_from_p4_results(
    wind_result: Optional[Dict[str, Any]] = None,
    wave_result: Optional[Dict[str, Any]] = None,
    swell_result: Optional[Dict[str, Any]] = None,
    tide_result: Optional[Dict[str, Any]] = None,
    currents_result: Optional[Dict[str, Any]] = None,
    vessel_type: Optional[str] = "default",
    weights: Optional[RiskWeights] = None,
    thresholds: Optional[RiskSeverityThresholds] = None,
) -> RiskAnalysisResult:
    """
    Compute multi-zone marine risk scores from canonical P4 ToolResults.
    
    Correlates candidate zones across wind, wave, swell, tide, and currents observations.
    """
    candidate_zones: Dict[str, Dict[str, Any]] = {}

    # 1. Ingest Wind zones
    if wind_result and isinstance(wind_result, dict):
        w_data = wind_result.get("data", {})
        zw = w_data.get("zone_wind") or w_data.get("zone_data") or {}
        for zid, zd in zw.items():
            candidate_zones.setdefault(zid, {})
            candidate_zones[zid]["zone_id"] = zid
            candidate_zones[zid]["wind_speed_knots"] = zd.get("speed_knots") or zd.get("wind_speed_knots")
            candidate_zones[zid]["wind_gust_knots"] = (
                zd.get("gust_knots") if zd.get("gust_knots") is not None
                else zd.get("gusts") if zd.get("gusts") is not None
                else zd.get("wind_gust_knots")
            )
            candidate_zones[zid]["wind_direction_deg"] = zd.get("direction_deg") or zd.get("wind_direction_deg")
            candidate_zones[zid]["wind_direction_cardinal"] = zd.get("direction_cardinal") or zd.get("wind_direction_cardinal")
            candidate_zones[zid]["latitude"] = zd.get("latitude")
            candidate_zones[zid]["longitude"] = zd.get("longitude")

    # 2. Ingest Wave zones
    if wave_result and isinstance(wave_result, dict):
        wv_data = wave_result.get("data", {})
        zwv = wv_data.get("zone_wave") or wv_data.get("zone_data") or {}
        for zid, zd in zwv.items():
            candidate_zones.setdefault(zid, {})
            candidate_zones[zid]["zone_id"] = zid
            candidate_zones[zid]["wave_height_m"] = zd.get("wave_height_m") or zd.get("significant_wave_height_m")
            candidate_zones[zid]["wave_period_sec"] = zd.get("wave_period_sec")
            candidate_zones[zid]["wave_direction_deg"] = zd.get("wave_direction_deg")
            if "latitude" in zd and "latitude" not in candidate_zones[zid]:
                candidate_zones[zid]["latitude"] = zd.get("latitude")
                candidate_zones[zid]["longitude"] = zd.get("longitude")

    # 3. Ingest Swell zones
    if swell_result and isinstance(swell_result, dict):
        sw_data = swell_result.get("data", {})
        zsw = sw_data.get("zone_swell") or {}
        if zsw:
            for zid, zd in zsw.items():
                candidate_zones.setdefault(zid, {})
                candidate_zones[zid]["zone_id"] = zid
                candidate_zones[zid]["swell_height_m"] = zd.get("swell_height_m")
                candidate_zones[zid]["swell_period_sec"] = zd.get("swell_period_sec")
                candidate_zones[zid]["swell_direction_deg"] = zd.get("swell_direction_deg")
        elif sw_data.get("swell_height_m") is not None:
            # Fallback if swell is provided globally rather than per zone
            for zid in candidate_zones:
                candidate_zones[zid]["swell_height_m"] = sw_data.get("swell_height_m")
                candidate_zones[zid]["swell_period_sec"] = sw_data.get("swell_period_sec")
                candidate_zones[zid]["swell_direction_deg"] = sw_data.get("swell_direction_deg")

    # 4. Ingest Tide data (general background)
    tide_ht = None
    if tide_result and isinstance(tide_result, dict):
        tide_ht = tide_result.get("data", {}).get("height_m")

    # 5. Ingest Currents data (general background)
    curr_spd = None
    if currents_result and isinstance(currents_result, dict):
        curr_spd = currents_result.get("data", {}).get("speed_knots")

    for zid in candidate_zones:
        if tide_ht is not None:
            candidate_zones[zid]["tide_height_m"] = tide_ht
        if curr_spd is not None:
            candidate_zones[zid]["current_speed_knots"] = curr_spd

    # Fallback if no candidate zones found in dependencies
    if not candidate_zones:
        return RiskAnalysisResult(
            status="insufficient_data",
            zones=[],
            lowest_risk_zone_id=None,
            lowest_risk_score=None,
            vessel_profile=vessel_type or "default",
            disclaimer="Heuristic marine-condition risk indicator based on coastal meteorological and wave observations; not an official maritime safety clearance or statutory navigation certificate.",
            source="P6_ANALYTICS_RISK",
        )

    # 6. Score each candidate zone
    scored_zones: List[ZoneRiskScore] = []
    for zid in sorted(candidate_zones.keys()):
        raw_feat = candidate_zones[zid]
        zone_score = calculate_zone_risk(
            zone_id=zid,
            raw_features=raw_feat,
            weights=weights,
            vessel_type=vessel_type,
            thresholds=thresholds,
        )
        scored_zones.append(zone_score)

    # 7. Identify lowest risk zone
    safest_zone = min(scored_zones, key=lambda x: x.risk_score) if scored_zones else None

    return RiskAnalysisResult(
        status="success",
        zones=scored_zones,
        lowest_risk_zone_id=safest_zone.zone_id if safest_zone else None,
        lowest_risk_score=safest_zone.risk_score if safest_zone else None,
        vessel_profile=vessel_type or "default",
        disclaimer="Heuristic marine-condition risk indicator based on coastal meteorological and wave observations; not an official maritime safety clearance or statutory navigation certificate.",
        source="P6_ANALYTICS_RISK",
    )


def calculate_marine_risk_tool_entrypoint(
    parameters: Dict[str, Any],
    dependencies: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Tool registry adapter compatible with DAG Executor StepType.ANALYTICS invocation.
    
    Extracts upstream dependencies (wind, wave, swell, tide, currents), performs deterministic
    risk calculations, and returns a canonical ToolResult envelope.
    """
    wind_res = dependencies.get("wind") or dependencies.get("weather")
    wave_res = dependencies.get("wave") or dependencies.get("waves")
    swell_res = dependencies.get("swell")
    tide_res = dependencies.get("tide")
    curr_res = dependencies.get("currents") or dependencies.get("current")

    vessel_type = parameters.get("vessel_type") or parameters.get("vessel_profile") or "default"

    analysis_res = calculate_marine_risk_from_p4_results(
        wind_result=wind_res,
        wave_result=wave_res,
        swell_result=swell_res,
        tide_result=tide_res,
        currents_result=curr_res,
        vessel_type=vessel_type,
    )

    scored_zones_dict = [z.to_dict() for z in analysis_res.zones]

    # Map for zone_risks dictionary lookup by downstream ranking / decision nodes
    zone_risks = {
        z.zone_id: {
            "risk_score": z.risk_score,
            "severity": z.severity,
            "is_safe": z.is_safe_heuristic,
            "wave_height_m": z.raw_features.wave_height_m,
            "wind_speed_knots": z.raw_features.wind_speed_knots,
            "warnings": z.warnings,
        }
        for z in analysis_res.zones
    }

    mean_risk = (
        round(sum(z.risk_score for z in analysis_res.zones) / len(analysis_res.zones), 1)
        if analysis_res.zones
        else 0.0
    )

    return {
        "status": "success",
        "source": "P6_ANALYTICS_RISK",
        "operation": "calculate_marine_risk",
        "observation_time": None,
        "valid_time": None,
        "data": {
            "risk_evaluated": True,
            "risk_score": mean_risk,
            "severity": derive_risk_severity(mean_risk),
            "zone_risks": zone_risks,
            "scored_zones": scored_zones_dict,
            "lowest_risk_zone_id": analysis_res.lowest_risk_zone_id,
            "lowest_risk_score": analysis_res.lowest_risk_score,
            "vessel_profile": analysis_res.vessel_profile,
            "disclaimer": analysis_res.disclaimer,
        },
        "quality": "deterministic_analytical",
        "metadata": {
            "source_type": "derived",
            "model": "P6_MULTICRITERIA_MARINE_RISK_v1",
            "weights": {
                "wave": DEFAULT_WAVE_WEIGHT,
                "wind": DEFAULT_WIND_WEIGHT,
                "gust": DEFAULT_GUST_WEIGHT,
                "swell": DEFAULT_SWELL_WEIGHT,
            },
        },
    }
