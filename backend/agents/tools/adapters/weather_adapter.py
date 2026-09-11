"""Weather, Wave, Swell, Tide, and Currents Data Adapter."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.agents.tools.adapters.base import BaseDataAdapter


class SyntheticMarineWeatherAdapter(BaseDataAdapter):
    """
    Synthetic realistic adapter for coastal marine meteorology, waves, and ocean dynamics.
    Provides realistic physical oceanographic variables with honest 'synthetic' source tagging.
    """

    @property
    def source_name(self) -> str:
        return "synthetic"

    @property
    def is_synthetic(self) -> bool:
        return True

    def fetch_wind(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "forecast",
    ) -> Dict[str, Any]:
        """Fetch surface wind observations or forecast."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or f"({lat:.2f}, {lon:.2f})"

        # Generate realistic coastal wind for Karnataka/West Coast
        now_utc = datetime.now(timezone.utc).isoformat()

        # Moderate sea breeze profile
        speed_knots = 11.5
        gust_knots = 15.0
        direction_deg = 245.0  # WSW
        direction_cardinal = "WSW"

        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "get_wind",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "speed_knots": speed_knots,
                "speed_ms": round(speed_knots * 0.514444, 2),
                "gust_knots": gust_knots,
                "direction_deg": direction_deg,
                "direction_cardinal": direction_cardinal,
                "unit": "knots",
                "temporal_mode": temporal_mode,
            },
            "quality": "synthetic_model",
            "metadata": {
                "model": "SYNTHETIC_COASTAL_ATMOSPHERIC_v1",
                "resolution_km": 10.0,
            },
        }

    def fetch_wave(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "forecast",
    ) -> Dict[str, Any]:
        """Fetch significant wave height and sea state conditions without safety bias."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or f"({lat:.2f}, {lon:.2f})"

        now_utc = datetime.now(timezone.utc).isoformat()
        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        sig_wave_height_m = 1.35
        wave_period_sec = 7.5
        wave_direction_deg = 240.0

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "get_wave",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "significant_wave_height_m": sig_wave_height_m,
                "wave_period_sec": wave_period_sec,
                "wave_direction_deg": wave_direction_deg,
                "unit": "m",
                "temporal_mode": temporal_mode,
            },
            "quality": "synthetic_model",
            "metadata": {
                "model": "SYNTHETIC_WAVEWATCH_COASTAL_v1",
                "resolution_km": 5.0,
            },
        }

    def fetch_swell(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "forecast",
    ) -> Dict[str, Any]:
        """Fetch ocean swell parameters."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        now_utc = datetime.now(timezone.utc).isoformat()
        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "get_swell",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "latitude": lat,
                "longitude": lon,
                "swell_height_m": 0.9,
                "swell_period_sec": 10.2,
                "swell_direction_deg": 230.0,
                "unit": "m",
            },
            "quality": "synthetic_model",
            "metadata": {"model": "SYNTHETIC_SWELL_v1"},
        }

    def fetch_tide(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "forecast",
    ) -> Dict[str, Any]:
        """Fetch tidal timing and height predictions."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        now_utc = datetime.now(timezone.utc).isoformat()
        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "get_tide",
            "observation_time": None,
            "valid_time": valid_time,
            "data": {
                "latitude": lat,
                "longitude": lon,
                "tide_phase": "flood",
                "water_level_m": 1.15,
                "next_high_tide": "08:30 UTC",
                "next_low_tide": "14:45 UTC",
                "unit": "m",
            },
            "quality": "synthetic_harmonic",
            "metadata": {"method": "HARMONIC_CONSTITUENTS_SIMULATION"},
        }

    def fetch_currents(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "forecast",
    ) -> Dict[str, Any]:
        """Fetch surface current velocity and direction."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        now_utc = datetime.now(timezone.utc).isoformat()
        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "get_currents",
            "observation_time": None,
            "valid_time": valid_time,
            "data": {
                "latitude": lat,
                "longitude": lon,
                "current_speed_knots": 0.85,
                "current_direction_deg": 165.0,  # South-Southeast along coast
                "unit": "knots",
            },
            "quality": "synthetic_hydrodynamic",
            "metadata": {"model": "SYNTHETIC_COASTAL_CURRENTS_v1"},
        }
