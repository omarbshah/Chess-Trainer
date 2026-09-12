# Chess Trainer — Browser Extension (dev)

The Phase B extension shell: a popup that shows your weakest Lichess puzzle themes, pulled
from the local backend built in Phase A.

## Prerequisites

The backend needs to be running locally — see the main project README. From
`ChessTrainerMain/`:

```bash
uvicorn chess_trainer.api:app --reload
```

with a valid `LICHESS_API_TOKEN` in `.env`. The popup fetches `http://127.0.0.1:8000` directly,
so nothing works until this is up.

## Loading the unpacked extension (Chrome / Edge / other Chromium browsers)

1. Open `chrome://extensions`.
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked**.
4. Select the `ChessTrainerMain/extension/` folder (the one with `manifest.json` in it).
5. Click the puzzle-piece icon in the toolbar and pin "Chess Trainer" for quick access.

## Using it

- Click the toolbar icon to open the popup — it fetches ranked weak themes and lists each one
  with its resources.
- Right-click the icon → **Options** to open the settings page, which stores a Lichess API
  token in the extension's local storage. Nothing reads this value yet (the backend still
  authenticates every request with its own `.env` token) — it's there for a later phase to
  wire up.

## Reloading after changes

Chrome doesn't auto-reload unpacked extensions when files change on disk. After editing
anything under `extension/`:

1. Go to `chrome://extensions`.
2. Click the refresh icon on the Chess Trainer card.
3. Reopen the popup (or options page) to see the change.

## Troubleshooting

- **Popup shows "Can't reach the local backend"** — the backend isn't running, or isn't on
  port 8000.
- **A CORS error in the popup's console instead** — the backend is running but its CORS config
  is stale; restart it after pulling changes to `chess_trainer/api.py`.
