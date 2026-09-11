from __future__ import annotations

import json
import logging
from collections.abc import Iterator

import requests

from chess_trainer.config import get_settings
from chess_trainer.errors import LichessAPIError, MissingApiTokenError
from chess_trainer.lichess_models import PuzzleActivityEntry, PuzzleDashboard

logger = logging.getLogger(__name__)


class LichessClient:
    """Thin wrapper around a `requests.Session` for talking to the Lichess API."""

    def __init__(self, base_url: str | None = None, api_token: str | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.lichess_base_url).rstrip("/")
        self._session = requests.Session()

        # `api_token=None` (the default) means "use whatever's configured"; an
        # explicit `api_token=""` means "force no token" — used by tests so
        # behavior doesn't depend on whatever happens to be in the real .env.
        token = settings.lichess_api_token if api_token is None else api_token
        self._has_token = bool(token)
        if self._has_token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    def _request(self, path: str, **kwargs: object) -> requests.Response:
        """GET a path relative to the Lichess base URL, raising `LichessAPIError`
        (never a raw `requests` exception) on failure."""
        try:
            response = self._session.get(f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.warning("Lichess API request to %s failed: %s", path, error)
            raise LichessAPIError(
                f"Lichess API request to {path} failed with status {response.status_code}",
                status_code=response.status_code,
            ) from error
        except requests.RequestException as error:
            logger.warning("Could not reach the Lichess API at %s: %s", path, error)
            raise LichessAPIError(f"Could not reach the Lichess API at {path}: {error}") from error
        return response

    def get(self, path: str, **kwargs: object) -> requests.Response:
        """GET a path relative to the Lichess base URL, raising on non-2xx responses."""
        return self._request(path, **kwargs)

    def get_puzzle_dashboard(self, days: int) -> PuzzleDashboard:
        """Fetch this account's puzzle performance dashboard for the last `days` days."""
        self._require_token()
        response = self._request(f"/api/puzzle/dashboard/{days}")
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
        self._require_token()
        params = {"max": max_entries, "before": before, "since": since}
        params = {key: value for key, value in params.items() if value is not None}

        response = self._request("/api/puzzle/activity", params=params, stream=True)

        for line in response.iter_lines():
            if not line:
                continue
            yield PuzzleActivityEntry.model_validate(json.loads(line))

    def _require_token(self) -> None:
        """Dashboard/activity are account-scoped; fail with a clear message up
        front instead of letting Lichess return an opaque 401 later."""
        if not self._has_token:
            raise MissingApiTokenError()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "LichessClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
