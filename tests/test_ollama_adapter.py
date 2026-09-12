import pytest
import requests
import responses

from chess_trainer.providers.base import ProviderError
from chess_trainer.providers.ollama import OllamaAdapter

GENERATE_URL = "http://localhost:11434/api/generate"


@responses.activate
def test_explain_returns_the_response_field() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"response": "It's a fork on e4.", "done": True},
        status=200,
    )

    adapter = OllamaAdapter()
    result = adapter.explain("Explain this puzzle.")

    assert result == "It's a fork on e4."


@responses.activate
def test_explain_sends_the_model_and_prompt_with_streaming_disabled() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"response": "ok", "done": True},
        status=200,
    )

    adapter = OllamaAdapter(model="llama3.2")
    adapter.explain("Explain this puzzle.")

    sent_body = responses.calls[0].request.body.decode()
    assert '"model": "llama3.2"' in sent_body
    assert '"Explain this puzzle."' in sent_body
    assert '"stream": false' in sent_body


@responses.activate
def test_explain_raises_provider_error_when_ollama_isnt_running() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        body=requests.exceptions.ConnectionError("Connection refused"),
    )

    adapter = OllamaAdapter()

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")


@responses.activate
def test_explain_raises_provider_error_on_unexpected_response_shape() -> None:
    responses.add(
        responses.POST,
        GENERATE_URL,
        json={"unexpected": "shape"},
        status=200,
    )

    adapter = OllamaAdapter()

    with pytest.raises(ProviderError):
        adapter.explain("Explain this puzzle.")
