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
        self.register("calculate_zone_ranking", mock_rank_zones)
        self.register("calculate_distance", mock_calculate_distance)
        self.register("detect_algal_bloom_risk", mock_detect_algal_bloom_risk)
        self.register("analyze_historical_trends", mock_analyze_historical_trends)

        # 3. Decision & Synthesis Operations
        self.register("select_safe_fishing_zone", mock_select_safe_fishing_zone)
        self.register("select_best_zone", mock_select_safe_fishing_zone)
        self.register("evaluate_hazard", mock_evaluate_hazard)
        self.register("evaluate_route", mock_evaluate_route)
        self.register("generate_recommendation", mock_generate_recommendation)
        self.register("summarize_conditions", mock_summarize_conditions)
        self.register("explain_recommendation", mock_explain_recommendation)


from backend.agents.mocks.fixtures.mangalore_scenario import get_scenario_zones


# =====================================================================
# Mock Handler Implementations (North Star Coherent Multi-Zone Model)
# =====================================================================

def mock_get_pfz(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    loc_name = loc.get("name") or "Mangalore Coast"
    lat = loc.get("latitude", 12.8681) or 12.8681
    lon = loc.get("longitude", 74.8427) or 74.8427
    scenario_zones = get_scenario_zones(loc)
    zones = [
        {
            "zone_id": z["zone_id"],
            "lat": z["latitude"],
            "lon": z["longitude"],
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "bearing": z["bearing"],
            "distance_nm": z["distance_nm"],
            "depth_m": z["depth_m"],
            "species": z["species"],
            "confidence": z["pfz_confidence"],
            "geometry": {
                "type": "Point",
                "coordinates": [z["longitude"], z["latitude"]],
            },
        }
        for z in scenario_zones
    ]
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_pfz",
        "data": {
            "region": loc_name,
            "latitude": lat,
            "longitude": lon,
            "zones": zones,
            "confidence": 0.88,
        },
    }


def mock_get_sst(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    scenario_zones = get_scenario_zones(loc)
    zone_gradients = {}
    zone_data = {}
    for z in scenario_zones:
        zid = z["zone_id"]
        zone_gradients[zid] = {
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "sst_celsius": z["sst_celsius"],
            "unit": "degC",
            "gradient": z["sst_gradient_delta"],
        }
        zone_data[zid] = {
            "zone_id": zid,
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "sst_celsius": z["sst_celsius"],
            "unit": "degC",
            "gradient_delta": z["sst_gradient_delta"],
        }
    mean_sst = round(sum(z["sst_celsius"] for z in scenario_zones) / len(scenario_zones), 2)
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_sst",
        "data": {
            "mean_sst_celsius": mean_sst,
            "value": mean_sst,
            "unit": "degC",
            "gradient_celsius_per_km": 0.18,
            "has_thermal_front": True,
            "zone_gradients": zone_gradients,
            "zone_data": zone_data,
        },
    }


def mock_get_chlorophyll(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    scenario_zones = get_scenario_zones(loc)
    zone_chlorophyll = {}
    zone_data = {}
    for z in scenario_zones:
        zid = z["zone_id"]
        zone_chlorophyll[zid] = {
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "chla_mg_m3": z["chlorophyll_a_mg_m3"],
            "unit": "mg/m3",
            "density": z["chlorophyll_density"],
        }
        zone_data[zid] = {
            "zone_id": zid,
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "chlorophyll_a_mg_m3": z["chlorophyll_a_mg_m3"],
            "unit": "mg/m3",
            "density": z["chlorophyll_density"],
        }
    mean_chla = round(sum(z["chlorophyll_a_mg_m3"] for z in scenario_zones) / len(scenario_zones), 2)
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_chlorophyll",
        "data": {
            "chlorophyll_a_mg_m3": mean_chla,
            "value": mean_chla,
            "unit": "mg/m3",
            "productivity_index": "high",
            "zone_chlorophyll": zone_chlorophyll,
            "zone_data": zone_data,
        },
    }


