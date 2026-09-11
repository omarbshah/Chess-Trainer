import pytest
from fastapi.testclient import TestClient

from chess_trainer.api import app
from chess_trainer.lichess_client import LichessClient
from chess_trainer.lichess_models import PuzzleDashboard

client = TestClient(app)


@pytest.fixture(autouse=True)
def _stub_dashboard(monkeypatch: pytest.MonkeyPatch) -> None:
    dashboard = PuzzleDashboard(
        days=30,
        **{"global": {"firstWins": 80, "nb": 100, "performance": 1700, "puzzleRatingAvg": 1700, "replayWins": 0}},
        themes={
            "fork": {
                "theme": "fork",
                "results": {
                    "firstWins": 5,
                    "nb": 20,
                    "performance": 1500,
                    "puzzleRatingAvg": 1550,
                    "replayWins": 1,
                },
            },
        },
    )
    monkeypatch.setattr(LichessClient, "get_puzzle_dashboard", lambda self, days: dashboard)


def test_get_weaknesses_returns_ranked_themes_with_resources() -> None:
    response = client.get("/api/weaknesses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["theme_id"] == "fork"
    assert body[0]["display_name"] == "Fork"
    assert any(resource["source"] == "Lichess Puzzle Trainer" for resource in body[0]["resources"])


def test_get_weaknesses_respects_min_attempts_query_param() -> None:
    response = client.get("/api/weaknesses", params={"min_attempts": 25})

    assert response.status_code == 200
    assert response.json() == []
