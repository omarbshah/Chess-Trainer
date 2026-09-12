// Background service worker — hub between the content script and the popup.
//
// The content script pushes the puzzle id it detects on the current tab; the popup pulls
// the latest known id for the active tab when it opens. Kept in memory only (a service
// worker can be killed and restarted at any time, but re-detection on the content script
// side means this state is cheap to lose).

const API_BASE = "http://127.0.0.1:8000";

const puzzleIdByTab = new Map();

async function explainPuzzle(puzzleId) {
  const response = await fetch(`${API_BASE}/api/explain/${puzzleId}`);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
  return response.json();
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "PUZZLE_DETECTED") {
    if (sender.tab?.id != null) {
      puzzleIdByTab.set(sender.tab.id, message.puzzleId);
    }
    return false;
  }

  if (message?.type === "GET_CURRENT_PUZZLE") {
    const puzzleId = message.tabId != null ? puzzleIdByTab.get(message.tabId) ?? null : null;
    sendResponse({ puzzleId });
    return false;
  }

  if (message?.type === "EXPLAIN_PUZZLE") {
    // Run from here, not the content script: the backend's CORS config only allows
    // chrome-extension:// origins, and a fetch from the content script would carry the
    // page's own https://lichess.org origin instead.
    explainPuzzle(message.puzzleId)
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true; // keep the message channel open for the async sendResponse above
  }

  return false;
});

// Stop the map from growing forever as tabs come and go.
chrome.tabs.onRemoved.addListener((tabId) => {
  puzzleIdByTab.delete(tabId);
});
