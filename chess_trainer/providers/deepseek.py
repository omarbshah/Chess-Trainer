"""DeepSeek adapter — an OpenAI-compatible chat completions endpoint, called directly with
`requests` (same style as the Gemini and Lichess clients, no vendor SDK dependency)."""

from __future__ import annotations

import logging

import requests

from chess_trainer.providers.base import ProviderAdapter, ProviderError, raise_for_provider_response

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "deepseek-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"


class DeepSeekAdapter(ProviderAdapter):
    name = "deepseek"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def explain(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            logger.warning("DeepSeek request failed: %s", error)
            raise ProviderError(f"DeepSeek request failed: {error}") from error

        raise_for_provider_response("DeepSeek", response)

        body = response.json()
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as error:
            raise ProviderError(f"Unexpected DeepSeek response shape: {body}") from error
