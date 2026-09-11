"""Interfaces package for external subsystems (P4 Tools & P6 Analytics)."""

from .p4_tools import (
    P4ToolProvider,
    MockP4ToolProvider,
    get_p4_provider,
    set_p4_provider,
)
from .p6_analytics import (
    P6AnalyticsProvider,
    MockP6AnalyticsProvider,
    get_p6_provider,
    set_p6_provider,
)

__all__ = [
    "P4ToolProvider",
    "MockP4ToolProvider",
    "get_p4_provider",
    "set_p4_provider",
    "P6AnalyticsProvider",
    "MockP6AnalyticsProvider",
    "get_p6_provider",
    "set_p6_provider",
]
