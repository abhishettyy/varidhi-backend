"""Interface and protocol definitions for P6 (Marine Analytics, Risk & Deterministic Calculations).

Ownership Boundary:
- P6 implements the scientific calculations, risk models, PFZ intersection algorithms, and GIS operations.
- P3 ONLY defines the invocation contract and consumes the results for orchestration and evidence assembly.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class P6AnalyticsProvider(Protocol):
    """Protocol that P6 analytics & calculation modules must satisfy."""

    async def calculate_sea_state_risk(
        self,
        weather_data: Dict[str, Any],
        vessel_type: Optional[str] = "small_motorized_boat"
    ) -> Dict[str, Any]:
        """Calculate deterministic vessel risk index and sea hazard score."""
        ...

    async def compute_pfz_zones(
        self,
        sst_data: Dict[str, Any],
        chlorophyll_data: Dict[str, Any],
        spatial_bounds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compute potential fishing zone clusters based on SST fronts and Chlorophyll-a."""
        ...

    async def detect_algal_bloom_risk(
        self,
        water_quality_data: Dict[str, Any],
        spatial_bounds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assess harmful algal bloom (HAB) probability and water health indices."""
        ...


class MockP6AnalyticsProvider:
    """
    Default mock analytics provider for testing orchestration pipelines
    before P6 connects deterministic calculation models.
    """

    async def calculate_sea_state_risk(
        self,
        weather_data: Dict[str, Any],
        vessel_type: Optional[str] = "small_motorized_boat"
    ) -> Dict[str, Any]:
        wave_height = weather_data.get("data", {}).get("wave_height_m", 1.2)
        wind_speed = weather_data.get("data", {}).get("wind_speed_knots", 10.0)

        # Basic deterministic mock calculation
        risk_score = min(100.0, (wave_height * 25.0) + (wind_speed * 1.5))
        severity = "safe_green" if risk_score < 40 else ("caution_yellow" if risk_score < 70 else "danger_red")

        return {
            "status": "success",
            "source": "P6_MOCK_RISK_ENGINE",
            "data": {
                "risk_score": round(risk_score, 1),
                "severity": severity,
                "vessel_safety": "Permitted for coastal vessels under 15m" if risk_score < 50 else "Advisory in effect",
                "max_recommended_distance_nm": 20 if risk_score < 40 else 8,
            }
        }

    async def compute_pfz_zones(
        self,
        sst_data: Dict[str, Any],
        chlorophyll_data: Dict[str, Any],
        spatial_bounds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "source": "P6_MOCK_PFZ_ENGINE",
            "data": {
                "pfz_detected": True,
                "confidence_score": 0.88,
                "recommended_hotspots": [
                    {
                        "zone_id": "PFZ-01",
                        "bearing": "SSW",
                        "distance_nm": 14.2,
                        "latitude": 9.85,
                        "longitude": 75.95,
                        "target_depth_m": 45,
                        "likely_species": ["Pelagic Tuna", "Mackerel", "Sardines"],
                        "chlorophyll_gradient": "High",
                        "sst_gradient_delta": "0.8°C thermal front"
                    }
                ],
                "summary": "1 primary PFZ hotspot identified along thermal gradient edge."
            }
        }

    async def detect_algal_bloom_risk(
        self,
        water_quality_data: Dict[str, Any],
        spatial_bounds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "source": "P6_MOCK_HAB_ENGINE",
            "data": {
                "hab_risk_level": "low",
                "algal_bloom_probability": 0.12,
                "water_health_index": 85.0,
                "anomalies_detected": []
            }
        }


# Global provider registry for dependency injection
_CURRENT_P6_PROVIDER: P6AnalyticsProvider = MockP6AnalyticsProvider()


def get_p6_provider() -> P6AnalyticsProvider:
    """Retrieve currently active P6 analytics provider."""
    return _CURRENT_P6_PROVIDER


def set_p6_provider(provider: P6AnalyticsProvider) -> None:
    """Allow P6 teammate to inject their live implementation."""
    global _CURRENT_P6_PROVIDER
    _CURRENT_P6_PROVIDER = provider
