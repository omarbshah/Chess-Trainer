"""FastAPI app exposing the diagnosis engine over HTTP (for the extension popup, later)."""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from chess_trainer.api_schemas import (
    ExplainResponse,
    ResourceResponse,
    ThemeResourcesResponse,
    WeakThemeResponse,
)
from chess_trainer.errors import LichessAPIError
from chess_trainer.lichess_client import LichessClient
from chess_trainer.logging_config import configure_logging
from chess_trainer.prompt import build_explanation_prompt
from chess_trainer.providers.factory import get_default_router
from chess_trainer.providers.router import AllProvidersFailedError
from chess_trainer.puzzle_position import build_puzzle_position
from chess_trainer.resources import get_resources
from chess_trainer.themes import THEME_NAMES
from chess_trainer.weakness import rank_weak_themes

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Chess Trainer", version="0.1.0")

# The popup fetches this API straight from its chrome-extension:// origin. Unpacked extension
# ids are derived from the local install path (not known ahead of time), so we match the whole
# scheme rather than a fixed origin — fine here since every endpoint is a read-only GET with no
# cookies/credentials involved.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(LichessAPIError)
async def handle_lichess_api_error(request: Request, exc: LichessAPIError) -> JSONResponse:
    """Turn a failed Lichess call into a clean JSON error instead of a raw 500."""
    logger.warning("Lichess API error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=exc.status_code or 502, content={"detail": str(exc)})


@app.exception_handler(AllProvidersFailedError)
async def handle_all_providers_failed(
    request: Request, exc: AllProvidersFailedError
) -> JSONResponse:
    """Every AI provider failed or was circuit-broken — a clean 502, not a raw 500."""
    logger.warning("Every AI provider failed on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=502,
        content={"detail": "No AI provider could explain this puzzle right now."},
    )


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


@app.get("/api/explain/{puzzle_id}", response_model=ExplainResponse)
def explain_puzzle(puzzle_id: str) -> ExplainResponse:
    """AI-narrated explanation of why a puzzle's solution works, grounded in its FEN/solution
    and the tactical facts `tactics.py` can verify about the starting position."""
    with LichessClient() as client:
        detail = client.get_puzzle(puzzle_id)

    position = build_puzzle_position(detail)
    prompt = build_explanation_prompt(position)
    explanation = get_default_router().explain(prompt)

    return ExplainResponse(
        puzzle_id=position.puzzle_id,
        rating=position.rating,
        themes=position.themes,
        explanation=explanation,
    )
