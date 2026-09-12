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
  // Filled in in the next commit.
  console.log(themes);
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
