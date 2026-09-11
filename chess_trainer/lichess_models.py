from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PuzzlePerformance(BaseModel):
    """Aggregate stats for puzzles solved in a given scope (overall, or one theme)."""

    model_config = ConfigDict(populate_by_name=True)

    first_wins: int = Field(alias="firstWins")
    nb: int
    performance: int
    puzzle_rating_avg: int = Field(alias="puzzleRatingAvg")
    replay_wins: int = Field(alias="replayWins")


class ThemeResult(BaseModel):
    """One theme's performance within a puzzle dashboard."""

    theme: str
    results: PuzzlePerformance


class PuzzleDashboard(BaseModel):
    """Response shape of `GET /api/puzzle/dashboard/{days}`."""

    model_config = ConfigDict(populate_by_name=True)

    days: int
    overall: PuzzlePerformance = Field(alias="global")
    themes: dict[str, ThemeResult]
