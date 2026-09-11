from chess_trainer.lichess_models import PuzzleDashboard, PuzzlePerformance, ThemeResult
from chess_trainer.weakness import rank_weak_themes


def _performance(*, performance: int, nb: int, first_wins: int) -> PuzzlePerformance:
    return PuzzlePerformance(
        firstWins=first_wins,
        nb=nb,
        performance=performance,
        puzzleRatingAvg=performance,
        replayWins=0,
    )


def _dashboard(themes: dict[str, ThemeResult]) -> PuzzleDashboard:
    return PuzzleDashboard(
        days=30,
        **{"global": _performance(performance=1700, nb=100, first_wins=80)},
        themes=themes,
    )


def test_ranks_weakest_theme_first() -> None:
    dashboard = _dashboard(
        {
            "fork": ThemeResult(theme="fork", results=_performance(performance=1800, nb=20, first_wins=15)),
            "pin": ThemeResult(theme="pin", results=_performance(performance=1500, nb=20, first_wins=10)),
        }
    )

    ranked = rank_weak_themes(dashboard)

    assert [theme.theme_id for theme in ranked] == ["pin", "fork"]


def test_drops_themes_below_min_attempts() -> None:
    dashboard = _dashboard(
        {
            "fork": ThemeResult(theme="fork", results=_performance(performance=1500, nb=2, first_wins=1)),
            "pin": ThemeResult(theme="pin", results=_performance(performance=1600, nb=20, first_wins=10)),
        }
    )

    ranked = rank_weak_themes(dashboard)

    assert [theme.theme_id for theme in ranked] == ["pin"]


def test_min_attempts_is_configurable() -> None:
    dashboard = _dashboard(
        {"fork": ThemeResult(theme="fork", results=_performance(performance=1500, nb=2, first_wins=1))}
    )

    ranked = rank_weak_themes(dashboard, min_attempts=1)

    assert len(ranked) == 1


def test_computes_first_win_rate_and_known_display_name() -> None:
    dashboard = _dashboard(
        {"fork": ThemeResult(theme="fork", results=_performance(performance=1500, nb=20, first_wins=15))}
    )

    ranked = rank_weak_themes(dashboard)

    assert ranked[0].display_name == "Fork"
    assert ranked[0].first_win_rate == 0.75


def test_unknown_theme_id_falls_back_to_dashboard_theme_name() -> None:
    dashboard = _dashboard(
        {
            "notARealTheme": ThemeResult(
                theme="Not a real theme", results=_performance(performance=1500, nb=10, first_wins=5)
            )
        }
    )

    ranked = rank_weak_themes(dashboard)

    assert ranked[0].display_name == "Not a real theme"
