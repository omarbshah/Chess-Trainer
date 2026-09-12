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

function createExplainWidget() {
  const button = document.createElement("button");
  button.id = "chess-trainer-explain-button";
  button.type = "button";
  button.textContent = "Explain this puzzle";
  Object.assign(button.style, {
    position: "fixed",
    bottom: "16px",
    right: "16px",
    zIndex: "2147483647",
    padding: "8px 14px",
    borderRadius: "6px",
    border: "none",
    background: "#2f6f4f",
    color: "#fff",
    fontSize: "14px",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    cursor: "pointer",
    boxShadow: "0 2px 6px rgba(0, 0, 0, 0.3)",
  });

  const panel = document.createElement("div");
  panel.id = "chess-trainer-explain-panel";
  Object.assign(panel.style, {
    position: "fixed",
    bottom: "60px",
    right: "16px",
    width: "300px",
    maxHeight: "40vh",
    overflowY: "auto",
    padding: "12px",
    borderRadius: "8px",
    background: "#1e1e1e",
    color: "#f0f0f0",
    fontSize: "13px",
    lineHeight: "1.4",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    boxShadow: "0 2px 10px rgba(0, 0, 0, 0.4)",
    zIndex: "2147483647",
    display: "none",
  });

  document.body.append(button, panel);
  button.addEventListener("click", () => onExplainClick(button, panel));
}

async function onExplainClick(button, panel) {
  const puzzleId = getCurrentPuzzleId();
  panel.style.display = "block";

  if (!puzzleId) {
    panel.textContent = "Couldn't find a puzzle id on this page.";
    return;
  }

  button.disabled = true;
  panel.textContent = "Explaining…";

  // Routed through the background service worker rather than fetched directly here: the
  // backend's CORS config (commit 22) only allows chrome-extension:// origins, and a fetch
  // from this content script would carry the page's own https://lichess.org origin instead.
  const result = await chrome.runtime.sendMessage({ type: "EXPLAIN_PUZZLE", puzzleId });

  button.disabled = false;
  if (result?.ok) {
    panel.textContent = result.data.explanation;
  } else {
    panel.textContent = `Couldn't get an explanation: ${result?.error ?? "unknown error"}`;
  }
}

const puzzleId = getCurrentPuzzleId();
if (puzzleId) {
  chrome.runtime.sendMessage({ type: "PUZZLE_DETECTED", puzzleId });
}

createExplainWidget();
