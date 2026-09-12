from chess_trainer.lichess_models import PuzzleDetail
from chess_trainer.puzzle_position import build_puzzle_position

# Same real puzzle as tests/test_lichess_client.py's PUZZLE_DETAIL_PAYLOAD (id "fcEqc"),
# trimmed to what build_puzzle_position actually reads.
PUZZLE_DETAIL_PAYLOAD = {
    "game": {
        "id": "ROdRPQtw",
        "perf": {"key": "blitz", "name": "Blitz"},
        "rated": True,
        "players": [
            {"name": "butchersboys2802", "id": "butchersboys2802", "color": "white", "rating": 1690},
            {"name": "tartinemariol", "id": "tartinemariol", "color": "black", "rating": 1773},
        ],
        "pgn": "Nf3 d5",
        "clock": "5+3",
    },
    "puzzle": {
        "id": "fcEqc",
        "rating": 1289,
        "plays": 671,
        "solution": ["e4e8", "c8e8", "e2e8", "d6f8", "f3f8"],
        "themes": ["middlegame", "long", "mateIn3", "sacrifice"],
        "fen": "2r3k1/1pr3pp/3b4/8/1pq1Q3/P4RPP/1B2RP2/1K6 w - - 1 1",
        "lastMove": "f7c4",
        "initialPly": 53,
    },
}


def test_build_puzzle_position_replays_solution_to_san() -> None:
    detail = PuzzleDetail.model_validate(PUZZLE_DETAIL_PAYLOAD)

    position = build_puzzle_position(detail)

    assert position.puzzle_id == "fcEqc"
    assert position.turn == "white"
    assert position.rating == 1289
    assert position.themes == ["middlegame", "long", "mateIn3", "sacrifice"]

    sans = [move.san for move in position.solution]
    assert sans == ["Qe8+", "Rxe8", "Rxe8+", "Bf8", "Rfxf8#"]


def test_build_puzzle_position_alternates_solver_and_opponent() -> None:
    detail = PuzzleDetail.model_validate(PUZZLE_DETAIL_PAYLOAD)

    position = build_puzzle_position(detail)

    assert [move.by for move in position.solution] == [
        "solver",
        "opponent",
        "solver",
        "opponent",
        "solver",
    ]
