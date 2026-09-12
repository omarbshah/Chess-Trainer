"""Builds the text prompt sent to the AI provider router — the one place that turns a
validated `PuzzlePosition` (plus the tactical facts pulled from its starting position) into
words. Keeping this in one function makes what the AI is actually told fully inspectable and
testable, instead of scattered string-building wherever `/api/explain` (the next commit)
happens to need it.
"""

from __future__ import annotations

import chess

from chess_trainer.puzzle_position import PuzzlePosition
from chess_trainer.tactics import Fork, HangingPiece, Pin, find_forks, find_hanging_pieces, find_pins


def build_explanation_prompt(position: PuzzlePosition) -> str:
    board = chess.Board(position.fen)
    facts = _describe_tactical_facts(
        find_hanging_pieces(board), find_pins(board), find_forks(board)
    )

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
