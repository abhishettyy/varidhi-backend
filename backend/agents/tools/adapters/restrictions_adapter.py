"""Maritime Boundary and Regulatory Restrictions Data Adapter."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.agents.tools.adapters.base import BaseDataAdapter


class SyntheticRestrictionsAdapter(BaseDataAdapter):
    """
    Synthetic realistic adapter for maritime legal boundaries, protected areas,
    and coastal geofencing restrictions.
    """

    @property
    def source_name(self) -> str:
        return "synthetic"

    @property
    def is_synthetic(self) -> bool:
        return True

    def check_restrictions(
        self,
        location: Dict[str, Any],
        vessel: Optional[Dict[str, Any]] = None,
        requested_time: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Check maritime boundaries, marine protected areas, and security buffers."""
        lat = location.get("latitude", 12.8681) or 12.8681
        lon = location.get("longitude", 74.8427) or 74.8427
        loc_name = location.get("name") or "Coastal Waters"

        now_utc = datetime.now(timezone.utc).isoformat()

        # Check candidate zones against realistic coastal boundaries
        zone_restrictions: Dict[str, Dict[str, Any]] = {
            "ZONE_A": {
                "restricted": False,
                "reason": None,
                "status": "CLEAR",
                "nearest_mpa_distance_nm": 42.0,
                "imbl_distance_nm": 185.0,
            },
            "ZONE_B": {
                "restricted": False,
                "reason": None,
                "status": "CLEAR",
                "nearest_mpa_distance_nm": 36.0,
                "imbl_distance_nm": 192.0,
            },
            "ZONE_C": {
                "restricted": False,
                "reason": None,
                "status": "CLEAR",
                "nearest_mpa_distance_nm": 28.0,
                "imbl_distance_nm": 204.0,
            },
        }

        # Known regional restricted areas (e.g. Netrani Island coral sanctuary ~60nm north of Mangalore)
        active_regulatory_areas: List[Dict[str, Any]] = [
            {
                "area_id": "MPA_NETRANI",
                "name": "Netrani Island Marine Sanctuary",
                "type": "MARINE_PROTECTED_AREA",
                "latitude": 14.018,
                "longitude": 74.329,
                "radius_nm": 3.0,
                "restriction_type": "NO_TRAWLING_NO_SPEARFISHING",
            },
            {
                "area_id": "PORT_SECURITY_NMPT",
                "name": "New Mangalore Port Ingress Channel",
                "type": "COMMERCIAL_SHIPPING_LANE",
                "latitude": 12.925,
                "longitude": 74.795,
                "radius_nm": 2.5,
                "restriction_type": "NO_STATIONARY_NETS",
            },
        ]

        return {
            "status": "success",
            "source": self.source_name,
            "operation": "check_restrictions",
            "observation_time": now_utc,
            "valid_time": None,
            "data": {
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "restricted": False,
                "general_advisory": "Karnataka coastal waters clear for traditional & motorized craft within territorial baseline.",
                "zone_restrictions": zone_restrictions,
                "active_regulatory_areas": active_regulatory_areas,
            },
            "quality": "official_gazette_synthetic",
            "metadata": {
                "jurisdiction": "State Fisheries Dept & Coast Guard (Karnataka)",
                "monsoon_ban_active": False,
            },
        }
