"""Command-line entry point: `chess-trainer weaknesses` ties the dashboard fetch,
weakness ranking, and curated resources together into something runnable.
"""

from __future__ import annotations

import argparse

from chess_trainer.lichess_client import LichessClient
from chess_trainer.resources import get_resources
from chess_trainer.weakness import rank_weak_themes


def weaknesses_command(days: int, top: int, min_attempts: int) -> None:
    with LichessClient() as client:
        dashboard = client.get_puzzle_dashboard(days)

    ranked = rank_weak_themes(dashboard, min_attempts=min_attempts)

    if not ranked:
        print(f"Not enough puzzle attempts in the last {days} days to rank any themes.")
        print(f"(A theme needs at least {min_attempts} attempts to be counted.)")
        return

    print(f"Weakest themes over the last {days} days:\n")
    for theme in ranked[:top]:
        solve_pct = round(theme.first_win_rate * 100)
        print(f"- {theme.display_name} ({theme.theme_id})")
        print(
            f"    performance {theme.performance} · {theme.attempts} attempts "
            f"· {solve_pct}% solved first try"
        )
        for resource in get_resources(theme.theme_id):
            print(f"    -> {resource.title} [{resource.source}]: {resource.url}")
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chess-trainer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    weaknesses_parser = subparsers.add_parser(
        "weaknesses", help="Rank your weakest Lichess puzzle themes and show lessons for each."
    )
    weaknesses_parser.add_argument(
        "--days", type=int, default=30, help="How many days of puzzle history to look at (default: 30)."
    )
    weaknesses_parser.add_argument(
        "--top", type=int, default=3, help="How many weak themes to show (default: 3)."
    )
    weaknesses_parser.add_argument(
        "--min-attempts",
        type=int,
        default=5,
        help="Minimum attempts for a theme to be ranked (default: 5).",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "weaknesses":
        weaknesses_command(days=args.days, top=args.top, min_attempts=args.min_attempts)


if __name__ == "__main__":
    main()
