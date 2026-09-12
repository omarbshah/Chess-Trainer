import json

import pytest
import responses

from chess_trainer.errors import LichessAPIError, MissingApiTokenError
from chess_trainer.lichess_client import LichessClient
from chess_trainer.lichess_models import PuzzleActivityEntry, PuzzleDashboard, PuzzleDetail

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

# A real puzzle (id "fcEqc"), fetched from https://lichess.org/api/puzzle/fcEqc to make sure
# the model/client match Lichess's actual response shape rather than a guessed-at one.
PUZZLE_DETAIL_PAYLOAD = {
    "game": {
        "id": "ROdRPQtw",
        "perf": {"key": "blitz", "name": "Blitz"},
        "rated": True,
        "players": [
            {"name": "butchersboys2802", "id": "butchersboys2802", "color": "white", "rating": 1690},
            {"name": "tartinemariol", "id": "tartinemariol", "color": "black", "rating": 1773},
        ],
        "pgn": "Nf3 d5 b3 Nf6 Bb2 c5 e3 Nc6 d4 Bg4 h3 Bxf3 Qxf3 cxd4 exd4 e6 Nd2 Bd6 O-O-O O-O Kb1 "
        "Qc7 Bd3 Nb4 a3 Nxd3 Qxd3 Rac8 Rhe1 Qa5 b4 Qb6 Nb3 Ne4 Re2 Rc7 g3 Rfc8 c4 dxc4 Qxe4 "
        "cxb3 Rd3 a5 Rxb3 axb4 d5 Qc5 dxe6 Qc4 exf7+ Qxf7 Rf3 Qc4",
        "clock": "5+3",
    },
    "puzzle": {
        "id": "fcEqc",
        "rating": 1289,
        "plays": 671,
        "solution": ["e4e8", "c8e8", "e2e8", "d6f8", "f3f8"],
        "themes": ["middlegame", "long", "mateIn3", "sacrifice"],
        "fen": "2r3k1/1pr3pp/3b4/8/1pq1Q3/P4RPP/1B2RP2/1K6 w - - 1 1",
        "lastMove": "f7c4",
        "initialPly": 53,
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
def test_get_puzzle_parses_response() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/fcEqc",
        json=PUZZLE_DETAIL_PAYLOAD,
        status=200,
    )

    client = LichessClient(api_token="")  # public endpoint — no token needed
    detail = client.get_puzzle("fcEqc")

    assert isinstance(detail, PuzzleDetail)
    assert detail.puzzle.id == "fcEqc"
    assert detail.puzzle.initial_ply == 53
    assert detail.puzzle.last_move == "f7c4"
    assert detail.game.id == "ROdRPQtw"
    assert detail.game.perf.key == "blitz"


@responses.activate
def test_get_raises_on_http_error() -> None:
    responses.add(
        responses.GET,
        "https://lichess.org/api/puzzle/dashboard/30",
        json={"error": "nope"},
        status=401,
    )

    client = LichessClient(api_token="bad-token")

    with pytest.raises(LichessAPIError) as exc_info:
        client.get_puzzle_dashboard(30)

    assert exc_info.value.status_code == 401


def test_get_puzzle_dashboard_raises_without_a_token() -> None:
    client = LichessClient(api_token="")

    with pytest.raises(MissingApiTokenError):
        client.get_puzzle_dashboard(30)


def test_get_puzzle_activity_raises_without_a_token() -> None:
    client = LichessClient(api_token="")

    with pytest.raises(MissingApiTokenError):
        next(client.get_puzzle_activity())
