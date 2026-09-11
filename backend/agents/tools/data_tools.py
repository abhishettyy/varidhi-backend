"""P4 Data Tool implementations bridging canonical operations to data adapters."""

from typing import Any, Dict, Optional

from backend.agents.tools.adapters.ocean_adapter import SyntheticOceanAdapter
from backend.agents.tools.adapters.pfz_adapter import SyntheticPFZAdapter
from backend.agents.tools.adapters.restrictions_adapter import SyntheticRestrictionsAdapter
from backend.agents.tools.adapters.weather_adapter import SyntheticMarineWeatherAdapter

# Global active adapters (can be swapped with live API adapters when network/credentials are configured)
_WEATHER_ADAPTER = SyntheticMarineWeatherAdapter()
_OCEAN_ADAPTER = SyntheticOceanAdapter()
_PFZ_ADAPTER = SyntheticPFZAdapter()
_RESTRICTIONS_ADAPTER = SyntheticRestrictionsAdapter()


def set_weather_adapter(adapter: Any) -> None:
    global _WEATHER_ADAPTER
    _WEATHER_ADAPTER = adapter


def set_ocean_adapter(adapter: Any) -> None:
    global _OCEAN_ADAPTER
    _OCEAN_ADAPTER = adapter


def set_pfz_adapter(adapter: Any) -> None:
    global _PFZ_ADAPTER
    _PFZ_ADAPTER = adapter


def set_restrictions_adapter(adapter: Any) -> None:
    global _RESTRICTIONS_ADAPTER
    _RESTRICTIONS_ADAPTER = adapter


# =====================================================================
# Canonical P4 Tool Implementations
# =====================================================================

async def p4_get_pfz(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve Potential Fishing Zone (PFZ) candidate hotspots."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "latest_available")
    try:
        return _PFZ_ADAPTER.fetch_pfz(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _PFZ_ADAPTER.source_name,
            "operation": "get_pfz",
            "error": f"Failed to retrieve PFZ data: {str(e)}",
            "data": {},
        }


async def p4_get_sst(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve Sea Surface Temperature (SST) and thermal front gradient data."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "latest_available")
    try:
        return _OCEAN_ADAPTER.fetch_sst(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _OCEAN_ADAPTER.source_name,
            "operation": "get_sst",
            "error": f"Failed to retrieve SST data: {str(e)}",
            "data": {},
        }


async def p4_get_chlorophyll(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve Chlorophyll-a ocean color productivity data."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "latest_available")
    try:
        return _OCEAN_ADAPTER.fetch_chlorophyll(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _OCEAN_ADAPTER.source_name,
            "operation": "get_chlorophyll",
            "error": f"Failed to retrieve chlorophyll data: {str(e)}",
            "data": {},
        }


async def p4_get_wind(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve surface wind speed, direction, and gusts."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "forecast")
    try:
        return _WEATHER_ADAPTER.fetch_wind(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _WEATHER_ADAPTER.source_name,
            "operation": "get_wind",
            "error": f"Failed to retrieve wind data: {str(e)}",
            "data": {},
        }


async def p4_get_wave(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve significant wave height and sea conditions (raw observations, no safety bias)."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "forecast")
    try:
        return _WEATHER_ADAPTER.fetch_wave(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _WEATHER_ADAPTER.source_name,
            "operation": "get_wave",
            "error": f"Failed to retrieve wave data: {str(e)}",
            "data": {},
        }


async def p4_check_restrictions(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Check legal boundaries, marine protected areas, and security geofences."""
    location = parameters.get("location") or {}
    vessel = parameters.get("vessel")
    requested_time = parameters.get("requested_time")
    try:
        return _RESTRICTIONS_ADAPTER.check_restrictions(
            location=location,
            vessel=vessel,
            requested_time=requested_time,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _RESTRICTIONS_ADAPTER.source_name,
            "operation": "check_restrictions",
            "error": f"Failed to check maritime restrictions: {str(e)}",
            "data": {},
        }


async def p4_get_swell(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve ocean swell parameters."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "forecast")
    try:
        return _WEATHER_ADAPTER.fetch_swell(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _WEATHER_ADAPTER.source_name,
            "operation": "get_swell",
            "error": f"Failed to retrieve swell data: {str(e)}",
            "data": {},
        }


async def p4_get_tide(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve tidal phase and water level forecasts."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "forecast")
    try:
        return _WEATHER_ADAPTER.fetch_tide(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _WEATHER_ADAPTER.source_name,
            "operation": "get_tide",
            "error": f"Failed to retrieve tide data: {str(e)}",
            "data": {},
        }


async def p4_get_currents(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve ocean surface currents."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    temporal_mode = parameters.get("temporal_mode", "forecast")
    try:
        return _WEATHER_ADAPTER.fetch_currents(
            location=location,
            requested_time=requested_time,
            temporal_mode=temporal_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "source": _WEATHER_ADAPTER.source_name,
            "operation": "get_currents",
            "error": f"Failed to retrieve currents data: {str(e)}",
            "data": {},
        }


async def p4_fetch_ocean_weather(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Combined weather & sea state observation."""
    location = parameters.get("location") or {}
    requested_time = parameters.get("requested_time")
    wind_res = await p4_get_wind(parameters, dependencies)
    wave_res = await p4_get_wave(parameters, dependencies)

    wind_data = wind_res.get("data", {})
    wave_data = wave_res.get("data", {})

    return {
        "status": "success",
        "source": _WEATHER_ADAPTER.source_name,
        "operation": "fetch_ocean_weather",
        "observation_time": None,
        "valid_time": wind_res.get("valid_time"),
        "data": {
            "location": location.get("name", "Coastal Waters"),
            "wave_height_m": wave_data.get("significant_wave_height_m", 1.35),
            "swell_period_sec": wave_data.get("wave_period_sec", 7.5),
            "wind_speed_knots": wind_data.get("speed_knots", 11.5),
            "wind_direction": wind_data.get("direction_cardinal", "WSW"),
            "visibility_km": 10.0,
        },
        "quality": "synthetic_model",
    }


async def p4_fetch_hazard_bulletins(parameters: Dict[str, Any], dependencies: Dict[str, Any]) -> Dict[str, Any]:
    """Official weather and marine hazard bulletins."""
    location = parameters.get("location") or {}
    return {
        "status": "success",
        "source": "synthetic",
        "operation": "fetch_hazard_bulletins",
        "observation_time": None,
        "valid_time": None,
        "data": {
            "location": location.get("name", "Coastal Waters"),
            "active_alerts": [],
            "cyclone_warning": False,
            "high_swell_advisory": False,
        },
        "quality": "synthetic_bulletin",
    }
