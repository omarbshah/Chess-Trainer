// Popup logic — fetches weak themes from the local backend and renders them.

const API_BASE = "http://127.0.0.1:8000";

async function fetchWeaknesses() {
  const response = await fetch(`${API_BASE}/api/weaknesses`);
  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }
  return response.json();
}

function renderThemes(themes) {
  const list = document.getElementById("theme-list");
  const status = document.getElementById("status");
  list.innerHTML = "";

  if (themes.length === 0) {
    status.textContent = "No weak themes to show yet — keep solving puzzles!";
    return;
  }

  status.textContent = "";
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

async function init() {
  try {
    const themes = await fetchWeaknesses();
    renderThemes(themes);
  } catch (err) {
    // Loading/error UI polish lands in a later commit — for now, just don't crash the popup.
    console.error("Failed to fetch weaknesses:", err);
  }
}

document.addEventListener("DOMContentLoaded", init);
