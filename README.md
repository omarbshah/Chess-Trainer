# Chess Trainer

Diagnoses which tactical themes are stalling your Lichess puzzle rating, and points you at
curated lessons for each one — instead of grinding puzzles with no structure.

It pulls your own puzzle-performance-by-theme straight from Lichess's API, ranks your weakest
themes by their actual performance rating, and attaches a couple of solid, hand-checked lessons
to each one.

## How it works

1. `LichessClient` fetches your account's puzzle dashboard (`/api/puzzle/dashboard/{days}`) —
   Lichess already computes per-theme performance, so this app doesn't reinvent that.
2. `rank_weak_themes` sorts your themes weakest-first, dropping any with too few attempts to be
   a meaningful signal.
3. `resources.get_resources` attaches learning material to each weak theme: a guaranteed link to
   Lichess's own theme-filtered puzzle trainer, plus a hand-verified external lesson for the
   themes people most commonly plateau on.

You can use this either as a one-off CLI command or as a small local API server.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate       # .venv\Scripts\activate on Windows
pip install -e ".[test]"
cp .env.example .env
```

Then fill in `LICHESS_API_TOKEN` in `.env` — create a personal token at
<https://lichess.org/account/oauth/token>. Puzzle dashboard/activity endpoints need a token
scoped to your own account; nothing else in this project needs write access to anything.

## Usage

**CLI** — ranked weak themes printed straight to your terminal:

```bash
chess-trainer weaknesses --days 30 --top 3
```

Flags: `--days` (history window, default 30), `--top` (how many themes to show, default 3),
`--min-attempts` (minimum attempts for a theme to be ranked, default 5).

**API server** — the same logic over HTTP, for the browser extension below:

```bash
uvicorn chess_trainer.api:app --reload
```

| Endpoint | Description |
| --- | --- |
| `GET /health` | Liveness check |
| `GET /api/weaknesses?days=30&top=3&min_attempts=5` | Ranked weak themes with resources |
| `GET /api/resources/{theme_id}` | Curated resources for one theme id |

## Browser extension

A small Manifest V3 extension (`extension/`) puts the same weak-theme diagnosis in a popup,
right in the browser, instead of the CLI or a raw HTTP call. It talks to the API server above
over `localhost`, so that still needs to be running.

See [`extension/README.md`](extension/README.md) for how to load it unpacked, and
[`extension/TESTING.md`](extension/TESTING.md) for a manual test checklist.

## Running tests

```bash
pytest
```

Tests mock all Lichess HTTP calls (via `responses`), so they run offline and don't touch your
real account.

## Project layout

```text
chess_trainer/
  config.py           settings (.env handling)
  lichess_client.py    Lichess API client (dashboard, activity)
  lichess_models.py    response models for the Lichess API
  themes.py             Lichess's puzzle theme id -> display name
  resources.py          curated learning resources per theme
  weakness.py            ranks themes from a dashboard
  errors.py              LichessAPIError / MissingApiTokenError
  logging_config.py      basic logging setup
  cli.py                  `chess-trainer weaknesses`
  api.py                  FastAPI app
  api_schemas.py          HTTP response models
tests/                    mirrors the modules above
extension/                Manifest V3 browser extension (popup + options page)
```

## Status

Phase A (the diagnosis engine — CLI + API) and Phase B (the browser extension popup showing
that same data) are both done. Next up is Phase C: auto-detecting the puzzle you're currently
on and adding an AI-narrated explanation for puzzles you missed in your weakest theme.
