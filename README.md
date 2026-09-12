# Chess Trainer

Diagnoses which tactical themes are stalling your Lichess puzzle rating, points you at curated
lessons for each one, and — for puzzles in your weakest theme — has an AI walk through why the
solution actually works. Instead of grinding puzzles with no structure.

It pulls your own puzzle-performance-by-theme straight from Lichess's API, ranks your weakest
themes by their actual performance rating, attaches a couple of solid hand-checked lessons to
each one, and can narrate an explanation of any specific puzzle grounded in real board analysis
rather than a model just guessing at what it sees.

## How it works

1. `LichessClient` fetches your account's puzzle dashboard (`/api/puzzle/dashboard/{days}`) —
   Lichess already computes per-theme performance, so this app doesn't reinvent that.
2. `rank_weak_themes` sorts your themes weakest-first, dropping any with too few attempts to be
   a meaningful signal.
3. `resources.get_resources` attaches learning material to each weak theme: a guaranteed link to
   Lichess's own theme-filtered puzzle trainer, plus a hand-verified external lesson for the
   themes people most commonly plateau on.
4. For a specific puzzle, `puzzle_position.build_puzzle_position` replays its solution through
   `python-chess` and `tactics.py` checks the starting position for pins/forks/hanging pieces —
   real, verified facts about the board, not something an AI model is trusted to read correctly
   on its own. `prompt.build_explanation_prompt` turns that into one prompt (prioritized toward
   your current weakest theme when it applies), and a provider-fallback router sends it to
   whichever AI backend is configured and working.

You can use this as a one-off CLI command, a small local API server, or a browser extension
that layers both of the above onto lichess.org itself.

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

The AI explainer needs at least one provider configured too — see
[AI puzzle explainer](#ai-puzzle-explainer) below; everything else works without one.

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
| `GET /api/explain/{puzzle_id}` | AI-narrated explanation of one puzzle's solution |

## AI puzzle explainer

`/api/explain/{puzzle_id}` fetches the puzzle from Lichess, validates its FEN/solution through
`python-chess`, runs the classical tactic detectors, builds a prompt grounded in all of that,
and sends it through a **provider-fallback router**: it tries each configured AI provider in
order and falls back to the next on failure, so no single vendor being down or rate-limited
breaks the feature. Each provider sits behind its own circuit breaker — after repeated failures
it's skipped for a cooldown period instead of being retried (and paid for) on every request.

Configure any subset of these in `.env` — the router only tries providers with a key set:

| Provider | Env vars | Notes |
| --- | --- | --- |
| Gemini | `GEMINI_API_KEY`, `GEMINI_MODEL` | <https://aistudio.google.com/apikey> |
| DeepSeek | `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` | <https://platform.deepseek.com/api_keys> |
| Groq | `GROQ_API_KEY`, `GROQ_MODEL` | <https://console.groq.com/keys> |
| Ollama | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Local, no key — needs Ollama installed and the model pulled (`ollama pull llama3.2`) |

Fallback order is Gemini → DeepSeek → Groq → Ollama (cloud providers first, then the free local
one last). With nothing configured at all, Ollama is still tried — it just fails if it isn't
actually running locally.

## Browser extension

A Manifest V3 extension (`extension/`) brings both of the above into the browser instead of the
CLI or raw HTTP calls:

- **Popup** — the same weak-theme diagnosis as `/api/weaknesses`, one click from the toolbar.
- **Content script** — on any lichess.org/training puzzle, an "Explain this puzzle" button
  appears; clicking it calls `/api/explain/{puzzle_id}` for the puzzle actually on screen and
  shows the result inline, prioritized toward your current weakest theme when it applies.

Both talk to the API server above over `localhost`, so that still needs to be running.

See [`extension/README.md`](extension/README.md) for how to load it unpacked, and
[`extension/TESTING.md`](extension/TESTING.md) for a manual test checklist.

## Demo: trying it end-to-end

1. Follow **Setup** above, then fill in `LICHESS_API_TOKEN` and at least one AI provider's
   config in `.env` (Groq's free tier is the fastest way to get something working).
2. Start the backend: `uvicorn chess_trainer.api:app --reload`.
3. Load the extension unpacked (`extension/README.md`) and pin it to the toolbar.
4. Click the toolbar icon — your ranked weakest themes appear, each with resources to study.
5. Open a puzzle at <https://lichess.org/training> and solve (or miss) it.
6. Click the green "Explain this puzzle" button in the bottom-right corner — after a moment,
   an AI-narrated explanation appears, grounded in the puzzle's actual solution and tactical
   facts about the position, and calling out your weakest theme if this puzzle happens to be
   tagged with it.

## Running tests

```bash
pytest
```

Tests mock all Lichess/AI-provider HTTP calls (via `responses`), so they run offline and don't
touch your real account or any real API key.

## Project layout

```text
chess_trainer/
  config.py               settings (.env handling)
  lichess_client.py        Lichess API client (dashboard, activity, single puzzle)
  lichess_models.py        response models for the Lichess API
  themes.py                 Lichess's puzzle theme id -> display name
  resources.py               curated learning resources per theme
  weakness.py                 ranks themes from a dashboard
  puzzle_position.py          validates a puzzle's FEN/solution via python-chess, gets SAN
  tactics.py                   pin/fork/hanging-piece detection over a chess.Board
  prompt.py                    builds the AI explainer's prompt from the above
  providers/                   provider-fallback router
    base.py                     adapter interface + shared HTTP-error handling
    circuit_breaker.py           closed/open/half-open failure tracking
    router.py                    tries adapters in order, falls back on failure
    factory.py                   assembles the real router from Settings
    gemini.py, deepseek.py, groq.py, ollama.py   one adapter each
  errors.py                   LichessAPIError / MissingApiTokenError
  logging_config.py           basic logging setup
  cli.py                       `chess-trainer weaknesses`
  api.py                       FastAPI app
  api_schemas.py                HTTP response models
tests/                        mirrors the modules above
extension/                    Manifest V3 browser extension
  popup/                        toolbar popup — weak themes
  options/                      settings page — Lichess API token storage
  content/                      injects the "Explain this puzzle" button on lichess.org
  background/                   service worker — message hub + the actual API calls
```

## Status

All three phases are done: Phase A (the diagnosis engine — CLI + API), Phase B (the browser
extension popup), and Phase C (auto-detecting the current puzzle and an AI-narrated explanation
for it, prioritized toward your weakest theme, via a provider-fallback router).
