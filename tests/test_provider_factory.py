from chess_trainer.config import Settings
from chess_trainer.providers.deepseek import DeepSeekAdapter
from chess_trainer.providers.factory import build_default_router
from chess_trainer.providers.gemini import GeminiAdapter
from chess_trainer.providers.groq import GroqAdapter
from chess_trainer.providers.ollama import OllamaAdapter

# Every provider-key field spelled out explicitly in each test, so this doesn't depend on
# (and isn't broken by) whatever happens to be in a real local .env file.


def test_includes_every_provider_when_all_keys_are_configured() -> None:
    settings = Settings(
        gemini_api_key="gemini-key",
        deepseek_api_key="deepseek-key",
        groq_api_key="groq-key",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )

    router = build_default_router(settings)

    adapter_types = [type(adapter) for adapter in router._adapters]
    assert adapter_types == [GeminiAdapter, DeepSeekAdapter, GroqAdapter, OllamaAdapter]


def test_skips_cloud_providers_with_no_api_key_configured() -> None:
    settings = Settings(
        gemini_api_key="",
        deepseek_api_key="",
        groq_api_key="groq-key",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )

    router = build_default_router(settings)

    adapter_types = [type(adapter) for adapter in router._adapters]
    assert adapter_types == [GroqAdapter, OllamaAdapter]


def test_ollama_is_always_included_even_with_no_cloud_keys() -> None:
    settings = Settings(
        gemini_api_key="",
        deepseek_api_key="",
        groq_api_key="",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )

    router = build_default_router(settings)

    adapter_types = [type(adapter) for adapter in router._adapters]
    assert adapter_types == [OllamaAdapter]


def test_each_adapter_gets_its_own_circuit_breaker() -> None:
    settings = Settings(
        gemini_api_key="gemini-key",
        deepseek_api_key="",
        groq_api_key="",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )

    router = build_default_router(settings)

    assert set(router._breakers.keys()) == {"gemini", "ollama"}
    assert router._breakers["gemini"] is not router._breakers["ollama"]
