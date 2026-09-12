# Chess Trainer Extension — Manual Test Checklist

There's no automated test runner for the extension itself (see `tests/` at the project root for
the backend's automated suite). Run through this by hand after loading/reloading the unpacked
extension — see `README.md` for how.

## Setup

- [ ] Backend running (`uvicorn chess_trainer.api:app --reload`) with a valid token in `.env`
- [ ] Extension loaded unpacked, pinned to the toolbar

## Popup — happy path

- [ ] Opening the popup briefly shows "Loading your weak themes…"
- [ ] Ranked weak themes appear, each with performance/attempts/solved-first-try stats
- [ ] Each theme's resource links are present and open in a new tab
- [ ] Resource links point at the expected URLs (spot-check one against
  `GET /api/resources/{theme_id}`)

## Popup — empty result

- [ ] With `min_attempts` set high enough that no theme qualifies (e.g. temporarily hit
  `/api/weaknesses?min_attempts=100000` in a browser tab to confirm the backend also returns
  an empty list), the popup shows the "keep solving puzzles" message instead of a blank list

## Popup — error states

- [ ] Stop the backend, reopen the popup → "Can't reach the local backend…" message shown
- [ ] Restart the backend, reopen the popup → recovers back to the happy path
- [ ] With the backend running but returning an error (e.g. an invalid/expired Lichess token in
  `.env`) → popup shows the backend's error detail, not a raw crash

## Options page

- [ ] Right-click the icon → Options opens the settings page in a new tab
- [ ] Entering a token and clicking Save shows a "Saved." confirmation
- [ ] Reopening the options page shows the previously saved token still populated
- [ ] Clearing the field and saving persists an empty value (doesn't error)

## "Explain this puzzle" button (content script)

- [ ] Open a puzzle at lichess.org/training — a green "Explain this puzzle" button appears
  fixed in the bottom-right corner
- [ ] Clicking it shows "Explaining…", then replaces it with an AI-narrated explanation
- [ ] The explanation text is specific to the actual puzzle on screen (spot-check against
  `GET /api/explain/{puzzle_id}` for that puzzle's id)
- [ ] Button is disabled (not double-clickable) while a request is in flight
- [ ] Stop the backend, click the button → panel shows a "Couldn't get an explanation" message,
  not a silent failure or a raw browser error
- [ ] Open the page's own DevTools console — no CORS errors from the explain request (it's
  routed through the background service worker, not fetched directly from the page)

## Icons / manifest

- [ ] Toolbar icon shows the pawn glyph, not a placeholder/broken image
- [ ] `chrome://extensions` card shows the same icon at its larger size
- [ ] Options page browser tab shows the icon and the title "Chess Trainer Settings"

## Cross-origin sanity check

- [ ] Open the popup's DevTools console (right-click → Inspect) — no CORS errors on load
