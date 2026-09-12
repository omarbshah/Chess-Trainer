import pytest
import responses

from chess_trainer.providers.base import ProviderError
from chess_trainer.providers.deepseek import DeepSeekAdapter

CHAT_URL = "https://api.deepseek.com/chat/completions"


@responses.activate
def test_explain_returns_the_message_content() -> None:
    responses.add(
        responses.POST,
        CHAT_URL,
        json={"choices": [{"message": {"content": "It's a fork on e4."}}]},
        status=200,
    )

    adapter = DeepSeekAdapter(api_key="test-key")
    result = adapter.explain("Explain this puzzle.")

    assert result == "It's a fork on e4."


@responses.activate
def test_explain_sends_the_prompt_and_auth_header() -> None:
    responses.add(
        responses.POST,
        CHAT_URL,
        json={"choices": [{"message": {"content": "ok"}}]},
        status=200,
    )

    adapter = DeepSeekAdapter(api_key="secret-key")
    adapter.explain("Explain this puzzle.")

    sent = responses.calls[0].request
    assert sent.headers["Authorization"] == "Bearer secret-key"
    assert '"Explain this puzzle."' in sent.body.decode()


@responses.activate
def test_explain_raises_provider_error_on_http_failure() -> None:
    responses.add(
        responses.POST,
        CHAT_URL,
        json={"error": "nope"},
        status=500,
    )

    adapter = DeepSeekAdapter(api_key="test-key")

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")


@responses.activate
def test_explain_raises_provider_error_on_unexpected_response_shape() -> None:
    responses.add(
        responses.POST,
        CHAT_URL,
        json={"unexpected": "shape"},
        status=200,
    )

    adapter = DeepSeekAdapter(api_key="test-key")

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")
