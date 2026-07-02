const API_BASE = "https://primeai-backendtest.onrender.com/api/v1";
const TOKEN_KEY = "primetrade_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function requireAuthOrRedirect() {
  if (!getToken()) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}

async function apiRequest(path, { method = "GET", body, form = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let payload;
  if (body !== undefined) {
    if (form) {
      headers["Content-Type"] = "application/x-www-form-urlencoded";
      payload = new URLSearchParams(body).toString();
    } else {
      headers["Content-Type"] = "application/json";
      payload = JSON.stringify(body);
    }
  }

  const response = await fetch(`${API_BASE}${path}`, { method, headers, body: payload });

  if (response.status === 401) {
    clearToken();
    if (!path.includes("/auth/login")) {
      window.location.href = "index.html";
    }
  }

  if (response.status === 204) {
    return null;
  }

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    const message = extractErrorMessage(data) || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

function extractErrorMessage(data) {
  if (!data) return null;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg || JSON.stringify(e)).join(", ");
  }
  return null;
}

function showMessage(el, text, type) {
  el.textContent = text;
  el.className = `message ${type}`;
}

function hideMessage(el) {
  el.className = "message";
  el.textContent = "";
}

function setLoading(button, isLoading, label) {
  button.disabled = isLoading;
  button.innerHTML = isLoading ? `<span class="spinner"></span>${label}...` : label;
}
