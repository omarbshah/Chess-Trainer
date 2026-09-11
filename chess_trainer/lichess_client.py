from __future__ import annotations

import json
from collections.abc import Iterator

import requests

from chess_trainer.config import get_settings
from chess_trainer.lichess_models import PuzzleActivityEntry, PuzzleDashboard


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

    def get_puzzle_dashboard(self, days: int) -> PuzzleDashboard:
        """Fetch this account's puzzle performance dashboard for the last `days` days."""
        response = self.get(f"/api/puzzle/dashboard/{days}")
        return PuzzleDashboard.model_validate(response.json())

    def get_puzzle_activity(
        self,
        max_entries: int | None = None,
        before: int | None = None,
        since: int | None = None,
    ) -> Iterator[PuzzleActivityEntry]:
        """Stream this account's puzzle activity, most recent first.

        Lazily parses the newline-delimited JSON response so a long history doesn't
        have to be held in memory all at once. `before`/`since` are Lichess
        timestamps in milliseconds; `max_entries` caps how many entries are fetched.
        """
        params = {"max": max_entries, "before": before, "since": since}
        params = {key: value for key, value in params.items() if value is not None}

        response = self._session.get(
            f"{self.base_url}/api/puzzle/activity", params=params, stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue
            yield PuzzleActivityEntry.model_validate(json.loads(line))

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "LichessClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
