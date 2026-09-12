// Background service worker — runs the actual backend fetch for the content script's
// "Explain this puzzle" button.
//
// This has to happen here rather than in the content script itself: the backend's CORS
// config only allows chrome-extension:// origins, and a fetch from the content script would
// carry the page's own https://lichess.org origin instead. A service worker's fetch carries
// the extension's origin, so it clears CORS with no backend changes needed.

const API_BASE = "http://127.0.0.1:8000";

async function explainPuzzle(puzzleId) {
  const response = await fetch(`${API_BASE}/api/explain/${puzzleId}`);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
  return response.json();
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "EXPLAIN_PUZZLE") {
    explainPuzzle(message.puzzleId)
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true; // keep the message channel open for the async sendResponse above
  }

  return false;
});
