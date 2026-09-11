"""FastAPI app exposing the diagnosis engine over HTTP (for the extension popup, later)."""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from chess_trainer.api_schemas import ResourceResponse, ThemeResourcesResponse, WeakThemeResponse
from chess_trainer.errors import LichessAPIError
from chess_trainer.lichess_client import LichessClient
from chess_trainer.logging_config import configure_logging
from chess_trainer.resources import get_resources
from chess_trainer.themes import THEME_NAMES
from chess_trainer.weakness import rank_weak_themes

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Chess Trainer", version="0.1.0")


@app.exception_handler(LichessAPIError)
async def handle_lichess_api_error(request: Request, exc: LichessAPIError) -> JSONResponse:
    """Turn a failed Lichess call into a clean JSON error instead of a raw 500."""
    logger.warning("Lichess API error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=exc.status_code or 502, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/api/weaknesses", response_model=list[WeakThemeResponse])
def get_weaknesses(days: int = 30, top: int = 3, min_attempts: int = 5) -> list[WeakThemeResponse]:
    """Ranked weakest puzzle themes for this account, each with its resources attached."""
    with LichessClient() as client:
        dashboard = client.get_puzzle_dashboard(days)

    ranked = rank_weak_themes(dashboard, min_attempts=min_attempts)

    return [
        WeakThemeResponse(
            theme_id=theme.theme_id,
            display_name=theme.display_name,
            performance=theme.performance,
            attempts=theme.attempts,
            first_win_rate=theme.first_win_rate,
            resources=[ResourceResponse(**asdict(resource)) for resource in get_resources(theme.theme_id)],
        )
        for theme in ranked[:top]
    ]


@app.get("/api/resources/{theme_id}", response_model=ThemeResourcesResponse)
def get_theme_resources(theme_id: str) -> ThemeResourcesResponse:
    """Curated learning resources for a single theme id, looked up directly
    (no dashboard fetch) so the popup can show resources for any theme on demand."""
    return ThemeResourcesResponse(
        theme_id=theme_id,
        display_name=THEME_NAMES.get(theme_id, theme_id),
        resources=[ResourceResponse(**asdict(resource)) for resource in get_resources(theme_id)],
    )
