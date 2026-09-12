import pytest

from chess_trainer.providers.base import ProviderAdapter, ProviderError
from chess_trainer.providers.circuit_breaker import CircuitBreaker
from chess_trainer.providers.router import AllProvidersFailedError, ProviderRouter


class FakeAdapter(ProviderAdapter):
    """A test double: either always succeeds with a fixed response, or always raises."""

    def __init__(self, name: str, response: str | None = None) -> None:
        self.name = name
        self.response = response
        self.calls = 0

    def explain(self, prompt: str) -> str:
        self.calls += 1
        if self.response is None:
            raise ProviderError(f"{self.name} is down")
        return self.response


def test_returns_the_first_successful_providers_response() -> None:
    first = FakeAdapter("first", response="first's explanation")
    second = FakeAdapter("second", response="second's explanation")
    router = ProviderRouter([first, second])

    result = router.explain("prompt")

    assert result == "first's explanation"
    assert first.calls == 1
    assert second.calls == 0


def test_falls_back_to_the_next_provider_on_failure() -> None:
    first = FakeAdapter("first", response=None)
    second = FakeAdapter("second", response="second's explanation")
    router = ProviderRouter([first, second])

    result = router.explain("prompt")

    assert result == "second's explanation"
    assert first.calls == 1
    assert second.calls == 1


def test_raises_when_every_provider_fails() -> None:
    first = FakeAdapter("first", response=None)
    second = FakeAdapter("second", response=None)
    router = ProviderRouter([first, second])

    with pytest.raises(AllProvidersFailedError):
        router.explain("prompt")


def test_skips_a_provider_whose_circuit_is_open() -> None:
    always_open = CircuitBreaker(failure_threshold=1)
    always_open.record_failure()  # opens it; default 60s cooldown means allow() stays False

    first = FakeAdapter("first", response="would have worked")
    second = FakeAdapter("second", response="second's explanation")
    router = ProviderRouter([first, second], breaker_factory=lambda: CircuitBreaker())
    # Force the first provider's breaker into the open state after construction.
    router._breakers["first"] = always_open

    result = router.explain("prompt")

    assert result == "second's explanation"
    assert first.calls == 0
