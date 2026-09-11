"""Mock Tool Registry providing deterministic, dependency-aware simulated operations.

P3 Orchestration Mock Tool Registry:
- Simulates external P4 data retrieval and P6 scientific analytics.
- Strictly returns structured objects explicitly tagged with `"source": "mock"`.
- Enables end-to-end testing of complex DAGs without external network/API dependencies.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional


class ToolRegistry:
    """Registry mapping canonical operation names to execution handlers."""

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._register_defaults()

    def register(self, operation: str, handler: Callable) -> None:
        """Register a handler for a canonical operation name."""
        self._handlers[operation] = handler

    def has_operation(self, operation: str) -> bool:
        """Check if an operation is registered."""
        return operation in self._handlers

    async def execute(
        self,
        operation: str,
        parameters: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a registered operation with given parameters and dependency outputs.
        Returns a structured dictionary with status, source='mock', operation, and data payload.
        """
        params = parameters or {}
        deps = dependencies or {}

        if operation not in self._handlers:
            return {
                "status": "failed",
                "source": "mock",
                "operation": operation,
                "error": f"Unknown operation '{operation}'",
                "data": {},
            }

        handler = self._handlers[operation]
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(parameters=params, dependencies=deps)
            else:
                result = handler(parameters=params, dependencies=deps)

            # Ensure consistent envelope
            if isinstance(result, dict) and "status" in result and "source" in result:
                return result
            return {
                "status": "success",
                "source": "mock",
                "operation": operation,
                "data": result if isinstance(result, dict) else {"value": result},
            }
        except Exception as e:
            return {
                "status": "failed",
                "source": "mock",
                "operation": operation,
                "error": str(e),
                "data": {},
            }

    def _register_defaults(self) -> None:
        """Register all default mock handlers for canonical planner operations."""
        # 1. P4 Data Acquisition Operations
        self.register("get_pfz", mock_get_pfz)
        self.register("fetch_pfz", mock_get_pfz)
        self.register("get_sst", mock_get_sst)
        self.register("fetch_sst_data", mock_get_sst)
        self.register("get_chlorophyll", mock_get_chlorophyll)
        self.register("fetch_chlorophyll_data", mock_get_chlorophyll)
        self.register("get_wind", mock_get_wind)
        self.register("get_wave", mock_get_wave)
        self.register("get_swell", mock_get_swell)
        self.register("get_tide", mock_get_tide)
        self.register("fetch_ocean_weather", mock_fetch_ocean_weather)
        self.register("check_restrictions", mock_check_restrictions)
        self.register("check_geofence", mock_check_geofence)
        self.register("fetch_hazard_bulletins", mock_fetch_hazard_bulletins)
        self.register("get_vessel_position", mock_get_vessel_position)
        self.register("get_vessel_activity", mock_get_vessel_activity)
        self.register("get_historical_data", mock_get_historical_data)

        # 2. P6 Analytics & Calculation Operations
        self.register("calculate_opportunity", mock_calculate_opportunity)
        self.register("compute_pfz_zones", mock_calculate_opportunity)
        self.register("calculate_marine_risk", mock_calculate_marine_risk)
        self.register("calculate_sea_state_risk", mock_calculate_marine_risk)
        self.register("rank_zones", mock_rank_zones)
        self.register("calculate_distance", mock_calculate_distance)
        self.register("detect_algal_bloom_risk", mock_detect_algal_bloom_risk)
        self.register("analyze_historical_trends", mock_analyze_historical_trends)

        # 3. Decision & Synthesis Operations
        self.register("select_safe_fishing_zone", mock_select_safe_fishing_zone)
        self.register("evaluate_hazard", mock_evaluate_hazard)
        self.register("evaluate_route", mock_evaluate_route)
        self.register("generate_recommendation", mock_generate_recommendation)
        self.register("summarize_conditions", mock_summarize_conditions)
        self.register("explain_recommendation", mock_explain_recommendation)


# =====================================================================
# Mock Handler Implementations (North Star Coherent Multi-Zone Model)
# =====================================================================

