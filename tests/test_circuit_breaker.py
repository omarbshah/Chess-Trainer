import pytest

from chess_trainer.providers.circuit_breaker import CircuitBreaker


def _patch_clock(monkeypatch: pytest.MonkeyPatch, start: float = 1000.0) -> list[float]:
    """Returns a single-item mutable "clock" list; advance it via clock[0] += n."""
    clock = [start]
    monkeypatch.setattr("chess_trainer.providers.circuit_breaker.time.monotonic", lambda: clock[0])
    return clock


def test_allows_calls_while_closed() -> None:
    breaker = CircuitBreaker(failure_threshold=3)

    assert breaker.allow() is True
    assert breaker.is_open is False


def test_stays_closed_below_the_failure_threshold() -> None:
    breaker = CircuitBreaker(failure_threshold=3)

    breaker.record_failure()
    breaker.record_failure()

    assert breaker.allow() is True
    assert breaker.is_open is False


def test_opens_after_reaching_the_failure_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_clock(monkeypatch)
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)

    breaker.record_failure()
    breaker.record_failure()

    assert breaker.is_open is True
    assert breaker.allow() is False


def test_allows_a_probe_call_after_the_cooldown_elapses(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = _patch_clock(monkeypatch)
    breaker = CircuitBreaker(failure_threshold=1, cooldown_seconds=30.0)

    breaker.record_failure()
    assert breaker.allow() is False

    clock[0] += 30.0
    assert breaker.allow() is True


def test_success_closes_the_breaker_and_resets_the_failure_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_clock(monkeypatch)
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.is_open is True

    breaker.record_success()

    assert breaker.is_open is False
    assert breaker.allow() is True

    # Failure count reset too — one more failure shouldn't be enough to re-open it.
    breaker.record_failure()
    assert breaker.is_open is False