def mock_get_wind(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    scenario_zones = get_scenario_zones(loc)
    zone_wind = {}
    zone_data = {}
    for z in scenario_zones:
        zid = z["zone_id"]
        zone_wind[zid] = {
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "speed_knots": z["wind_speed_knots"],
            "gust_knots": z["wind_gust_knots"],
            "direction_deg": z["wind_direction_deg"],
            "direction_cardinal": z["wind_direction_cardinal"],
        }
        zone_data[zid] = {
            "zone_id": zid,
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "speed_knots": z["wind_speed_knots"],
            "gust_knots": z["wind_gust_knots"],
            "direction_deg": z["wind_direction_deg"],
            "unit": "knots",
        }
    mean_speed = round(sum(z["wind_speed_knots"] for z in scenario_zones) / len(scenario_zones), 1)
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_wind",
        "data": {
            "wind_speed_knots": mean_speed,
            "speed_knots": mean_speed,
            "gust_knots": round(mean_speed * 1.3, 1),
            "wind_gust_knots": round(mean_speed * 1.3, 1),
            "wind_direction": "WSW",
            "direction_deg": 245.0,
            "direction_cardinal": "WSW",
            "unit": "knots",
            "zone_wind": zone_wind,
            "zone_data": zone_data,
        },
    }


def mock_get_wave(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    scenario_zones = get_scenario_zones(loc)
    zone_wave = {}
    zone_data = {}
    for z in scenario_zones:
        zid = z["zone_id"]
        zone_wave[zid] = {
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "wave_height_m": z["wave_height_m"],
            "wave_period_sec": z["wave_period_sec"],
            "wave_direction_deg": z["wave_direction_deg"],
        }
        zone_data[zid] = {
            "zone_id": zid,
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "significant_wave_height_m": z["wave_height_m"],
            "wave_period_sec": z["wave_period_sec"],
            "wave_direction_deg": z["wave_direction_deg"],
            "unit": "m",
        }
    mean_wave = round(sum(z["wave_height_m"] for z in scenario_zones) / len(scenario_zones), 2)
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_wave",
        "data": {
            "wave_height_m": mean_wave,
            "significant_wave_height_m": mean_wave,
            "wave_period_sec": 7.0,
            "sea_state": "Slight to Moderate",
            "unit": "m",
            "zone_wave": zone_wave,
            "zone_data": zone_data,
        },
    }


def mock_get_swell(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    loc = parameters.get("location") or {}
    scenario_zones = get_scenario_zones(loc)
    zone_swell = {}
    for z in scenario_zones:
        zid = z["zone_id"]
        zone_swell[zid] = {
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "swell_height_m": z["swell_height_m"],
            "swell_period_sec": z["swell_period_sec"],
            "swell_direction_deg": z["swell_direction_deg"],
        }
    mean_swell = round(sum(z["swell_height_m"] for z in scenario_zones) / len(scenario_zones), 2)
    return {
        "status": "success",
        "source": "mock",
        "operation": "get_swell",
        "data": {
            "swell_height_m": mean_swell,
            "swell_period_sec": 8.5,
            "swell_direction": "SSW",
            "swell_direction_deg": 230.0,
            "unit": "m",
            "zone_swell": zone_swell,
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
    from backend.agents.analytics.regulatory import calculate_regulatory_compliance_tool_entrypoint
    return calculate_regulatory_compliance_tool_entrypoint(parameters, dependencies)


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
    from backend.agents.analytics.opportunity import calculate_opportunity_tool_entrypoint
    return calculate_opportunity_tool_entrypoint(parameters, dependencies)


def mock_calculate_marine_risk(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    from backend.agents.analytics.risk import calculate_marine_risk_tool_entrypoint
    return calculate_marine_risk_tool_entrypoint(parameters, dependencies)


def mock_rank_zones(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    from backend.agents.analytics.decision import calculate_zone_ranking_tool_entrypoint
    return calculate_zone_ranking_tool_entrypoint(parameters, dependencies)


def mock_select_safe_fishing_zone(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    from backend.agents.analytics.decision import select_safe_fishing_zone_tool_entrypoint
    return select_safe_fishing_zone_tool_entrypoint(parameters, dependencies)



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
