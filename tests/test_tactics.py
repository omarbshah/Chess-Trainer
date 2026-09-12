import chess

from chess_trainer.tactics import find_forks, find_hanging_pieces, find_pins


def _empty_board_with_kings() -> chess.Board:
    board = chess.Board.empty()
    board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    return board


def test_find_hanging_pieces_flags_undefended_attacked_piece() -> None:
    board = _empty_board_with_kings()
    board.set_piece_at(chess.E4, chess.Piece(chess.KNIGHT, chess.WHITE))
    board.set_piece_at(chess.D5, chess.Piece(chess.PAWN, chess.BLACK))

    hanging = find_hanging_pieces(board)

    assert len(hanging) == 1
    assert hanging[0].square == "e4"
    assert hanging[0].piece_type == "knight"
    assert hanging[0].color == "white"
    assert hanging[0].attacked_by == ["d5"]


def test_find_hanging_pieces_ignores_defended_piece() -> None:
    board = _empty_board_with_kings()
    board.set_piece_at(chess.E4, chess.Piece(chess.KNIGHT, chess.WHITE))
    board.set_piece_at(chess.D5, chess.Piece(chess.PAWN, chess.BLACK))
    board.set_piece_at(chess.D3, chess.Piece(chess.PAWN, chess.WHITE))  # defends e4

    hanging = find_hanging_pieces(board)

    assert hanging == []


def test_find_pins_detects_absolute_pin_and_its_pinner() -> None:
    board = chess.Board.empty()
    board.set_piece_at(chess.E1, chess.Piece(chess.ROOK, chess.WHITE))
    board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.BLACK))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))

    pins = find_pins(board)

    assert len(pins) == 1
    assert pins[0].square == "e5"
    assert pins[0].piece_type == "pawn"
    assert pins[0].color == "black"
    assert pins[0].king_square == "e8"
    assert pins[0].pinned_by == "e1"


def test_find_pins_ignores_unpinned_piece() -> None:
    board = _empty_board_with_kings()
    board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.BLACK))

    assert find_pins(board) == []


def test_find_forks_detects_knight_fork_of_king_and_rook() -> None:
    board = chess.Board.empty()
    board.set_piece_at(chess.D6, chess.Piece(chess.KNIGHT, chess.WHITE))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.B7, chess.Piece(chess.ROOK, chess.BLACK))
    board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))

    forks = find_forks(board)

    assert len(forks) == 1
    assert forks[0].square == "d6"
    assert forks[0].piece_type == "knight"
    assert forks[0].color == "white"
    assert set(forks[0].forked_squares) == {"b7", "e8"}


def test_find_forks_ignores_piece_attacking_only_one_enemy_piece() -> None:
    board = _empty_board_with_kings()
    board.set_piece_at(chess.E4, chess.Piece(chess.KNIGHT, chess.WHITE))
    board.set_piece_at(chess.D6, chess.Piece(chess.PAWN, chess.BLACK))  # only one knight target

    assert find_forks(board) == []
