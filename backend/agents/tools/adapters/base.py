"""Base adapter abstraction for P4 external data sources."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDataAdapter(ABC):
    """Abstract base class for P4 data source adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the data provider (e.g. 'Open-Meteo', 'Copernicus', 'INCOIS', 'synthetic')."""
        pass

    @property
    @abstractmethod
    def is_synthetic(self) -> bool:
        """Whether this adapter provides synthetic / simulated data."""
        pass
