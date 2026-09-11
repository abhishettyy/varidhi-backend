"""Canonical tool result schemas and status contracts for P4 tools and P6 analytics."""

from enum import Enum
from typing import Any, Dict, List, Optional
from backend.agents.schemas.base import BaseModel, Field


class ToolResultStatus(str, Enum):
    """Execution status for tool operations."""
    SUCCESS = "success"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    FAILED = "failed"
    BLOCKED = "blocked"


class ToolResult(BaseModel):
    """
    Canonical tool execution result envelope.
    Enforces standardized provenance, timing semantics, and payload structures.
    """
    status: str = Field(
        default=ToolResultStatus.SUCCESS.value,
        description="Execution status: success, partial, unavailable, error, failed, blocked"
    )
    source: str = Field(
        ...,
        description="Data origin / provider: e.g., 'Open-Meteo', 'INCOIS', 'Copernicus', 'synthetic'"
    )
    operation: str = Field(
        ...,
        description="Canonical operation name: e.g., 'get_pfz', 'get_sst', 'get_wind'"
    )
    observation_time: Optional[str] = Field(
        default=None,
        description="Timestamp of physical observation / satellite capture (ISO 8601 or None)"
    )
    valid_time: Optional[str] = Field(
        default=None,
        description="Forecast validity window / model run timestamp (ISO 8601 or None)"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Normalized domain data payload"
    )
    quality: Optional[str] = Field(
        default=None,
        description="Data quality indicator: 'high', 'moderate', 'degraded', 'simulated'"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional technical provenance, dataset identifiers, or coordinate bounds"
    )
    error: Optional[str] = Field(
        default=None,
        description="Human-readable error details if status is error/unavailable/failed"
    )
    partial: Optional[bool] = Field(
        default=None,
        description="True if tool operated on incomplete inputs"
    )
    missing_dependencies: Optional[List[str]] = Field(
        default=None,
        description="List of upstream dependencies that were missing"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToolResult to a clean dictionary matching the canonical contract."""
        res: Dict[str, Any] = {
            "status": self.status,
            "source": self.source,
            "operation": self.operation,
            "observation_time": self.observation_time,
            "valid_time": self.valid_time,
            "data": self.data,
            "quality": self.quality,
            "metadata": self.metadata,
        }
        if self.error is not None:
            res["error"] = self.error
        if self.partial is not None:
            res["partial"] = self.partial
        if self.missing_dependencies is not None:
            res["missing_dependencies"] = self.missing_dependencies
        return res
