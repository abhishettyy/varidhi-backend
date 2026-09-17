"""Base definitions, configurations, and exception hierarchy for LLM providers."""

import abc
import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from backend.agents.schemas.base import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMConfig(BaseModel):
    """Configuration options for an LLM provider."""
    provider: str = Field(default="mock", description="Provider type: 'mock', 'gemini', 'openai'.")
    model: str = Field(default="gemini-3.6-flash", description="Model identifier.")
    api_key: Optional[str] = Field(default=None, description="API credential key.")
    api_base: Optional[str] = Field(default=None, description="Custom API endpoint base URL.")
    temperature: float = Field(default=0.0, description="Sampling temperature (0.0 for deterministic).")
    max_tokens: Optional[int] = Field(default=2048, description="Maximum token limit for generation.")
    timeout_seconds: float = Field(default=10.0, description="HTTP request timeout in seconds.")
    max_retries: int = Field(default=1, description="Number of retry attempts on transient failure.")


class LLMError(Exception):
    """Base exception for all LLM-related errors."""
    pass


class LLMAPIKeyMissingError(LLMError):
    """Raised when an API key is required but missing."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM API call times out."""
    pass


class LLMResponseParsingError(LLMError):
    """Raised when the LLM response cannot be parsed as JSON or text."""
    pass


class LLMSchemaValidationError(LLMError):
    """Raised when the parsed LLM response does not match the target schema."""
    pass


def classify_llm_error(error: Optional[Exception]) -> str:
    """Classifies an LLM exception into a safe, non-secret categorical status string."""
    if error is None:
        return "UNKNOWN_ERROR"
    if isinstance(error, LLMAPIKeyMissingError):
        return "AUTHENTICATION_ERROR"
    if isinstance(error, LLMTimeoutError):
        return "API_TIMEOUT"
    if isinstance(error, LLMResponseParsingError):
        return "MALFORMED_OUTPUT"
    if isinstance(error, LLMSchemaValidationError):
        return "SCHEMA_VALIDATION_ERROR"

    err_str = str(error).lower()
    if "401" in err_str or "403" in err_str or "unauthorized" in err_str or "api key" in err_str:
        return "AUTHENTICATION_ERROR"
    if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
        return "RATE_LIMIT_EXCEEDED"
    if "timed out" in err_str or "timeout" in err_str:
        return "API_TIMEOUT"
    if "getaddrinfo" in err_str or "connection" in err_str or "unreachable" in err_str or "urlerror" in err_str or "network" in err_str:
        return "NETWORK_UNREACHABLE"
    if "json" in err_str or "decode" in err_str:
        return "MALFORMED_OUTPUT"
    if "validation" in err_str or "schema" in err_str:
        return "SCHEMA_VALIDATION_ERROR"

    return "UPSTREAM_API_ERROR"


class LLMProvider(abc.ABC):
    """Abstract interface for Large Language Model providers."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    @property
    def provider_name(self) -> str:
        return self.config.provider

    @property
    def model_name(self) -> str:
        return self.config.model

    @abc.abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate free-form text response from the model."""
        pass

    @abc.abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        """Generate a response constrained and validated against a schema."""
        pass
