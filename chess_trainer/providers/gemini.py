"""Gemini adapter — talks to Google's `generateContent` REST API directly with `requests`,
the same way `LichessClient` talks to Lichess, rather than pulling in Google's SDK."""

from __future__ import annotations

import logging

import requests

from chess_trainer.providers.base import ProviderAdapter, ProviderError

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiAdapter(ProviderAdapter):
    name = "gemini"

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
        url = f"{self.base_url}/models/{self.model}:generateContent"
        try:
            response = requests.post(
                url,
                params={"key": self.api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            logger.warning("Gemini request failed: %s", error)
            raise ProviderError(f"Gemini request failed: {error}") from error

        body = response.json()
        try:
            return body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as error:
            raise ProviderError(f"Unexpected Gemini response shape: {body}") from error
