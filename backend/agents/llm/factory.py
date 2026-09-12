"""Factory for creating and configuring LLM provider instances."""

import os
from typing import Optional

from backend.agents.llm.base import LLMConfig, LLMProvider, LLMError
from backend.agents.llm.providers.fake_provider import FakeLLMProvider
from backend.agents.llm.providers.gemini_provider import GeminiLLMProvider
from backend.agents.llm.providers.openai_provider import OpenAILLMProvider

_GLOBAL_PROVIDER_OVERRIDE: Optional[LLMProvider] = None


def _load_dotenv_if_exists() -> None:
    """Lightweight stdlib loader for .env files in root or current directories."""
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass
            break


def set_global_llm_provider(provider: Optional[LLMProvider]) -> None:
    """Sets a global provider override (primarily used for unit testing)."""
    global _GLOBAL_PROVIDER_OVERRIDE
    _GLOBAL_PROVIDER_OVERRIDE = provider


def reset_global_llm_provider() -> None:
    """Clears any global provider override."""
    global _GLOBAL_PROVIDER_OVERRIDE
    _GLOBAL_PROVIDER_OVERRIDE = None


def get_llm_config_from_env() -> LLMConfig:
    """Reads LLM configuration options from environment variables and .env file."""
    _load_dotenv_if_exists()

    provider_env = os.environ.get("LLM_PROVIDER")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    llm_key = os.environ.get("LLM_API_KEY")

    if provider_env:
        provider = provider_env.lower().strip()
    elif gemini_key:
        provider = "gemini"
    elif openai_key:
        provider = "openai"
    else:
        provider = "mock"

    # Model defaults
    default_model = (
        "gemini-1.5-flash"
        if provider == "gemini"
        else ("gpt-4o-mini" if provider == "openai" else "mock-model")
    )
    model = os.environ.get("LLM_MODEL", default_model)

    # API keys
    api_key = llm_key
    if not api_key:
        if provider == "gemini":
            api_key = gemini_key
        elif provider == "openai":
            api_key = openai_key

    api_base = os.environ.get("LLM_API_BASE")

    # Temperature
    try:
        temp = float(os.environ.get("LLM_TEMPERATURE", "0.0"))
    except ValueError:
        temp = 0.0

    # Timeout
    try:
        timeout = float(os.environ.get("LLM_TIMEOUT_SECONDS", "10.0"))
    except ValueError:
        timeout = 10.0

    # Max retries
    try:
        retries = int(os.environ.get("LLM_MAX_RETRIES", "1"))
    except ValueError:
        retries = 1

    return LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        api_base=api_base,
        temperature=temp,
        timeout_seconds=timeout,
        max_retries=retries,
    )


def get_llm_provider(
    config: Optional[LLMConfig] = None,
    provider_type: Optional[str] = None,
) -> LLMProvider:
    """
    Factory function returning an instantiated LLMProvider.
    Respects global test override if set.
    """
    if _GLOBAL_PROVIDER_OVERRIDE is not None:
        return _GLOBAL_PROVIDER_OVERRIDE

    cfg = config or get_llm_config_from_env()
    selected_type = (provider_type or cfg.provider).lower().strip()

    if selected_type in ("mock", "fake", "testing", "synthetic"):
        return FakeLLMProvider(cfg)
    elif selected_type == "gemini":
        return GeminiLLMProvider(cfg)
    elif selected_type == "openai":
        return OpenAILLMProvider(cfg)
    else:
        raise LLMError(f"Unsupported LLM provider type: '{selected_type}'. Supported types: 'mock', 'gemini', 'openai'")
