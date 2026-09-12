"""Assembles the default provider router from `Settings` — the real Gemini/DeepSeek/Groq/
Ollama adapters, in fallback order, each behind its own circuit breaker. This is the "wiring"
commit: the router and the four adapters already existed, but nothing had connected them to
real configuration yet.
"""

from __future__ import annotations

from chess_trainer.config import Settings, get_settings
from chess_trainer.providers.base import ProviderAdapter
from chess_trainer.providers.circuit_breaker import CircuitBreaker
from chess_trainer.providers.deepseek import DeepSeekAdapter
from chess_trainer.providers.gemini import GeminiAdapter
from chess_trainer.providers.groq import GroqAdapter
from chess_trainer.providers.ollama import OllamaAdapter
from chess_trainer.providers.router import ProviderRouter

# Consecutive failures before a provider's breaker opens, and how long it then stays open.
# The same values for every provider for now — nothing yet suggests any of them need
# different tuning, and it's easy to split out per-provider later if that changes.
FAILURE_THRESHOLD = 3
COOLDOWN_SECONDS = 60.0


def _breaker_factory() -> CircuitBreaker:
    return CircuitBreaker(failure_threshold=FAILURE_THRESHOLD, cooldown_seconds=COOLDOWN_SECONDS)


def build_default_router(settings: Settings | None = None) -> ProviderRouter:
    """Cloud providers first (fastest, best quality), Ollama last (free, local, no API key —
    the fallback of last resort). A cloud provider with no API key configured is left out of
    the list entirely, rather than added and left to fail on every single call.
    """
    settings = settings or get_settings()
    adapters: list[ProviderAdapter] = []

    if settings.gemini_api_key:
        adapters.append(GeminiAdapter(api_key=settings.gemini_api_key, model=settings.gemini_model))
    if settings.deepseek_api_key:
        adapters.append(
            DeepSeekAdapter(api_key=settings.deepseek_api_key, model=settings.deepseek_model)
        )
    if settings.groq_api_key:
        adapters.append(GroqAdapter(api_key=settings.groq_api_key, model=settings.groq_model))

    # Always included — no key needed. If Ollama isn't installed or running, its calls just
    # fail and its breaker opens like any other provider's would.
    adapters.append(OllamaAdapter(base_url=settings.ollama_base_url, model=settings.ollama_model))

    return ProviderRouter(adapters, breaker_factory=_breaker_factory)
