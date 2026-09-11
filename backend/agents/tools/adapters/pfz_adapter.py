"""Potential Fishing Zone (PFZ) Advisory Data Adapter."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.agents.mocks.fixtures.mangalore_scenario import get_scenario_zones
from backend.agents.tools.adapters.base import BaseDataAdapter


class SyntheticPFZAdapter(BaseDataAdapter):
    """
    Synthetic realistic adapter for Potential Fishing Zone (PFZ) advisory data.
    Simulates multi-zone candidates with explicit synthetic provenance tagging.
    """

    @property
    def source_name(self) -> str:
        return "synthetic"

    @property
    def is_synthetic(self) -> bool:
        return True

    def fetch_pfz(
        self,
        location: Dict[str, Any],
        requested_time: Optional[Dict[str, Any]] = None,
        temporal_mode: str = "latest_available",
    ) -> Dict[str, Any]:
        """Fetch PFZ candidate zones for the given region."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or "Mangalore Coast"

        now_utc = datetime.now(timezone.utc).isoformat()
        scenario_zones = get_scenario_zones(location)

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
            "source": self.source_name,
            "operation": "get_pfz",
            "observation_time": now_utc,
            "valid_time": None,
            "data": {
                "region": loc_name,
                "latitude": lat,
                "longitude": lon,
                "zones": zones,
                "confidence": 0.88,
                "temporal_mode": temporal_mode,
            },
            "quality": "high",
            "metadata": {
                "source_type": "synthetic",
                "scenario": "mangalore_demo",
                "fallback": False,
                "dataset": "SYNTHETIC_INCOIS_PFZ_MULTISOURCE",
            },
        }
