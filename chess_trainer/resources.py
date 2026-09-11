"""Curated learning resources per puzzle theme.

Every theme id (see `chess_trainer.themes`) gets at least Lichess's own
theme-filtered puzzle trainer, since that URL pattern (`lichess.org/training/{theme}`)
exists for every theme with no risk of a dead link. On top of that, the handful of
themes people most often plateau on get one hand-checked external explainer.

This curated set is intentionally small to start — every entry below was verified
by hand rather than guessed, and it's meant to grow one verified link at a time
in later commits rather than all at once.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Resource:
    title: str
    url: str
    source: str


CURATED_RESOURCES: dict[str, list[Resource]] = {
    "fork": [
        Resource("Fork (chess)", "https://en.wikipedia.org/wiki/Fork_(chess)", "Wikipedia"),
    ],
    "pin": [
        Resource("What is a pin in chess?", "https://www.chess.com/terms/pin-chess", "Chess.com Terms"),
    ],
    "skewer": [
        Resource("Skewer", "https://www.chess.com/terms/skewer-chess", "Chess.com Terms"),
    ],
    "discoveredAttack": [
        Resource(
            "Discovered Attack", "https://www.chess.com/terms/discovered-attack-chess", "Chess.com Terms"
        ),
    ],
    "deflection": [
        Resource("Deflection (chess)", "https://en.wikipedia.org/wiki/Deflection_(chess)", "Wikipedia"),
    ],
    "hangingPiece": [
        Resource("Hanging Piece", "https://www.chess.com/terms/hanging-piece-chess", "Chess.com Terms"),
    ],
    "zugzwang": [
        Resource("What is Zugzwang in Chess?", "https://www.chess.com/terms/zugzwang-chess", "Chess.com Terms"),
    ],
    "backRankMate": [
        Resource("Back Rank Mate", "https://www.chess.com/terms/back-rank-mate-chess", "Chess.com Terms"),
    ],
    "smotheredMate": [
        Resource("Smothered Mate", "https://www.chess.com/terms/smothered-mate", "Chess.com Terms"),
    ],
}


def get_resources(theme_id: str) -> list[Resource]:
    """Learning resources for a theme: the guaranteed Lichess trainer link, plus
    any hand-curated external lessons for that theme."""
    lichess_trainer = Resource(
        title=f"Practice {theme_id} puzzles on Lichess",
        url=f"https://lichess.org/training/{theme_id}",
        source="Lichess Puzzle Trainer",
    )
    return [lichess_trainer, *CURATED_RESOURCES.get(theme_id, [])]
