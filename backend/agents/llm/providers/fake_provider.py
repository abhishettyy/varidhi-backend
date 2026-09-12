"""Fake/Mock LLM Provider for deterministic testing and offline execution."""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from backend.agents.schemas.base import BaseModel

from backend.agents.llm.base import (
    LLMConfig,
    LLMError,
    LLMAPIKeyMissingError,
    LLMTimeoutError,
    LLMResponseParsingError,
    LLMSchemaValidationError,
    LLMProvider,
)

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider(LLMProvider):
    """
    Mock LLM provider designed for unit testing, integration tests, and deterministic verification.
    Supports injecting error modes, canned structured outputs, canned text outputs, or dynamic handlers.
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        canned_text: Optional[str] = None,
        canned_structured: Optional[Dict[str, Any]] = None,
        error_mode: Optional[str] = None,
    ):
        super().__init__(config or LLMConfig(provider="mock", model="mock-model"))
        self.canned_text = canned_text
        self.canned_structured = canned_structured
        self.error_mode = error_mode
        self.call_history: List[Dict[str, Any]] = []

    def set_error_mode(self, error_mode: Optional[str]) -> None:
        """Dynamically configure simulated failure modes."""
        self.error_mode = error_mode

    def set_canned_text(self, text: Optional[str]) -> None:
        """Set fixed text generation response."""
        self.canned_text = text

    def set_canned_structured(self, data: Optional[Dict[str, Any]]) -> None:
        """Set fixed structured response dictionary."""
        self.canned_structured = data

    def _trigger_simulated_error(self) -> None:
        """Raises configured simulated errors."""
        if not self.error_mode:
            return
        if self.error_mode == "timeout":
            raise LLMTimeoutError("Simulated LLM call timeout after 10.0s")
        elif self.error_mode == "missing_key":
            raise LLMAPIKeyMissingError("Simulated missing API credential key")
        elif self.error_mode == "invalid_json":
            raise LLMResponseParsingError("Simulated malformed non-JSON output from LLM: '<<<Error: Parse Fail>>>'")
        elif self.error_mode == "schema_error":
            raise LLMSchemaValidationError("Simulated schema validation mismatch")
        elif self.error_mode == "api_error":
            raise LLMError("Simulated upstream HTTP 500 server error")
        else:
            raise LLMError(f"Simulated unknown error mode: {self.error_mode}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using canned output or deterministic rule synthesis."""
        self.call_history.append({
            "type": "text",
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "kwargs": kwargs,
        })

        self._trigger_simulated_error()

        if self.canned_text is not None:
            return self.canned_text

        # Default fallback response text
        return f"[MOCK LLM RESPONSE] Processed query context with model '{self.model_name}'."

    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured response validated against the requested Pydantic schema."""
        self.call_history.append({
            "type": "structured",
            "prompt": prompt,
            "schema_class": schema_class.__name__,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "kwargs": kwargs,
        })

        self._trigger_simulated_error()

        # If canned structured dict is provided
        if self.canned_structured is not None:
            try:
                return schema_class.model_validate(self.canned_structured)
            except Exception as e:
                raise LLMSchemaValidationError(f"Failed to validate canned data into {schema_class.__name__}: {e}")

        # Attempt intelligent synthesis based on prompt content
        lower_prompt = prompt.lower()
        if "mangalore" in lower_prompt:
            mock_data = {
                "intent": "FISHING_RECOMMENDATION",
                "confidence": 0.95,
                "location": {
                    "name": "Mangalore",
                    "latitude": 12.8681,
                    "longitude": 74.8427,
                    "harbor": "Mangalore Old Port",
                    "region": "Karnataka Coast",
                },
                "time_range": {
                    "raw": "tomorrow morning",
                    "relative_day": "tomorrow",
                    "period": "morning",
                    "forecast_horizon_hours": 36,
                    "is_historical": False,
                },
                "variables": ["SST", "CHLOROPHYLL", "PFZ", "WIND", "WAVE"],
                "vessel": None,
                "route": None,
                "constraints": {},
                "raw_query": prompt,
            }
            try:
                return schema_class.model_validate(mock_data)
            except Exception:
                pass

        # Try instantiating schema with default or dummy valid attributes
        try:
            return schema_class.model_validate({})
        except Exception:
            try:
                return schema_class()
            except Exception as e:
                raise LLMSchemaValidationError(f"Mock provider could not instantiate {schema_class.__name__}: {e}")


# Alias for naming symmetry
MockLLMProvider = FakeLLMProvider
