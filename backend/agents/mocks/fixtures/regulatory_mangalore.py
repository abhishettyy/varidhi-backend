"""Deterministic regulatory and marine spatial restrictions fixture for Mangalore / Karnataka coast.

IMPORTANT DISCLAIMER:
All spatial boundaries, Marine Protected Areas (MPAs), and naval coordinates in this fixture
are synthetic test artifacts designed for platform architecture verification and POC testing.
They DO NOT represent official government gazettes, statutory legal boundaries, or navigation clearances.
"""

from typing import Any, Dict, List, Optional
from backend.agents.analytics.schemas import Restriction, RestrictionType

# Canonical reference timestamp for deterministic temporal evaluation
MANGALORE_REGULATORY_REFERENCE_TIME = "2026-09-12T06:00:00Z"

# =====================================================================
# CANONICAL MOCK RESTRICTIONS CATALOG
# =====================================================================

SYNTHETIC_REGULATORY_RESTRICTIONS: List[Dict[str, Any]] = [
    # 1. Zone C Hard Block: Permanent Active Marine Protected Area
    {
        "restriction_id": "MPA_NETRAVATI_CORRIDOR_01",
        "restriction_type": RestrictionType.MPA.value,
        "name": "Netravati Marine Ecological Sanctuary & Port Approach",
        "status": "active",
        "zone_id": "ZONE_C",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [75.00, 12.75],
                [75.12, 12.75],
                [75.12, 12.88],
                [75.00, 12.88],
                [75.00, 12.75],
            ],  # Bounding box containing (12.82, 75.05)
        },
        "reason": "Sensitive estuarine coral/mangrove breeding sanctuary and naval security approach. Fishing strictly prohibited under State Gazette.",
        "source": "synthetic",
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": None,
        "severity": "HARD_BLOCK",
        "is_hard_block": True,
        "metadata": {
            "gazette_ref": "SYNTHETIC-KA-ENV-2024-09",
            "enforcement_authority": "Karnataka Coast Guard & Dept of Fisheries",
            "penalties": "Vessel impoundment and fine",
        },
    },

    # 2. Temporary Active Naval Live-Firing Exercise Zone
    {
        "restriction_id": "NAVAL_EXERCISE_KARWAR_S04",
        "restriction_type": RestrictionType.NAVAL_ZONE.value,
        "name": "Karwar Naval Base Offshore Live-Firing Sector Bravo",
        "status": "active",
        "zone_id": "ZONE_NAVAL_ACTIVE",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [74.30, 13.50],
                [74.60, 13.50],
                [74.60, 13.80],
                [74.30, 13.80],
                [74.30, 13.50],
            ],
        },
        "reason": "Active naval surface firing exercise in progress. Immediate exclusion zone.",
        "source": "synthetic",
        "valid_from": "2026-09-10T00:00:00Z",
        "valid_to": "2026-09-15T23:59:59Z",
        "severity": "HARD_BLOCK",
        "is_hard_block": True,
        "metadata": {
            "notam_ref": "SYNTHETIC-NAV-2026-0911",
            "vhf_channel": "CH-16",
        },
    },

    # 3. Expired Seasonal Monsoon Trawling Ban (Not active in September)
    {
        "restriction_id": "EXPIRED_MONSOON_BAN_2026",
        "restriction_type": RestrictionType.TEMPORARY_CLOSURE.value,
        "name": "Annual Karnataka Monsoon Fish Spawning Closure",
        "status": "expired",
        "zone_id": None,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [74.00, 12.50],
                [75.20, 12.50],
                [75.20, 14.50],
                [74.00, 14.50],
                [74.00, 12.50],
            ],
        },
        "reason": "Annual monsoon breeding ban (June 1 - July 31). Expired.",
        "source": "synthetic",
        "valid_from": "2026-06-01T00:00:00Z",
        "valid_to": "2026-07-31T23:59:59Z",
        "severity": "HARD_BLOCK",
        "is_hard_block": True,
        "metadata": {"status": "expired_clause"},
    },

    # 4. Future Scheduled Conservation Closure (Not yet active)
    {
        "restriction_id": "FUTURE_WINTER_CLOSURE_2026",
        "restriction_type": RestrictionType.TEMPORARY_CLOSURE.value,
        "name": "Scheduled Post-Monsoon Pelagic Nursery Rest Period",
        "status": "scheduled",
        "zone_id": None,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [74.70, 12.80],
                [75.00, 12.80],
                [75.00, 13.10],
                [74.70, 13.10],
                [74.70, 12.80],
            ],
        },
        "reason": "Winter juvenile replenishment nursery window (Nov 1 - Dec 31). Inactive.",
        "source": "synthetic",
        "valid_from": "2026-11-01T00:00:00Z",
        "valid_to": "2026-12-31T23:59:59Z",
        "severity": "HARD_BLOCK",
        "is_hard_block": True,
        "metadata": {"status": "future_clause"},
    },

    # 5. Commercial Shipping Lane (Caution / Warning only — NOT a hard block)
    {
        "restriction_id": "SHIPPING_LANE_NMPT_TSS",
        "restriction_type": RestrictionType.SHIPPING_LANE.value,
        "name": "New Mangalore Port Traffic Separation Scheme (TSS)",
        "status": "active",
        "zone_id": "ZONE_SHIPPING_CAUTION",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [74.75, 12.90],
                [74.82, 12.90],
                [74.82, 12.98],
                [74.75, 12.98],
                [74.75, 12.90],
            ],
        },
        "reason": "High-density international commercial vessel traffic corridor. Maintain active VHF CH-16 watch. No stationary drift nets.",
        "source": "synthetic",
        "valid_from": "2020-01-01T00:00:00Z",
        "valid_to": None,
        "severity": "WARNING",
        "is_hard_block": False,
        "metadata": {
            "advisory_type": "NAVIGATIONAL_CAUTION",
            "recommended_action": "Cross at right angles; maintain continuous lookout",
        },
    },

    # 6. International Maritime Boundary Line (IMBL) Exclusion
    {
        "restriction_id": "MARITIME_BOUNDARY_HIGH_SEAS",
        "restriction_type": RestrictionType.MARITIME_BOUNDARY.value,
        "name": "Exclusive Economic Zone Outer Perimeter Boundary",
        "status": "active",
        "zone_id": "ZONE_OUTSIDE_EEZ",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [70.00, 10.00],
                [72.00, 10.00],
                [72.00, 14.00],
                [70.00, 14.00],
                [70.00, 10.00],
            ],
        },
        "reason": "International waters beyond national fisheries jurisdiction. Requires distant-water permit.",
        "source": "synthetic",
        "valid_from": "2000-01-01T00:00:00Z",
        "valid_to": None,
        "severity": "HARD_BLOCK",
        "is_hard_block": True,
        "metadata": {"jurisdiction": "International High Seas"},
    },
]


def get_synthetic_restrictions() -> List[Restriction]:
    """Returns typed synthetic restrictions list."""
    return [Restriction(**dict(r)) for r in SYNTHETIC_REGULATORY_RESTRICTIONS]
