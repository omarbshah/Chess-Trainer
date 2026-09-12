from chess_trainer.lichess_models import PuzzleDetail
from chess_trainer.prompt import build_explanation_prompt
from chess_trainer.puzzle_position import build_puzzle_position

# Same real puzzle (id "fcEqc") used in test_lichess_client.py and test_puzzle_position.py.
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


def _build_prompt() -> str:
    detail = PuzzleDetail.model_validate(PUZZLE_DETAIL_PAYLOAD)
    position = build_puzzle_position(detail)
    return build_explanation_prompt(position)


def test_prompt_includes_the_position_and_metadata() -> None:
    prompt = _build_prompt()

    assert "2r3k1/1pr3pp/3b4/8/1pq1Q3/P4RPP/1B2RP2/1K6 w - - 1 1" in prompt
    assert "White to move." in prompt
    assert "1289" in prompt
    assert "middlegame, long, mateIn3, sacrifice" in prompt


def test_prompt_includes_the_full_san_solution_in_order() -> None:
    prompt = _build_prompt()

    assert "1. Qe8+ (solver)" in prompt
    assert "2. Rxe8 (opponent)" in prompt
    assert "3. Rxe8+ (solver)" in prompt
    assert "4. Bf8 (opponent)" in prompt
    assert "5. Rfxf8# (solver)" in prompt


def test_prompt_includes_verified_tactical_facts_for_this_position() -> None:
    # In fcEqc's starting position, tactics.py finds the white queen on e4 forking c4/b7/h7.
    prompt = _build_prompt()

    assert "Verified tactical facts" in prompt
    assert "white queen on e4 forks" in prompt


def test_prompt_instructs_the_model_not_to_go_beyond_the_given_solution() -> None:
    prompt = _build_prompt()

    assert "Don't suggest any other moves" in prompt
