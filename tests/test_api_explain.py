import pytest
from fastapi.testclient import TestClient

import chess_trainer.api as api_module
from chess_trainer.api import app
from chess_trainer.errors import MissingApiTokenError
from chess_trainer.lichess_client import LichessClient
from chess_trainer.lichess_models import PuzzleDashboard, PuzzleDetail
from chess_trainer.providers.router import AllProvidersFailedError

client = TestClient(app)

# Same real puzzle (id "fcEqc") used elsewhere in the test suite.
PUZZLE_DETAIL_PAYLOAD = {
    "game": {
        "id": "ROdRPQtw",
        "perf": {"key": "blitz", "name": "Blitz"},
        "rated": True,
        "players": [
            {"name": "a", "id": "a", "color": "white", "rating": 1690},
            {"name": "b", "id": "b", "color": "black", "rating": 1773},
        ],
        "pgn": "Nf3 d5",
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


class _FakeRouter:
    def __init__(self, response: str | None = None) -> None:
        self.response = response
        self.received_prompt: str | None = None

    def explain(self, prompt: str) -> str:
        self.received_prompt = prompt
        if self.response is None:
            raise AllProvidersFailedError("every provider failed")
        return self.response


def _raise_missing_token(self: LichessClient, days: int) -> PuzzleDashboard:
    raise MissingApiTokenError()


@pytest.fixture(autouse=True)
def _stub_get_puzzle(monkeypatch: pytest.MonkeyPatch) -> None:
    detail = PuzzleDetail.model_validate(PUZZLE_DETAIL_PAYLOAD)
    monkeypatch.setattr(LichessClient, "get_puzzle", lambda self, puzzle_id: detail)


@pytest.fixture(autouse=True)
def _stub_get_puzzle_dashboard_to_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """`explain_puzzle` also fetches the dashboard for weak-theme prioritization — stub it to
    fail by default (as if no token were configured) so these tests never make a real network
    call. Tests that care about the prioritization behavior itself override this."""
    monkeypatch.setattr(LichessClient, "get_puzzle_dashboard", _raise_missing_token)


def test_explain_puzzle_returns_the_router_response(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_router = _FakeRouter(response="It's a fork on e4.")
    monkeypatch.setattr(api_module, "get_default_router", lambda: fake_router)

    response = client.get("/api/explain/fcEqc")

    assert response.status_code == 200
    body = response.json()
    assert body["puzzle_id"] == "fcEqc"
    assert body["rating"] == 1289
    assert body["themes"] == ["middlegame", "long", "mateIn3", "sacrifice"]
    assert body["explanation"] == "It's a fork on e4."


def test_explain_puzzle_sends_a_prompt_built_from_the_real_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_router = _FakeRouter(response="ok")
    monkeypatch.setattr(api_module, "get_default_router", lambda: fake_router)

    client.get("/api/explain/fcEqc")

    assert fake_router.received_prompt is not None
    assert "2r3k1/1pr3pp/3b4/8/1pq1Q3/P4RPP/1B2RP2/1K6 w - - 1 1" in fake_router.received_prompt
    assert "1. Qe8+ (solver)" in fake_router.received_prompt


def test_explain_puzzle_returns_502_when_every_provider_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(api_module, "get_default_router", lambda: _FakeRouter(response=None))

    response = client.get("/api/explain/fcEqc")

    assert response.status_code == 502


def test_explain_puzzle_succeeds_even_when_weak_theme_lookup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The autouse dashboard-failure stub above is exactly this scenario (no token
    # configured) — asserting it explicitly here so the graceful-fallback behavior has a
    # test of its own, not just an incidental side effect of every other test's setup.
    fake_router = _FakeRouter(response="ok")
    monkeypatch.setattr(api_module, "get_default_router", lambda: fake_router)

    response = client.get("/api/explain/fcEqc")

    assert response.status_code == 200
    assert "current weakest themes" not in fake_router.received_prompt


def test_explain_puzzle_prioritizes_a_theme_the_player_is_weak_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # fcEqc is tagged ["middlegame", "long", "mateIn3", "sacrifice"]; make "mateIn3" this
    # account's single weakest theme and confirm that reaches the actual prompt sent out.
    dashboard = PuzzleDashboard(
        days=30,
        **{"global": {"firstWins": 40, "nb": 50, "performance": 1800, "puzzleRatingAvg": 1750, "replayWins": 5}},
        themes={
            "mateIn3": {
                "theme": "mateIn3",
                "results": {
                    "firstWins": 2,
                    "nb": 10,
                    "performance": 1300,
                    "puzzleRatingAvg": 1350,
                    "replayWins": 0,
                },
            },
        },
    )
    monkeypatch.setattr(LichessClient, "get_puzzle_dashboard", lambda self, days: dashboard)

    fake_router = _FakeRouter(response="ok")
    monkeypatch.setattr(api_module, "get_default_router", lambda: fake_router)

    response = client.get("/api/explain/fcEqc")

    assert response.status_code == 200
    assert "This puzzle is tagged with mateIn3" in fake_router.received_prompt
