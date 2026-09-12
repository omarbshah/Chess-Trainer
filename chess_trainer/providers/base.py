"""The provider adapter interface every AI backend (Gemini, DeepSeek, Groq, Ollama) implements,
so the router can treat them all the same way."""

from __future__ import annotations

from abc import ABC, abstractmethod

import requests


class ProviderError(Exception):
    """Raised by an adapter when it can't produce an explanation — a failed request, a
    timeout, a rate limit, whatever. The router treats this as "try the next provider"."""


class ProviderAdapter(ABC):
    """One AI provider capable of explaining a puzzle from a prompt."""

    name: str

    @abstractmethod
    def explain(self, prompt: str) -> str:
        """Return the explanation text for `prompt`, or raise `ProviderError`."""
        raise NotImplementedError


def raise_for_provider_response(provider_name: str, response: requests.Response) -> None:
    """Shared HTTP-status check for the REST-based adapters: raises `ProviderError` on a
    non-2xx response, with a distinct message for 429 specifically — worth telling apart from
    "something's actually broken" in logs, and from the circuit breaker's point of view it's
    still just another failure that should move on to the next provider."""
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        if response.status_code == 429:
            raise ProviderError(f"{provider_name} rate-limited this request (429)") from error
        raise ProviderError(f"{provider_name} request failed: {error}") from error
