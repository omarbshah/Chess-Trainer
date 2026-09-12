"""Tries each configured provider in order, skipping any whose circuit breaker is currently
open and falling back to the next on failure.

Works against the abstract `ProviderAdapter` interface and is fully testable with fakes — the
real adapters (Gemini/DeepSeek/Groq/Ollama, and optionally Claude) are assembled into an
instance of this by `providers/factory.py`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from chess_trainer.providers.base import ProviderAdapter, ProviderError
from chess_trainer.providers.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class AllProvidersFailedError(Exception):
    """Raised when every configured provider either refused (circuit open) or failed."""


class ProviderRouter:
    def __init__(
        self,
        adapters: list[ProviderAdapter],
        breaker_factory: Callable[[], CircuitBreaker] = CircuitBreaker,
    ) -> None:
        self._adapters = adapters
        self._breakers = {adapter.name: breaker_factory() for adapter in adapters}

    def explain(self, prompt: str) -> str:
        """Try each adapter in order; return the first successful explanation."""
        last_error: Exception | None = None

        for adapter in self._adapters:
            breaker = self._breakers[adapter.name]
            if not breaker.allow():
                logger.info("Skipping %s — circuit open", adapter.name)
                continue

            try:
                result = adapter.explain(prompt)
            except ProviderError as error:
                logger.warning("Provider %s failed: %s", adapter.name, error)
                breaker.record_failure()
                last_error = error
                continue

            breaker.record_success()
            return result

        raise AllProvidersFailedError(
            "Every provider failed or is temporarily unavailable"
        ) from last_error
