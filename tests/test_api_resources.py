from fastapi.testclient import TestClient

from chess_trainer.api import app

client = TestClient(app)


def test_known_theme_returns_display_name_and_curated_resources() -> None:
    response = client.get("/api/resources/fork")

    assert response.status_code == 200
    body = response.json()
    assert body["theme_id"] == "fork"
    assert body["display_name"] == "Fork"
    assert any(resource["source"] == "Lichess Puzzle Trainer" for resource in body["resources"])
    assert len(body["resources"]) > 1  # curated extra, on top of the guaranteed fallback


def test_unknown_theme_still_returns_the_guaranteed_fallback() -> None:
    response = client.get("/api/resources/madeUpTheme")

    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "madeUpTheme"
    assert len(body["resources"]) == 1
    assert body["resources"][0]["source"] == "Lichess Puzzle Trainer"