def mock_get_pfz(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    loc_name = loc.get("name", "Mangalore")
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_pfz",
        "data": {
            "region": loc_name,
            "zones": [
                {
                    "zone_id": "ZONE_A",
                    "lat": 12.95,
                    "lon": 74.80,
                    "bearing": "WNW",
                    "distance_nm": 14.5,
                    "depth_m": 45,
                    "species": ["Pelagic Tuna", "Kingfish"],
                },
                {
                    "zone_id": "ZONE_B",
                    "lat": 12.90,
                    "lon": 74.95,
                    "bearing": "SSW",
                    "distance_nm": 8.2,
                    "depth_m": 35,
                    "species": ["Mackerel", "Sardines"],
                },
                {
                    "zone_id": "ZONE_C",
                    "lat": 12.82,
                    "lon": 75.05,
                    "bearing": "SSE",
                    "distance_nm": 18.0,
                    "depth_m": 60,
                    "species": ["Yellowfin Tuna", "Barracuda"],
                },
            ],
            "confidence": 0.88,
        },
    }


def mock_get_sst(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_sst",
        "data": {
            "mean_sst_celsius": 28.6,
            "gradient_celsius_per_km": 0.18,
            "has_thermal_front": True,
            "zone_gradients": {
                "ZONE_A": {"sst_celsius": 28.4, "gradient": "High thermal front (0.9°C delta)"},
                "ZONE_B": {"sst_celsius": 28.7, "gradient": "Moderate thermal front (0.6°C delta)"},
                "ZONE_C": {"sst_celsius": 28.2, "gradient": "Strong thermal front (1.1°C delta)"},
            },
        },
    }


def mock_get_chlorophyll(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_chlorophyll",
        "data": {
            "chlorophyll_a_mg_m3": 2.4,
            "productivity_index": "high",
            "zone_chlorophyll": {
                "ZONE_A": {"chla_mg_m3": 2.8, "density": "High"},
                "ZONE_B": {"chla_mg_m3": 2.3, "density": "Moderate-High"},
                "ZONE_C": {"chla_mg_m3": 3.1, "density": "Very High"},
            },
        },
    }


def mock_get_wind(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_wind",
        "data": {
            "wind_speed_knots": 12.5,
            "wind_gust_knots": 16.0,
            "wind_direction": "WSW",
            "zone_wind": {
                "ZONE_A": {"speed_knots": 22.0, "gusts": 28.0, "condition": "Strong breeze"},
                "ZONE_B": {"speed_knots": 11.0, "gusts": 14.0, "condition": "Moderate breeze"},
                "ZONE_C": {"speed_knots": 9.5, "gusts": 12.0, "condition": "Light-Moderate"},
            },
        },
    }


def mock_get_wave(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_wave",
        "data": {
            "wave_height_m": 1.3,
            "wave_period_sec": 6.5,
            "sea_state": "Slight to Moderate",
            "zone_wave": {
                "ZONE_A": {"wave_height_m": 2.4, "sea_roughness": "Rough"},
                "ZONE_B": {"wave_height_m": 1.1, "sea_roughness": "Calm-Slight"},
                "ZONE_C": {"wave_height_m": 1.0, "sea_roughness": "Calm"},
            },
        },
    }


def mock_get_swell(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_swell",
        "data": {
            "swell_height_m": 0.8,
            "swell_period_sec": 9.0,
            "swell_direction": "SSW",
        },
    }


def mock_get_tide(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_tide",
        "data": {
            "high_tide_time": "08:45 IST",
            "high_tide_height_m": 1.6,
            "low_tide_time": "14:30 IST",
            "low_tide_height_m": 0.4,
            "tidal_flow": "Ebb phase",
        },
    }


def mock_fetch_ocean_weather(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "fetch_ocean_weather",
        "data": {
            "wave_height_m": 1.2,
            "wind_speed_knots": 12.0,
            "swell_period_sec": 8.5,
            "wind_direction": "WSW",
            "visibility_km": 10.0,
        },
    }


