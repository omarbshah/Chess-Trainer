import json

import pytest
import requests
import responses

from chess_trainer.lichess_client import LichessClient
from chess_trainer.lichess_models import PuzzleActivityEntry, PuzzleDashboard

DASHBOARD_PAYLOAD = {
    "days": 30,
    "global": {
        "firstWins": 40,
        "nb": 50,
        "performance": 1800,
        "puzzleRatingAvg": 1750,
        "replayWins": 5,
    },
    "themes": {
        "fork": {
            "theme": "fork",
            "results": {
                "firstWins": 10,
                "nb": 20,
                "performance": 1600,
                "puzzleRatingAvg": 1650,
                "replayWins": 2,
            },
        }
    },
}

ACTIVITY_ENTRY = {
    "date": 1_700_000_000_000,
    "win": True,
    "puzzle": {
        "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
        "id": "abcd1",
        "lastMove": "e2e4",
        "plays": 100,
        "rating": 1500,
        "solution": ["e7e5"],
        "themes": ["fork"],
    },
}


@responses.activate
def test_get_puzzle_dashboard_parses_response() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/dashboard/30",
        json=DASHBOARD_PAYLOAD,
        status=200,
    )

    client = LichessClient(api_token="test-token")
    dashboard = client.get_puzzle_dashboard(30)

    assert isinstance(dashboard, PuzzleDashboard)
    assert dashboard.overall.nb == 50
    assert dashboard.themes["fork"].results.performance == 1600


@responses.activate
def test_get_puzzle_dashboard_sends_auth_header() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/dashboard/7",
        json=DASHBOARD_PAYLOAD,
        status=200,
    )

    client = LichessClient(api_token="secret-token")
    client.get_puzzle_dashboard(7)

    sent_request = responses.calls[0].request
    assert sent_request.headers["Authorization"] == "Bearer secret-token"


@responses.activate
def test_get_puzzle_activity_streams_ndjson_entries() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/activity",
        body=json.dumps(ACTIVITY_ENTRY),
        status=200,
        content_type="application/x-ndjson",
    )

    client = LichessClient(api_token="test-token")
    entries = list(client.get_puzzle_activity(max_entries=1))

    assert len(entries) == 1
    assert isinstance(entries[0], PuzzleActivityEntry)
    assert entries[0].win is True
    assert entries[0].puzzle.id == "abcd1"


@responses.activate
def test_get_puzzle_activity_passes_query_params() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/activity",
        body="",
        status=200,
    )

    client = LichessClient(api_token="test-token")
    list(client.get_puzzle_activity(max_entries=5, before=123, since=100))

    sent_url = responses.calls[0].request.url
    assert "max=5" in sent_url
    assert "before=123" in sent_url
    assert "since=100" in sent_url


@responses.activate
def test_get_raises_on_http_error() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/dashboard/30",
        json={"error": "nope"},
        status=401,
    )

    client = LichessClient(api_token="bad-token")

    with pytest.raises(requests.HTTPError):
        client.get_puzzle_dashboard(30)
