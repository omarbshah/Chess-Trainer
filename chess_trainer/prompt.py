"""Builds the text prompt sent to the AI provider router — the one place that turns a
validated `PuzzlePosition` (plus the tactical facts pulled from its starting position) into
words. Keeping this in one function makes what the AI is actually told fully inspectable and
testable, instead of scattered string-building wherever `/api/explain` needs it.
"""

from __future__ import annotations

import chess

from chess_trainer.puzzle_position import PuzzlePosition
from chess_trainer.tactics import Fork, HangingPiece, Pin, find_forks, find_hanging_pieces, find_pins


def build_explanation_prompt(
    position: PuzzlePosition, weak_theme_ids: list[str] | None = None
) -> str:
    """`weak_theme_ids` (optional) is the player's current weakest themes, e.g. from
    `rank_weak_themes` — if any of them tag this puzzle, the prompt asks the AI to prioritize
    explaining that specific tactical idea over the puzzle's other theme tags."""
    board = chess.Board(position.fen)
    facts = _describe_tactical_facts(
        find_hanging_pieces(board), find_pins(board), find_forks(board)
    )
    matched_weak_themes = [t for t in position.themes if weak_theme_ids and t in weak_theme_ids]

    lines = [
        "You are a chess coach explaining a Lichess puzzle to a player studying this exact "
        "weak theme.",
        "",
        f"Position (FEN): {position.fen}",
        f"{position.turn.capitalize()} to move.",
        f"Lichess puzzle rating: {position.rating}.",
        f"Themes: {', '.join(position.themes)}.",
        "",
        "The correct solution, move by move:",
    ]
    lines.extend(f"{i}. {move.san} ({move.by})" for i, move in enumerate(position.solution, start=1))

    if facts:
        lines.append("")
        lines.append(
            "Verified tactical facts about the starting position (use these — don't invent "
            "others):"
        )
        lines.extend(f"- {fact}" for fact in facts)

    if matched_weak_themes:
        lines.append("")
        lines.append(
            f"This puzzle is tagged with {', '.join(matched_weak_themes)} — one of this "
            "player's current weakest themes. Prioritize explaining that tactical idea clearly "
            "and connect it to why puzzles like this one tend to trip them up, over the "
            "puzzle's other theme tags."
        )

    lines.append("")
    lines.append(
        "Explain in plain language why this solution works, tying it to the facts above where "
        "relevant. Keep it to a short paragraph or two. Don't suggest any other moves — only "
        "explain the given solution."
    )

    return "\n".join(lines)


def _describe_tactical_facts(
    hanging: list[HangingPiece], pins: list[Pin], forks: list[Fork]
) -> list[str]:
    facts = []
    for piece in hanging:
        facts.append(
            f"The {piece.color} {piece.piece_type} on {piece.square} is hanging "
            f"(attacked by {', '.join(piece.attacked_by)}, undefended)."
        )
    for pin in pins:
        facts.append(
            f"The {pin.color} {pin.piece_type} on {pin.square} is pinned to its king on "
            f"{pin.king_square} by the piece on {pin.pinned_by}."
        )
    for fork in forks:
        facts.append(
            f"The {fork.color} {fork.piece_type} on {fork.square} forks "
            f"{', '.join(fork.forked_squares)}."
        )
    return facts
