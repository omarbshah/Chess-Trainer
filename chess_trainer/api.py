"""FastAPI app exposing the diagnosis engine over HTTP (for the extension popup, later)."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Chess Trainer", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
