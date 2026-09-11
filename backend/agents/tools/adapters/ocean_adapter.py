"""Oceanographic Satellite & In-Situ Data Adapter for SST and Chlorophyll."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.agents.mocks.fixtures.mangalore_scenario import get_scenario_zones
from backend.agents.tools.adapters.base import BaseDataAdapter


class SyntheticOceanAdapter(BaseDataAdapter):
    """
    Synthetic realistic adapter for Sea Surface Temperature (SST) and Chlorophyll-a ocean color.
    Correctly models satellite observation semantics (latest available observation vs requested forecast).
    """

    @property
    def source_name(self) -> str:
        return "synthetic"

    @property
    def is_synthetic(self) -> bool:
        return True

    def fetch_sst(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "latest_available",
    ) -> Dict[str, Any]:
        """Fetch SST observations with thermal gradient breakdown aligned by candidate zone."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or f"({lat:.2f}, {lon:.2f})"

        now_utc = datetime.now(timezone.utc).isoformat()
        scenario_zones = get_scenario_zones(location)

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
            "source": self.source_name,
            "operation": "get_sst",
            "observation_time": now_utc,
            "valid_time": None,  # Satellite observations do not have forecast valid_time
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "value": mean_sst,
                "mean_sst_celsius": mean_sst,
                "unit": "degC",
                "gradient_celsius_per_km": 0.18,
                "has_thermal_front": True,
                "zone_gradients": zone_gradients,
                "zone_data": zone_data,
                "temporal_mode": temporal_mode,
            },
            "quality": "high",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "sensor": "SYNTHETIC_AVHRR_MODIS_COMPOSITE",
                "spatial_resolution_km": 1.0,
                "temporal_semantics": "latest_available",
            },
        }

    def fetch_chlorophyll(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "latest_available",
    ) -> Dict[str, Any]:
        """Fetch Chlorophyll-a concentration (biological productivity proxy) aligned by candidate zone."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or f"({lat:.2f}, {lon:.2f})"

        now_utc = datetime.now(timezone.utc).isoformat()
        scenario_zones = get_scenario_zones(location)

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
            "source": self.source_name,
            "operation": "get_chlorophyll",
            "observation_time": now_utc,
            "valid_time": None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "value": mean_chla,
                "chlorophyll_a_mg_m3": mean_chla,
                "unit": "mg/m3",
                "productivity_index": "high",
                "zone_chlorophyll": zone_chlorophyll,
                "zone_data": zone_data,
                "temporal_mode": temporal_mode,
            },
            "quality": "high",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "sensor": "SYNTHETIC_OCM_OLCI_COMPOSITE",
                "spatial_resolution_km": 1.0,
                "note": "Chlorophyll-a is an oceanic primary productivity proxy, not direct fish presence",
            },
        }