def mock_check_restrictions(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "check_restrictions",
        "data": {
            "restrictions_checked": True,
            "zone_compliance": {
                "ZONE_A": {"is_legal": True, "protected_area": False, "notes": "Open territorial fishing waters"},
                "ZONE_B": {"is_legal": True, "protected_area": False, "notes": "Approved artisanal & mechanized fishing zone"},
                "ZONE_C": {"is_legal": False, "protected_area": True, "notes": "Marine Protected Sanctuary & Naval Exercise Corridor - RESTRICTED"},
            },
        },
    }


def mock_check_geofence(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or parameters.get("route") or {}
    return {
        "status": "success",
        "source": "mock",
        "operation": "check_geofence",
        "data": {
            "inside_eez": True,
            "inside_protected_area": False,
            "distance_to_boundary_km": 42.5,
            "location": loc,
        },
    }


def mock_fetch_hazard_bulletins(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "fetch_hazard_bulletins",
        "data": {
            "active_alerts": [],
            "cyclone_warning": False,
            "high_swell_advisory": False,
        },
    }


def mock_get_vessel_position(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    vessel = parameters.get("vessel") or {}
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_vessel_position",
        "data": {
            "vessel_id": vessel.get("id", "VESSEL_DEFAULT"),
            "latitude": 12.8681,
            "longitude": 74.8427,
            "speed_knots": 8.5,
            "heading": 245.0,
            "status": "underway",
        },
    }


def mock_get_vessel_activity(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_vessel_activity",
        "data": {
            "hours_at_sea": 4.2,
            "distance_traveled_nm": 32.0,
            "telemetry_status": "nominal",
        },
    }


def mock_get_historical_data(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    var = parameters.get("variable", "SST")
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_historical_data",
        "data": {
            "variable": var,
            "time_series": [
                {"date": "2026-08-15", "value": 28.5},
                {"date": "2026-08-25", "value": 28.7},
                {"date": "2026-09-05", "value": 28.6},
            ],
            "record_count": 30,
        },
    }


# =====================================================================
# Mock Analytics & Calculations (P6 Simulation)
# =====================================================================

def mock_calculate_opportunity(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    # Extract zones from dependencies if available
    pfz_dep = {}
    for dep_val in dependencies.values():
        if isinstance(dep_val, dict) and "zones" in dep_val.get("data", {}):
            pfz_dep = dep_val["data"]
            break

    zones = pfz_dep.get("zones", [
        {"zone_id": "ZONE_A", "lat": 12.95, "lon": 74.80},
        {"zone_id": "ZONE_B", "lat": 12.90, "lon": 74.95},
        {"zone_id": "ZONE_C", "lat": 12.82, "lon": 75.05},
    ])

    scores = {
        "ZONE_A": 94,
        "ZONE_B": 83,
        "ZONE_C": 96,
    }

    scored_zones = []
    for z in zones:
        zid = z.get("zone_id", "ZONE")
        score = scores.get(zid, 80)
        scored_zones.append({
            **z,
            "opportunity_score": score,
            "convergence_grade": "High" if score > 90 else "Good",
        })

    return {
        "status": "success",
        "source": "mock",
        "operation": "calculate_opportunity",
        "data": {
            "opportunity_evaluated": True,
            "scored_zones": scored_zones,
            "pfz_detected": True,
            "recommended_hotspots": [
                {
                    "zone_id": z.get("zone_id"),
                    "latitude": z.get("lat", 12.90),
                    "longitude": z.get("lon", 74.95),
                    "bearing": z.get("bearing", "SSW"),
                    "distance_nm": z.get("distance_nm", 8.2),
                    "target_depth_m": z.get("depth_m", 35),
                    "likely_species": z.get("species", ["Mackerel", "Sardines"]),
                    "opportunity_score": z.get("opportunity_score"),
                }
                for z in scored_zones
            ],
        },
    }


def mock_calculate_marine_risk(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    # Evaluate risk scores based on dependencies or default model
    risk_scores = {
        "ZONE_A": {"risk_score": 75.0, "severity": "danger_red", "is_safe": False, "wave_height_m": 2.4, "wind_speed_knots": 22.0},
        "ZONE_B": {"risk_score": 25.0, "severity": "safe_green", "is_safe": True, "wave_height_m": 1.1, "wind_speed_knots": 11.0},
        "ZONE_C": {"risk_score": 20.0, "severity": "safe_green", "is_safe": True, "wave_height_m": 1.0, "wind_speed_knots": 9.5},
    }

    # Aggregate overall general risk for single-location queries
    overall_score = 25.0
    overall_sev = "safe_green"

    return {
        "status": "success",
        "source": "mock",
        "operation": "calculate_marine_risk",
        "data": {
            "risk_score": overall_score,
            "severity": overall_sev,
            "zone_risks": risk_scores,
            "vessel_safety": "Permitted for small motorized coastal crafts (<15m)",
            "max_recommended_distance_nm": 15,
        },
    }


def mock_rank_zones(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    # Combine opportunity and risk from dependencies
    opportunity_zones = []
    zone_risks = {}

    for dep_val in dependencies.values():
        data = dep_val.get("data", {}) if isinstance(dep_val, dict) else {}
        if "scored_zones" in data:
            opportunity_zones = data["scored_zones"]
        if "zone_risks" in data:
            zone_risks = data["zone_risks"]

    if not opportunity_zones:
        opportunity_zones = [
            {"zone_id": "ZONE_C", "opportunity_score": 96, "lat": 12.82, "lon": 75.05, "bearing": "SSE", "distance_nm": 18.0},
            {"zone_id": "ZONE_A", "opportunity_score": 94, "lat": 12.95, "lon": 74.80, "bearing": "WNW", "distance_nm": 14.5},
            {"zone_id": "ZONE_B", "opportunity_score": 83, "lat": 12.90, "lon": 74.95, "bearing": "SSW", "distance_nm": 8.2},
        ]

    ranked = []
    for z in opportunity_zones:
        zid = z.get("zone_id")
        risk_info = zone_risks.get(zid, {"risk_score": 30.0, "is_safe": True})
        ranked.append({
            **z,
            "risk_score": risk_info.get("risk_score", 30.0),
            "is_safe": risk_info.get("is_safe", True),
        })

    # Sort primarily by opportunity score descending
    ranked.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    return {
        "status": "success",
        "source": "mock",
        "operation": "rank_zones",
        "data": {
            "ranked_zones": ranked,
        },
    }


def mock_select_safe_fishing_zone(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """
    North Star Decision:
    - ZONE_C: Opportunity 96, Risk 20, but Legal: False -> REJECTED.
    - ZONE_A: Opportunity 94, but Risk 75 (Rough Sea) -> REJECTED.
    - ZONE_B: Opportunity 83, Risk 25, Legal: True -> SELECTED as safe optimal zone.
    """
    ranked_zones = []
    restrictions = {}

    for dep_val in dependencies.values():
        data = dep_val.get("data", {}) if isinstance(dep_val, dict) else {}
        if "ranked_zones" in data:
            ranked_zones = data["ranked_zones"]
        if "zone_compliance" in data:
            restrictions = data["zone_compliance"]

    if not ranked_zones:
        ranked_zones = [
            {"zone_id": "ZONE_C", "opportunity_score": 96, "risk_score": 20, "is_safe": True, "lat": 12.82, "lon": 75.05, "bearing": "SSE", "distance_nm": 18.0},
            {"zone_id": "ZONE_A", "opportunity_score": 94, "risk_score": 75, "is_safe": False, "lat": 12.95, "lon": 74.80, "bearing": "WNW", "distance_nm": 14.5},
            {"zone_id": "ZONE_B", "opportunity_score": 83, "risk_score": 25, "is_safe": True, "lat": 12.90, "lon": 74.95, "bearing": "SSW", "distance_nm": 8.2},
        ]

    selected_zone = None
    evaluated_candidates = []

    for z in ranked_zones:
        zid = z.get("zone_id")
        comp = restrictions.get(zid, {"is_legal": zid != "ZONE_C", "notes": "Standard"})
        is_legal = comp.get("is_legal", True)
        is_safe = z.get("is_safe", True) and (z.get("risk_score", 100) < 50)

        decision_status = "REJECTED_LEGAL" if not is_legal else ("REJECTED_SAFETY" if not is_safe else "SELECTED")
        evaluated_candidates.append({
            **z,
            "is_legal": is_legal,
            "decision_status": decision_status,
            "reason": comp.get("notes") if not is_legal else ("High sea state chop" if not is_safe else "Optimal convergence and calm sea state"),
        })

        if decision_status == "SELECTED" and selected_zone is None:
            selected_zone = evaluated_candidates[-1]

    if selected_zone is None and evaluated_candidates:
        selected_zone = evaluated_candidates[0]

    return {
        "status": "success",
        "source": "mock",
        "operation": "select_safe_fishing_zone",
        "data": {
            "selected_zone": selected_zone,
            "evaluated_candidates": evaluated_candidates,
            "safety_override_applied": True,
            "summary": f"Selected safe zone {selected_zone.get('zone_id')} (Opportunity {selected_zone.get('opportunity_score')}, Risk {selected_zone.get('risk_score')}) over higher-opportunity restricted/rough zones.",
        },
    }


def mock_generate_recommendation(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    selected_zone = {}
    for dep_val in dependencies.values():
        data = dep_val.get("data", {}) if isinstance(dep_val, dict) else {}
        if "selected_zone" in data:
            selected_zone = data["selected_zone"]
            break

    zid = selected_zone.get("zone_id", "ZONE_B")
    dist = selected_zone.get("distance_nm", 8.2)
    bearing = selected_zone.get("bearing", "SSW")

    return {
        "status": "success",
        "source": "mock",
        "operation": "generate_recommendation",
        "data": {
            "headline": f"Recommended Fishing Ground: {zid} ({dist} NM {bearing})",
            "advisory": f"Proceed to {zid} ({dist} NM {bearing}). Favorable thermal fronts, high phytoplankton density, calm wave conditions (~1.1m).",
            "selected_zone": selected_zone,
        },
    }


def mock_calculate_distance(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "calculate_distance",
        "data": {
            "distance_nm": 8.2,
            "bearing": "SSW",
            "transit_time_hours": 1.2,
        },
    }


def mock_detect_algal_bloom_risk(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "detect_algal_bloom_risk",
        "data": {
            "hab_risk_level": "low",
            "algal_bloom_probability": 0.08,
            "water_health_index": 92.0,
        },
    }


def mock_analyze_historical_trends(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "analyze_historical_trends",
        "data": {
            "trend": "stable",
            "mean_anomaly_celsius": 0.12,
            "summary": "Observations within standard 5-year climatological baseline.",
        },
    }


def mock_evaluate_hazard(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "evaluate_hazard",
        "data": {
            "hazard_level": "low",
            "warning_issued": False,
            "advisory": "Standard coastal navigation safety measures apply.",
        },
    }


def mock_evaluate_route(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "evaluate_route",
        "data": {
            "route_safe": True,
            "hazard_waypoints": [],
            "clearance_nm": 5.0,
        },
    }


def mock_summarize_conditions(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "summarize_conditions",
        "data": {
            "summary_text": "Marine conditions are favorable for maritime operations.",
            "status": "nominal",
        },
    }


def mock_explain_recommendation(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "source": "mock",
        "operation": "explain_recommendation",
        "data": {
            "explanation": "Target coordinates validated against EEZ and marine protected zone polygons.",
        },
    }


# Global tool registry singleton
_DEFAULT_TOOL_REGISTRY = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Retrieve the global tool registry singleton."""
    return _DEFAULT_TOOL_REGISTRY


def reset_tool_registry() -> ToolRegistry:
    """Reset the global tool registry to initial defaults."""
    global _DEFAULT_TOOL_REGISTRY
    _DEFAULT_TOOL_REGISTRY = ToolRegistry()
    return _DEFAULT_TOOL_REGISTRY
