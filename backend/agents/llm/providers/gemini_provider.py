"""Google Gemini REST API LLM Provider implementation using standard library urllib."""

import asyncio
import json
import re
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

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"


def _clean_json_text(raw_text: str) -> str:
    """Strips markdown formatting fences (```json ... ```) from model text."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class GeminiLLMProvider(LLMProvider):
    """
    Direct REST integration for Google Gemini models (e.g. gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash).
    Zero external pip dependencies required.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config or LLMConfig(provider="gemini", model="gemini-3.6-flash"))
        if not self.config.api_key:
            import os
            self.config.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("LLM_API_KEY")

    def _get_api_key(self) -> str:
        api_key = self.config.api_key
        if not api_key:
            import os
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("LLM_API_KEY")
        if not api_key:
            raise LLMAPIKeyMissingError("Gemini API key is missing. Set GEMINI_API_KEY or LLM_API_KEY environment variable.")
        return api_key

    def _build_request_payload(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Constructs the standard Gemini generateContent request JSON payload."""
        temp = temperature if temperature is not None else self.config.temperature

        generation_config: Dict[str, Any] = {
            "temperature": temp,
        }
        if self.config.max_tokens:
            generation_config["maxOutputTokens"] = self.config.max_tokens

        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        contents = [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": generation_config,
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        return payload

    def _prepare_payload(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Formats request payload according to Google Gemini REST specification."""
        return self._build_request_payload(prompt=prompt, system_prompt=system_prompt)

    def _execute_http_request(self, payload: Dict[str, Any], attempt_fallback: bool = True) -> Dict[str, Any]:
        """Synchronous HTTP execution with timeout and error handling."""
        api_key = self._get_api_key()
        url = self.config.api_base or GEMINI_API_ENDPOINT.format(
            model=self.config.model,
            api_key=api_key
        )

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                status_code = response.getcode()
                raw_body = response.read().decode("utf-8")
                if status_code != 200:
                    raise LLMError(f"Gemini API returned non-200 status code: {status_code} with body: {raw_body}")
                return json.loads(raw_body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            if e.code in (401, 403):
                raise LLMAPIKeyMissingError(f"Gemini API authentication failed (HTTP {e.code}): {err_body}")
            elif e.code == 429:
                raise LLMError(f"Gemini API rate limit exceeded (HTTP 429): {err_body}")
            elif e.code == 404 and attempt_fallback and self.config.model != "gemini-3.6-flash":
                # Automatically fallback from deprecated models (e.g. gemini-1.5-flash) to active gemini-3.6-flash
                self.config.model = "gemini-3.6-flash"
                return self._execute_http_request(payload, attempt_fallback=False)
            else:
                raise LLMError(f"Gemini API HTTP {e.code} error: {err_body}")
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower() or isinstance(e.reason, TimeoutError):
                raise LLMTimeoutError(f"Gemini request timed out after {self.config.timeout_seconds}s: {e}")
            raise LLMError(f"Gemini network connection error: {e}")
        except TimeoutError as e:
            raise LLMTimeoutError(f"Gemini request timed out after {self.config.timeout_seconds}s: {e}")
        except json.JSONDecodeError as e:
            raise LLMResponseParsingError(f"Gemini response could not be parsed as JSON: {e}")
        except Exception as e:
            raise LLMError(f"Unexpected error executing Gemini request: {e}")

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

        raise last_exception or LLMError("Gemini execution failed")

    def _extract_text_from_gemini_response(self, response_data: Dict[str, Any]) -> str:
        """Extracts candidate text from Gemini response structure."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            feedback = response_data.get("promptFeedback", {})
            raise LLMResponseParsingError(f"No candidates returned by Gemini. Feedback: {feedback}")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts or "text" not in parts[0]:
            raise LLMResponseParsingError("Candidate missing text part in Gemini response")

        return parts[0]["text"]

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate free-form text response from Gemini."""
        payload = self._build_request_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=False,
            temperature=temperature,
        )
        response_data = await self._execute_with_retries(payload)
        return self._extract_text_from_gemini_response(response_data)

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
        raw_text = self._extract_text_from_gemini_response(response_data)
        cleaned_json = _clean_json_text(raw_text)

        try:
            parsed_dict = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise LLMResponseParsingError(f"LLM output could not be parsed as JSON: {e}\nRaw output: {raw_text[:200]}")

        try:
            return schema_class.model_validate(parsed_dict)
        except Exception as e:
            raise LLMSchemaValidationError(f"Parsed JSON does not match schema {schema_class.__name__}: {e}")
