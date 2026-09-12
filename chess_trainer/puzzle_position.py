"""Turns a raw `PuzzleDetail` (Lichess's wire format) into a validated position with each
solution move replayed through `python-chess` and rendered as SAN — the structured shape later
commits (tactic feature extraction, the AI explainer's prompt template) will build on."""

from __future__ import annotations

from dataclasses import dataclass

import chess

from chess_trainer.lichess_models import PuzzleDetail


@dataclass
class SolutionMove:
    """One ply of the solution, alternating between the solver and their opponent (the side
    to move in the puzzle's FEN always moves first)."""

    uci: str
    san: str
    by: str  # "solver" or "opponent"


@dataclass
class PuzzlePosition:
    puzzle_id: str
    fen: str
    turn: str  # "white" or "black" — whoever is to move in `fen` is the solver
    rating: int
    themes: list[str]
    solution: list[SolutionMove]


def build_puzzle_position(detail: PuzzleDetail) -> PuzzlePosition:
    """Replay `detail.puzzle.solution` (UCI) from `detail.puzzle.fen` through a real board,
    both to catch a malformed FEN/solution early and to get SAN out for free."""
    board = chess.Board(detail.puzzle.fen)
    turn = "white" if board.turn == chess.WHITE else "black"

    solution = []
    for ply, uci in enumerate(detail.puzzle.solution):
        move = board.parse_uci(uci)
        san = board.san(move)
        board.push(move)
        solution.append(SolutionMove(uci=uci, san=san, by="solver" if ply % 2 == 0 else "opponent"))

    return PuzzlePosition(
        puzzle_id=detail.puzzle.id,
        fen=detail.puzzle.fen,
        turn=turn,
        rating=detail.puzzle.rating,
        themes=detail.puzzle.themes,
        solution=solution,
    )
