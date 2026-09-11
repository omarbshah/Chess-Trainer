"""Turns a raw puzzle dashboard into a ranked list of weak themes."""

from __future__ import annotations

from dataclasses import dataclass

from chess_trainer.lichess_models import PuzzleDashboard, ThemeResult
from chess_trainer.themes import THEME_NAMES

# Themes with fewer attempts than this are dropped — too little data to say
# anything meaningful about them (a single lucky/unlucky puzzle shouldn't rank).
MIN_ATTEMPTS = 5


@dataclass(frozen=True)
class WeakTheme:
    """One theme's performance, enriched with a human-readable name and solve rate."""

    theme_id: str
    display_name: str
    performance: int
    attempts: int
    first_win_rate: float


def rank_weak_themes(
    dashboard: PuzzleDashboard, min_attempts: int = MIN_ATTEMPTS
) -> list[WeakTheme]:
    """Rank themes from weakest to strongest, by Lichess's own performance rating.

    Themes with fewer than `min_attempts` puzzles are dropped rather than ranked.
    """
    weak_themes = [
        _to_weak_theme(theme_id, result)
        for theme_id, result in dashboard.themes.items()
        if result.results.nb >= min_attempts
    ]
    return sorted(weak_themes, key=lambda theme: theme.performance)


def _to_weak_theme(theme_id: str, result: ThemeResult) -> WeakTheme:
    performance = result.results
    first_win_rate = performance.first_wins / performance.nb if performance.nb else 0.0
    return WeakTheme(
        theme_id=theme_id,
        display_name=THEME_NAMES.get(theme_id, result.theme),
        performance=performance.performance,
        attempts=performance.nb,
        first_win_rate=first_win_rate,
    )
