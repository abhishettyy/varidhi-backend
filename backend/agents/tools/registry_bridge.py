"""Registry bridge to register P4 tools into ToolRegistry and swap between mock and P4 implementations."""

from typing import Any, Callable, Dict

from backend.agents.mocks.tool_registry import (
    ToolRegistry,
    get_tool_registry,
    mock_check_geofence,
    mock_check_restrictions,
    mock_fetch_hazard_bulletins,
    mock_fetch_ocean_weather,
    mock_get_chlorophyll,
    mock_get_pfz,
    mock_get_sst,
    mock_get_swell,
    mock_get_tide,
    mock_get_wave,
    mock_get_wind,
)
from backend.agents.tools.data_tools import (
    p4_check_restrictions,
    p4_fetch_hazard_bulletins,
    p4_fetch_ocean_weather,
    p4_get_chlorophyll,
    p4_get_currents,
    p4_get_pfz,
    p4_get_sst,
    p4_get_swell,
    p4_get_tide,
    p4_get_wave,
    p4_get_wind,
)

P4_OPERATIONS_MAP: Dict[str, Callable] = {
    "get_pfz": p4_get_pfz,
    "fetch_pfz": p4_get_pfz,
    "get_sst": p4_get_sst,
    "fetch_sst_data": p4_get_sst,
    "get_chlorophyll": p4_get_chlorophyll,
    "fetch_chlorophyll_data": p4_get_chlorophyll,
    "get_wind": p4_get_wind,
    "get_wave": p4_get_wave,
    "get_swell": p4_get_swell,
    "get_tide": p4_get_tide,
    "get_currents": p4_get_currents,
    "check_restrictions": p4_check_restrictions,
    "check_geofence": p4_check_restrictions,
    "fetch_ocean_weather": p4_fetch_ocean_weather,
    "fetch_hazard_bulletins": p4_fetch_hazard_bulletins,
}

MOCK_OPERATIONS_MAP: Dict[str, Callable] = {
    "get_pfz": mock_get_pfz,
    "fetch_pfz": mock_get_pfz,
    "get_sst": mock_get_sst,
    "fetch_sst_data": mock_get_sst,
    "get_chlorophyll": mock_get_chlorophyll,
    "fetch_chlorophyll_data": mock_get_chlorophyll,
    "get_wind": mock_get_wind,
    "get_wave": mock_get_wave,
    "get_swell": mock_get_swell,
    "get_tide": mock_get_tide,
    "check_restrictions": mock_check_restrictions,
    "check_geofence": mock_check_geofence,
    "fetch_ocean_weather": mock_fetch_ocean_weather,
    "fetch_hazard_bulletins": mock_fetch_hazard_bulletins,
}


def register_p4_tools(registry: ToolRegistry) -> None:
    """Register all P4 tool implementations into the specified ToolRegistry."""
    for op_name, handler in P4_OPERATIONS_MAP.items():
        registry.register(op_name, handler)


def register_mock_tools(registry: ToolRegistry) -> None:
    """Register/restore mock tool implementations into the specified ToolRegistry."""
    for op_name, handler in MOCK_OPERATIONS_MAP.items():
        registry.register(op_name, handler)


def use_p4_tools() -> ToolRegistry:
    """Switch global ToolRegistry singleton to use P4 tools."""
    registry = get_tool_registry()
    register_p4_tools(registry)
    return registry


def use_mock_tools() -> ToolRegistry:
    """Switch global ToolRegistry singleton to use mock tools."""
    registry = get_tool_registry()
    register_mock_tools(registry)
    return registry
