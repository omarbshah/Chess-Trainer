// Popup logic — fetches weak themes from the local backend and renders them.

const API_BASE = "http://127.0.0.1:8000";

async function fetchWeaknesses() {
  const response = await fetch(`${API_BASE}/api/weaknesses`);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
  return response.json();
}

function setStatus(message) {
  document.getElementById("status").textContent = message;
}

function renderThemes(themes) {
  const list = document.getElementById("theme-list");
  list.innerHTML = "";

  if (themes.length === 0) {
    setStatus("No weak themes to show yet — keep solving puzzles!");
    return;
  }

  setStatus("");
  for (const theme of themes) {
    list.appendChild(buildThemeItem(theme));
  }
}

function buildThemeItem(theme) {
  const item = document.createElement("li");
  item.className = "theme-item";

  const name = document.createElement("div");
  name.className = "theme-name";
  name.textContent = theme.display_name;
  item.appendChild(name);

  const stats = document.createElement("div");
  stats.className = "theme-stats";
  const solvePct = Math.round(theme.first_win_rate * 100);
  stats.textContent =
    `${theme.performance} performance · ${theme.attempts} attempts · ${solvePct}% solved first try`;
  item.appendChild(stats);

  if (theme.resources.length > 0) {
    const resources = document.createElement("div");
    resources.className = "theme-resources";
    theme.resources.forEach((resource, index) => {
      const link = document.createElement("a");
      link.href = resource.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = resource.title;
      resources.appendChild(link);
      if (index < theme.resources.length - 1) {
        resources.appendChild(document.createTextNode(" · "));
      }
    });
    item.appendChild(resources);
  }

  return item;
}

async function getCurrentPuzzleId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    return null;
  }
  const response = await chrome.runtime.sendMessage({ type: "GET_CURRENT_PUZZLE", tabId: tab.id });
  return response?.puzzleId ?? null;
}

async function init() {
  document.getElementById("theme-list").innerHTML = "";
  setStatus("Loading your weak themes…");

  try {
    const themes = await fetchWeaknesses();
    renderThemes(themes);
  } catch (err) {
    console.error("Failed to fetch weaknesses:", err);
    if (err instanceof TypeError) {
      // fetch() rejects with a bare TypeError for network-level failures — backend not
      // running, wrong port, CORS rejection, etc. There's no response to read a detail from.
      setStatus("Can't reach the local backend. Is it running on port 8000?");
    } else {
      setStatus(`Couldn't load weaknesses: ${err.message}`);
    }
  }

  // Not surfaced in the UI yet — later commits (the "Explain this" button, weakest-theme
  // prioritization) will do something with this. For now just confirm the plumbing works.
  console.log("Chess Trainer: current tab's puzzle id ->", await getCurrentPuzzleId());
}

document.addEventListener("DOMContentLoaded", init);
