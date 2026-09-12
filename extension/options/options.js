// Options page logic — stores the Lichess API token in chrome.storage.local.

const STORAGE_KEY = "lichessApiToken";

const form = document.getElementById("settings-form");
const tokenInput = document.getElementById("lichess-token");
const status = document.getElementById("status");

async function loadToken() {
  const stored = await chrome.storage.local.get(STORAGE_KEY);
  if (stored[STORAGE_KEY]) {
    tokenInput.value = stored[STORAGE_KEY];
  }
}

async function saveToken(event) {
  event.preventDefault();
  await chrome.storage.local.set({ [STORAGE_KEY]: tokenInput.value.trim() });
  status.textContent = "Saved.";
  setTimeout(() => {
    status.textContent = "";
  }, 2000);
}

form.addEventListener("submit", saveToken);
document.addEventListener("DOMContentLoaded", loadToken);
