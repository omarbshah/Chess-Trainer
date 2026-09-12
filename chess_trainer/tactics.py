"""Groundwork for classical tactic detection over a `chess.Board` — pins, hanging pieces, and
forks. These are deliberately simple heuristics, not a full tactics engine: they're meant to
hand the AI explainer (a later phase) a few structured, verifiably-true facts about a position
to ground its narration in, not to replace an evaluation engine. Known limitations are called
out on each function.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess

PIECE_TYPE_NAMES = {
    chess.PAWN: "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK: "rook",
    chess.QUEEN: "queen",
    chess.KING: "king",
}


def _color_name(color: bool) -> str:
    return "white" if color == chess.WHITE else "black"


@dataclass
class HangingPiece:
    """A piece that's attacked at least once and defended not at all."""

    square: str
    piece_type: str
    color: str
    attacked_by: list[str]


@dataclass
class Pin:
    """A piece absolutely pinned to its own king along a rank, file, or diagonal."""

    square: str
    piece_type: str
    color: str
    king_square: str
    pinned_by: str


@dataclass
class Fork:
    """A piece simultaneously attacking two or more enemy pieces."""

    square: str
    piece_type: str
    color: str
    forked_squares: list[str]


def find_hanging_pieces(board: chess.Board) -> list[HangingPiece]:
    """Pieces attacked by the opponent with zero defenders of their own.

    Limitation: purely a defender head-count — it doesn't weigh attacker vs. defender value,
    so a piece "defended" by something that can't actually recapture profitably still counts
    as safe here.
    """
    hanging = []
    for square, piece in board.piece_map().items():
        attackers = board.attackers(not piece.color, square)
        if not attackers:
            continue
        defenders = board.attackers(piece.color, square)
        if defenders:
            continue
        hanging.append(
            HangingPiece(
                square=chess.square_name(square),
                piece_type=PIECE_TYPE_NAMES[piece.piece_type],
                color=_color_name(piece.color),
                attacked_by=[chess.square_name(s) for s in attackers],
            )
        )
    return hanging


def find_pins(board: chess.Board) -> list[Pin]:
    """Pieces absolutely pinned to their own king (relies on `chess.Board.is_pinned`/`pin`,
    which already handles the ray geometry correctly)."""
    pins = []
    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.KING:
            continue
        if not board.is_pinned(piece.color, square):
            continue

        king_square = board.king(piece.color)
        ray = board.pin(piece.color, square)
        pinner_square = next(
            (
                s
                for s in ray
                if s != square
                and (occupant := board.piece_at(s)) is not None
                and occupant.color != piece.color
            ),
            None,
        )

        pins.append(
            Pin(
                square=chess.square_name(square),
                piece_type=PIECE_TYPE_NAMES[piece.piece_type],
                color=_color_name(piece.color),
                king_square=chess.square_name(king_square),
                pinned_by=chess.square_name(pinner_square) if pinner_square is not None else "?",
            )
        )
    return pins


def find_forks(board: chess.Board) -> list[Fork]:
    """Pieces attacking two or more enemy pieces at once.

    Limitation: a plain attack count, with no filter for piece value or whether the forked
    pieces are themselves defended — so this will also flag "forks" that aren't actually
    winning anything. Good enough to point the AI explainer at candidate squares; not a
    substitute for real evaluation.
    """
    forks = []
    for square, piece in board.piece_map().items():
        targets = [
            target
            for target in board.attacks(square)
            if (occupant := board.piece_at(target)) is not None and occupant.color != piece.color
        ]
        if len(targets) < 2:
            continue
        forks.append(
            Fork(
                square=chess.square_name(square),
                piece_type=PIECE_TYPE_NAMES[piece.piece_type],
                color=_color_name(piece.color),
                forked_squares=[chess.square_name(t) for t in targets],
            )
        )
    return forks
