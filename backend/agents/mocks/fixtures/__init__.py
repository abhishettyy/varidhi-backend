"""Fixtures package for deterministic mock marine scenarios."""

from .mangalore_scenario import (
    MANGALORE_REFERENCE,
    MANGALORE_ZONES,
    get_scenario_zones,
)

__all__ = [
    "MANGALORE_REFERENCE",
    "MANGALORE_ZONES",
    "get_scenario_zones",
]
