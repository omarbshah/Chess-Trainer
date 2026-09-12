import pytest
import responses

from chess_trainer.providers.base import ProviderError
from chess_trainer.providers.gemini import GeminiAdapter

GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"


@responses.activate
def test_explain_returns_text_from_the_first_candidate() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"candidates": [{"content": {"parts": [{"text": "It's a fork on e4."}]}}]},
        status=200,
    )

    adapter = GeminiAdapter(api_key="test-key")
    result = adapter.explain("Explain this puzzle.")

    assert result == "It's a fork on e4."


@responses.activate
def test_explain_sends_the_prompt_and_api_key() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]},
        status=200,
    )

    adapter = GeminiAdapter(api_key="secret-key")
    adapter.explain("Explain this puzzle.")

    sent = responses.calls[0].request
    assert "key=secret-key" in sent.url
    assert '"Explain this puzzle."' in sent.body.decode()


@responses.activate
def test_explain_raises_provider_error_on_http_failure() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"error": "nope"},
        status=500,
    )

    adapter = GeminiAdapter(api_key="test-key")

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")


@responses.activate
def test_explain_raises_a_clear_error_on_rate_limit() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"error": "quota exceeded"},
        status=429,
    )

    adapter = GeminiAdapter(api_key="test-key")

    with pytest.raises(ProviderError, match="rate-limited"):
        adapter.explain("Explain this puzzle.")


@responses.activate
def test_explain_raises_provider_error_on_unexpected_response_shape() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"unexpected": "shape"},
        status=200,
    )

    adapter = GeminiAdapter(api_key="test-key")

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")
