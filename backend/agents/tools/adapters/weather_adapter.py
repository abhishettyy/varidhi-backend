"""Weather, Wave, Swell, Tide, and Currents Data Adapter."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.agents.mocks.fixtures.mangalore_scenario import get_scenario_zones
from backend.agents.tools.adapters.base import BaseDataAdapter


class SyntheticMarineWeatherAdapter(BaseDataAdapter):
    """
    Synthetic realistic adapter for coastal marine meteorology, waves, and ocean dynamics.
    Provides realistic physical oceanographic variables aligned by candidate zone.
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
        """Fetch surface wind observations or forecast aligned by candidate zone."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or f"({lat:.2f}, {lon:.2f})"

        now_utc = datetime.now(timezone.utc).isoformat()
        valid_time = (
            requested_time.get("iso_start") or requested_time.get("start") or now_utc
            if requested_time else now_utc
        )

        scenario_zones = get_scenario_zones(location)

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
            "source": self.source_name,
            "operation": "get_wind",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "speed_knots": mean_speed,
                "speed_ms": round(mean_speed * 0.514444, 2),
                "gust_knots": round(mean_speed * 1.3, 1),
                "direction_deg": 245.0,
                "direction_cardinal": "WSW",
                "unit": "knots",
                "zone_wind": zone_wind,
                "zone_data": zone_data,
                "temporal_mode": temporal_mode,
            },
            "quality": "synthetic_model",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
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

        scenario_zones = get_scenario_zones(location)

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
            "source": self.source_name,
            "operation": "get_wave",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "significant_wave_height_m": mean_wave,
                "wave_period_sec": 7.0,
                "wave_direction_deg": 240.0,
                "unit": "m",
                "zone_wave": zone_wave,
                "zone_data": zone_data,
                "temporal_mode": temporal_mode,
            },
            "quality": "synthetic_model",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
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

        scenario_zones = get_scenario_zones(location)
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
            "source": self.source_name,
            "operation": "get_swell",
            "observation_time": now_utc if temporal_mode == "latest_available" else None,
            "valid_time": valid_time if temporal_mode == "forecast" else None,
            "data": {
                "latitude": lat,
                "longitude": lon,
                "swell_height_m": mean_swell,
                "swell_period_sec": 8.5,
                "swell_direction_deg": 230.0,
                "unit": "m",
                "zone_swell": zone_swell,
            },
            "quality": "synthetic_model",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "model": "SYNTHETIC_SWELL_v1",
            },
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
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "method": "HARMONIC_CONSTITUENTS_SIMULATION",
            },
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
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "model": "SYNTHETIC_COASTAL_CURRENTS_v1",
            },
        }
