"""The provider adapter interface every AI backend (Gemini, DeepSeek, Groq, Ollama — the next
few commits) implements, so the router can treat them all the same way."""

from __future__ import annotations

from abc import ABC, abstractmethod


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
