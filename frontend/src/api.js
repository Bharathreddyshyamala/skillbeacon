const API_URL = (
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000/api/v1"
  ).replace(/\/$/, "");
  
  const ACCESS_KEY = "skillbeacon_access_token";
  const REFRESH_KEY = "skillbeacon_refresh_token";
  
  export class ApiError extends Error {
    constructor(message, status) {
      super(message);
      this.status = status;
    }
  }
  
  export function saveTokens(accessToken, refreshToken) {
    localStorage.setItem(ACCESS_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken);
  }
  
  export function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }
  
  export function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }
  
  function errorMessage(payload, fallback) {
    if (typeof payload?.detail === "string") return payload.detail;
    if (Array.isArray(payload?.detail)) {
      return payload.detail.map((item) => item.msg).join(", ");
    }
    return fallback;
  }
  
  async function readResponse(response) {
    if (response.status === 204) return null;
    const type = response.headers.get("content-type") || "";
    return type.includes("application/json")
      ? response.json()
      : { detail: await response.text() };
  }
  
  async function refreshSession() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new ApiError("Session expired.", 401);
  
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  
    const payload = await readResponse(response);
    if (!response.ok) {
      clearTokens();
      throw new ApiError(
        errorMessage(payload, "Unable to refresh session."),
        response.status,
      );
    }
  
    saveTokens(payload.access_token, payload.refresh_token);
  }
  
  export async function apiRequest(path, options = {}, retry = true) {
    const headers = new Headers(options.headers || {});
    const accessToken = localStorage.getItem(ACCESS_KEY);
    const isFormData = options.body instanceof FormData;
  
    if (!isFormData && options.body !== undefined) {
      headers.set("Content-Type", "application/json");
    }
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }
  
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });
  
    if (
      response.status === 401 &&
      retry &&
      getRefreshToken() &&
      path !== "/auth/refresh"
    ) {
      await refreshSession();
      return apiRequest(path, options, false);
    }
  
    const payload = await readResponse(response);
    if (!response.ok) {
      throw new ApiError(
        errorMessage(payload, `Request failed (${response.status}).`),
        response.status,
      );
    }
    return payload;
  }
  export function jsonBody(data) {
    return JSON.stringify(data);
  }