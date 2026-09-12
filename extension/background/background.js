// Background service worker — hub between the content script and the popup.
//
// The content script pushes the puzzle id it detects on the current tab; the popup pulls
// the latest known id for the active tab when it opens. Kept in memory only (a service
// worker can be killed and restarted at any time, but re-detection on the content script
// side means this state is cheap to lose).

const puzzleIdByTab = new Map();

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

  return false;
});

// Stop the map from growing forever as tabs come and go.
chrome.tabs.onRemoved.addListener((tabId) => {
  puzzleIdByTab.delete(tabId);
});
