"""Deterministic multi-zone marine scenario fixture for Mangalore / Karnataka coast.

Primary North-Star Scenario:
- Zone A: High Opportunity (SST front 0.9°C, Chl-a 2.8 mg/m³), High Risk (Waves 2.4m, Wind 22 kts), Legal (Clear)
- Zone B: Good Opportunity (SST front 0.6°C, Chl-a 2.3 mg/m³), Low Risk (Waves 1.1m, Wind 11 kts), Legal (Clear) -> IDEAL RECOMMENDATION
- Zone C: Highest Opportunity (SST front 1.1°C, Chl-a 3.2 mg/m³), Low Risk (Waves 1.0m, Wind 9.5 kts), Illegal (RESTRICTED) -> MUST BE REJECTED
"""

from typing import Any, Dict, List

MANGALORE_REFERENCE = {
    "name": "Mangalore",
    "latitude": 12.8681,
    "longitude": 74.8427,
    "harbor": "Mangalore Old Port",
    "region": "Karnataka Coast",
}

MANGALORE_ZONES: List[Dict[str, Any]] = [
    {
        "zone_id": "ZONE_A",
        "latitude": 12.95,
        "longitude": 74.80,
        "bearing": "WNW",
        "distance_nm": 14.5,
        "depth_m": 45,
        "species": ["Pelagic Tuna", "Kingfish"],
        "pfz_confidence": 0.88,
        "sst_celsius": 28.4,
        "sst_gradient_delta": "High thermal front (0.9°C delta)",
        "chlorophyll_a_mg_m3": 2.8,
        "chlorophyll_density": "High",
        "wind_speed_knots": 22.0,
        "wind_gust_knots": 28.0,
        "wind_direction_deg": 250.0,
        "wind_direction_cardinal": "WSW",
        "wave_height_m": 2.4,
        "wave_period_sec": 8.0,
        "wave_direction_deg": 245.0,
        "swell_height_m": 1.8,
        "swell_period_sec": 11.0,
        "swell_direction_deg": 240.0,
        "restricted": False,
        "restriction_reason": None,
        "regulatory_status": "CLEAR",
    },
    {
        "zone_id": "ZONE_B",
        "latitude": 12.90,
        "longitude": 74.95,
        "bearing": "SSW",
        "distance_nm": 8.2,
        "depth_m": 35,
        "species": ["Mackerel", "Sardines"],
        "pfz_confidence": 0.82,
        "sst_celsius": 28.7,
        "sst_gradient_delta": "Moderate thermal front (0.6°C delta)",
        "chlorophyll_a_mg_m3": 2.3,
        "chlorophyll_density": "Moderate-High",
        "wind_speed_knots": 11.0,
        "wind_gust_knots": 14.0,
        "wind_direction_deg": 240.0,
        "wind_direction_cardinal": "WSW",
        "wave_height_m": 1.1,
        "wave_period_sec": 6.5,
        "wave_direction_deg": 235.0,
        "swell_height_m": 0.7,
        "swell_period_sec": 7.5,
        "swell_direction_deg": 230.0,
        "restricted": False,
        "restriction_reason": None,
        "regulatory_status": "CLEAR",
    },
    {
        "zone_id": "ZONE_C",
        "latitude": 12.82,
        "longitude": 75.05,
        "bearing": "SSE",
        "distance_nm": 18.0,
        "depth_m": 60,
        "species": ["Yellowfin Tuna", "Barracuda"],
        "pfz_confidence": 0.94,
        "sst_celsius": 28.2,
        "sst_gradient_delta": "Strong thermal front (1.1°C delta)",
        "chlorophyll_a_mg_m3": 3.2,
        "chlorophyll_density": "Very High",
        "wind_speed_knots": 9.5,
        "wind_gust_knots": 12.0,
        "wind_direction_deg": 230.0,
        "wind_direction_cardinal": "SW",
        "wave_height_m": 1.0,
        "wave_period_sec": 6.0,
        "wave_direction_deg": 225.0,
        "swell_height_m": 0.6,
        "swell_period_sec": 7.0,
        "swell_direction_deg": 220.0,
        "restricted": True,
        "restriction_reason": "Marine Protected Sanctuary & Naval Exercise Corridor - RESTRICTED",
        "regulatory_status": "BLOCKED",
    },
]


def get_scenario_zones(location: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns deterministic multi-zone candidates.
    If location is Mangalore (or close to 12.86°N, 74.84°E), returns the canonical Mangalore fixture.
    Otherwise, shifts the reference coordinates deterministically to match requested location.
    """
    req_lat = location.get("latitude")
    req_lon = location.get("longitude")

    if req_lat is None or req_lon is None:
        return [dict(z) for z in MANGALORE_ZONES]

    lat_diff = abs(req_lat - MANGALORE_REFERENCE["latitude"])
    lon_diff = abs(req_lon - MANGALORE_REFERENCE["longitude"])

    # If within ~1 degree of Mangalore, return canonical Mangalore scenario
    if lat_diff < 1.0 and lon_diff < 1.0:
        return [dict(z) for z in MANGALORE_ZONES]

    # For other geographic locations, offset zones deterministically
    shifted_zones = []
    for z in MANGALORE_ZONES:
        sz = dict(z)
        delta_lat = z["latitude"] - MANGALORE_REFERENCE["latitude"]
        delta_lon = z["longitude"] - MANGALORE_REFERENCE["longitude"]
        sz["latitude"] = round(req_lat + delta_lat, 4)
        sz["longitude"] = round(req_lon + delta_lon, 4)
        shifted_zones.append(sz)
    return shifted_zones
