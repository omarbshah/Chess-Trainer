// Content script injected on lichess.org/training/* puzzle pages.

function getCurrentPuzzleId() {
  // Lichess embeds the current puzzle's data as JSON in a #page-init-data script tag
  // (verified against a live /training page): {"data":{"puzzle":{"id":"...", ...}, ...}}.
  const dataEl = document.getElementById("page-init-data");
  if (dataEl) {
    try {
      const parsed = JSON.parse(dataEl.textContent);
      const id = parsed?.data?.puzzle?.id;
      if (id) {
        return id;
      }
    } catch (err) {
      console.warn("Chess Trainer: couldn't parse page-init-data", err);
    }
  }

  // Fallback: a specific puzzle's URL is /training/<id>. The "next puzzle" landing page
  // (bare /training, no id in the URL) has nothing to fall back to here.
  const match = location.pathname.match(/^\/training\/(\w+)/);
  return match ? match[1] : null;
}

const puzzleId = getCurrentPuzzleId();
if (puzzleId) {
  chrome.runtime.sendMessage({ type: "PUZZLE_DETECTED", puzzleId });
}
