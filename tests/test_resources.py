from chess_trainer.resources import get_resources


def test_every_theme_gets_the_lichess_trainer_link() -> None:
    resources = get_resources("someObscureThemeWithNoCuration")

    assert len(resources) == 1
    assert resources[0].source == "Lichess Puzzle Trainer"
    assert resources[0].url == "https://lichess.org/training/someObscureThemeWithNoCuration"


def test_curated_theme_includes_trainer_link_plus_extras() -> None:
    resources = get_resources("fork")

    assert resources[0].source == "Lichess Puzzle Trainer"
    assert any(resource.source != "Lichess Puzzle Trainer" for resource in resources)
