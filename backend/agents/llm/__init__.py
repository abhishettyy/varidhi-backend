"""LLM provider abstraction and integration for Varidhi Marine Intelligence."""

from backend.agents.llm.base import (
    LLMConfig,
    LLMError,
    LLMAPIKeyMissingError,
    LLMTimeoutError,
    LLMResponseParsingError,
    LLMSchemaValidationError,
    LLMProvider,
    classify_llm_error,
)
from backend.agents.llm.providers.fake_provider import FakeLLMProvider, MockLLMProvider
from backend.agents.llm.providers.gemini_provider import GeminiLLMProvider
from backend.agents.llm.providers.openai_provider import OpenAILLMProvider
from backend.agents.llm.factory import (
    get_llm_provider,
    get_llm_config_from_env,
    set_global_llm_provider,
    reset_global_llm_provider,
)

__all__ = [
    "LLMConfig",
    "LLMError",
    "LLMAPIKeyMissingError",
    "LLMTimeoutError",
    "LLMResponseParsingError",
    "LLMSchemaValidationError",
    "LLMProvider",
    "classify_llm_error",
    "FakeLLMProvider",
    "MockLLMProvider",
    "GeminiLLMProvider",
    "OpenAILLMProvider",
    "get_llm_provider",
    "get_llm_config_from_env",
    "set_global_llm_provider",
    "reset_global_llm_provider",
]
