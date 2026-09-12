"""A minimal circuit breaker: after enough consecutive failures from a provider, stop trying
it for a cooldown period instead of paying for (and waiting on) a call likely to fail again.

Closed (normal) -> `failure_threshold` consecutive failures -> Open (blocks calls) -> after
`cooldown_seconds`, the next call is let through as a half-open probe -> success closes it
again, failure re-opens it.
"""

from __future__ import annotations

import time


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._consecutive_failures = 0
        self._opened_at: float | None = None

    def allow(self) -> bool:
        """Whether a call should be attempted right now."""
        if self._opened_at is None:
            return True
        return (time.monotonic() - self._opened_at) >= self.cooldown_seconds

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._opened_at = time.monotonic()

    @property
    def is_open(self) -> bool:
        """True while actively blocking calls (open and still within its cooldown)."""
        return self._opened_at is not None and not self.allow()
