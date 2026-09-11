from __future__ import annotations

import requests

from chess_trainer.config import get_settings


class LichessClient:
    """Thin wrapper around a `requests.Session` for talking to the Lichess API."""

    def __init__(self, base_url: str | None = None, api_token: str | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.lichess_base_url).rstrip("/")
        self._session = requests.Session()

        token = api_token or settings.lichess_api_token
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, **kwargs: object) -> requests.Response:
        """GET a path relative to the Lichess base URL, raising on non-2xx responses."""
        response = self._session.get(f"{self.base_url}{path}", **kwargs)
        response.raise_for_status()
        return response

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "LichessClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
