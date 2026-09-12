from fastapi.testclient import TestClient

from chess_trainer.api import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_allows_cors_from_any_extension_origin() -> None:
    origin = "chrome-extension://abcdefghijklmnopabcdefghijklmnop"

    response = client.get("/health", headers={"Origin": origin})

    assert response.headers["access-control-allow-origin"] == origin


def test_rejects_cors_from_non_extension_origin() -> None:
    response = client.get("/health", headers={"Origin": "https://example.com"})

    assert "access-control-allow-origin" not in response.headers
