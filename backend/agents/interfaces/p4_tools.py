"""Interface and protocol definitions for P4 (Tools, MCP, and External APIs).

Ownership Boundary:
- P4 implements the real tool functions (connecting to INCOIS, NOAA, Copernicus, IMD, MCP servers).
- P3 ONLY defines the invocation contract and consumes the results.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class P4ToolProvider(Protocol):
    """Protocol that P4 tool integrations must satisfy."""

    async def fetch_ocean_weather(
        self,
        location: Dict[str, Any],
        forecast_horizon_hours: int = 24
    ) -> Dict[str, Any]:
        """Fetch wind speed, wave height, swell period, direction, and visibility."""
        ...

    async def fetch_sst_data(
        self,
        location: Dict[str, Any],
        timeframe: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fetch Sea Surface Temperature (SST) and thermal front data."""
        ...

    async def fetch_chlorophyll_data(
        self,
        location: Dict[str, Any],
        timeframe: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fetch ocean color / Chlorophyll-a concentration data."""
        ...

    async def fetch_hazard_bulletins(
        self,
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch official meteorological and ocean hazard bulletins/alerts."""
        ...


class MockP4ToolProvider:
    """
    Default mock tool provider for testing orchestration pipelines
    before P4 connects live external APIs / MCP servers.
    """

    async def fetch_ocean_weather(
        self,
        location: Dict[str, Any],
        forecast_horizon_hours: int = 24
    ) -> Dict[str, Any]:
        place = location.get("place_name") or "Coastal Waters"
        return {
            "status": "success",
            "source": "P4_MOCK_WEATHER_API",
            "data": {
                "location": place,
                "wave_height_m": 1.4,
                "swell_period_sec": 8.5,
                "wind_speed_knots": 12.0,
                "wind_direction": "WSW",
                "visibility_km": 10.0,
                "forecast_hours": forecast_horizon_hours,
            }
        }

    async def fetch_sst_data(
        self,
        location: Dict[str, Any],
        timeframe: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        place = location.get("place_name") or "Coastal Waters"
        return {
            "status": "success",
            "source": "P4_MOCK_SST_API",
            "data": {
                "location": place,
                "mean_sst_celsius": 28.6,
                "gradient_celsius_per_km": 0.15,
                "has_thermal_front": True,
            }
        }

    async def fetch_chlorophyll_data(
        self,
        location: Dict[str, Any],
        timeframe: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        place = location.get("place_name") or "Coastal Waters"
        return {
            "status": "success",
            "source": "P4_MOCK_CHLOROPHYLL_API",
            "data": {
                "location": place,
                "chlorophyll_a_mg_m3": 2.4,
                "productivity_index": "high",
            }
        }

    async def fetch_hazard_bulletins(
        self,
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        place = location.get("place_name") or "Coastal Waters"
        return {
            "status": "success",
            "source": "P4_MOCK_HAZARD_BULLETINS",
            "data": {
                "location": place,
                "active_alerts": [],
                "cyclone_warning": False,
                "high_swell_advisory": False,
            }
        }


# Global provider registry for dependency injection
_CURRENT_P4_PROVIDER: P4ToolProvider = MockP4ToolProvider()


def get_p4_provider() -> P4ToolProvider:
    """Retrieve currently active P4 tool provider."""
    return _CURRENT_P4_PROVIDER


def set_p4_provider(provider: P4ToolProvider) -> None:
    """Allow P4 teammate to inject their live implementation."""
    global _CURRENT_P4_PROVIDER
    _CURRENT_P4_PROVIDER = provider
