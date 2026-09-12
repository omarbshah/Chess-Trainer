"""Ollama adapter — the local fallback. Talks to a locally-running Ollama server
(https://ollama.com), so unlike the other three adapters there's no API key: whatever's
running on `base_url` is trusted as-is. Meant to be the last provider in the router's list —
it works with no internet and no account, at the cost of needing the model already pulled
locally and a machine that can actually run it."""

from __future__ import annotations

import logging

import requests

from chess_trainer.providers.base import ProviderAdapter, ProviderError, raise_for_provider_response

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama3.2"
DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaAdapter(ProviderAdapter):
    name = "ollama"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        # No api_key parameter — local server, nothing to authenticate. A longer default
        # timeout than the cloud adapters too: local inference (especially on CPU) is
        # often much slower than a hosted API.
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def explain(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        try:
            response = requests.post(
                url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            logger.warning("Ollama request failed: %s", error)
            raise ProviderError(f"Ollama request failed: {error}") from error

        raise_for_provider_response("Ollama", response)

        body = response.json()
        try:
            return body["response"]
        except KeyError as error:
            raise ProviderError(f"Unexpected Ollama response shape: {body}") from error
