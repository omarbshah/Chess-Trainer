"""Custom exceptions for translating Lichess/API failures into clean responses,
instead of leaking raw `requests` exceptions and tracebacks to API consumers."""

from __future__ import annotations


class LichessAPIError(Exception):
    """Raised when a call to the Lichess API fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class MissingApiTokenError(LichessAPIError):
    """Raised when an endpoint needs a Lichess API token and none is configured."""

    def __init__(self) -> None:
        super().__init__(
            "No Lichess API token configured. Set LICHESS_API_TOKEN in your .env file.",
            status_code=401,
        )
