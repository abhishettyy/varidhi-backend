"""OpenAI REST API LLM Provider implementation using standard library urllib."""

import asyncio
import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Type, TypeVar
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

OPENAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def _clean_json_text(raw_text: str) -> str:
    """Strips markdown formatting fences from response text."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class OpenAILLMProvider(LLMProvider):
    """
    Direct REST integration for OpenAI compatible models (e.g. gpt-4o-mini, gpt-4o).
    Zero external pip dependencies required.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config or LLMConfig(provider="openai", model="gpt-4o-mini"))
        if not self.config.api_key:
            import os
            self.config.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")

    def _get_api_key(self) -> str:
        key = self.config.api_key
        if not key or not key.strip():
            raise LLMAPIKeyMissingError("OpenAI API key is missing. Set OPENAI_API_KEY or LLM_API_KEY environment variable.")
        return key.strip()

    def _build_request_payload(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Constructs the standard OpenAI chat completions JSON payload."""
        temp = temperature if temperature is not None else self.config.temperature

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temp,
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        return payload

    def _execute_http_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous HTTP execution with timeout and error handling."""
        api_key = self._get_api_key()
        url = self.config.api_base or OPENAI_API_ENDPOINT

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                status_code = response.getcode()
                raw_body = response.read().decode("utf-8")
                if status_code != 200:
                    raise LLMError(f"OpenAI API returned non-200 status code: {status_code} with body: {raw_body}")
                return json.loads(raw_body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            if e.code in (401, 403):
                raise LLMAPIKeyMissingError(f"OpenAI API authentication failed (HTTP {e.code}): {err_body}")
            elif e.code == 429:
                raise LLMError(f"OpenAI API rate limit exceeded (HTTP 429): {err_body}")
            else:
                raise LLMError(f"OpenAI API HTTP {e.code} error: {err_body}")
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower() or isinstance(e.reason, TimeoutError):
                raise LLMTimeoutError(f"OpenAI request timed out after {self.config.timeout_seconds}s: {e}")
            raise LLMError(f"OpenAI network connection error: {e}")
        except TimeoutError as e:
            raise LLMTimeoutError(f"OpenAI request timed out after {self.config.timeout_seconds}s: {e}")
        except json.JSONDecodeError as e:
            raise LLMResponseParsingError(f"OpenAI response could not be parsed as JSON: {e}")
        except Exception as e:
            raise LLMError(f"Unexpected error executing OpenAI request: {e}")

    async def _execute_with_retries(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes HTTP request off-thread with retry logic."""
        loop = asyncio.get_running_loop()
        retries = max(0, self.config.max_retries)
        last_exception = None

        for attempt in range(retries + 1):
            try:
                result = await loop.run_in_executor(None, self._execute_http_request, payload)
                return result
            except (LLMAPIKeyMissingError, LLMSchemaValidationError):
                raise
            except (LLMTimeoutError, LLMError) as e:
                last_exception = e
                if attempt < retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                else:
                    raise last_exception

        raise last_exception or LLMError("OpenAI execution failed")

    def _extract_text_from_openai_response(self, response_data: Dict[str, Any]) -> str:
        """Extracts content string from OpenAI response structure."""
        choices = response_data.get("choices", [])
        if not choices:
            raise LLMResponseParsingError("No choices returned in OpenAI response")

        message = choices[0].get("message", {})
        content = message.get("content")
        if content is None:
            raise LLMResponseParsingError("No content in message returned by OpenAI")

        return content

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate free-form text response from OpenAI."""
        payload = self._build_request_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=False,
            temperature=temperature,
        )
        response_data = await self._execute_with_retries(payload)
        return self._extract_text_from_openai_response(response_data)

    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured JSON response and validate against schema."""
        schema_json = json.dumps(schema_class.model_json_schema(), indent=2)
        enriched_system_prompt = (
            f"{system_prompt or ''}\n\n"
            f"You MUST respond ONLY with valid JSON matching the following JSON Schema:\n{schema_json}"
        ).strip()

        payload = self._build_request_payload(
            prompt=prompt,
            system_prompt=enriched_system_prompt,
            json_mode=True,
            temperature=temperature,
        )

        response_data = await self._execute_with_retries(payload)
        raw_text = self._extract_text_from_openai_response(response_data)
        cleaned_json = _clean_json_text(raw_text)

        try:
            parsed_dict = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise LLMResponseParsingError(f"LLM output could not be parsed as JSON: {e}\nRaw output: {raw_text[:200]}")

        try:
            return schema_class.model_validate(parsed_dict)
        except Exception as e:
            raise LLMSchemaValidationError(f"Parsed JSON does not match schema {schema_class.__name__}: {e}")
