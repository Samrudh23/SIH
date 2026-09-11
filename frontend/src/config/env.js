/**
 * Environment Configuration for SIH26034 P4 Frontend
 * Supports: development, staging, production
 * 
 * Rules:
 * 1. Never hard-code production backend as localhost.
 * 2. In production, mock data is strictly disabled.
 * 3. Supports runtime window.__ENV__ overrides for containerized/static deployments.
 */

function detectEnvironment() {
  if (typeof window === "undefined") return "development";

  // Check explicit runtime env injection (e.g. from server or container env)
  if (window.__ENV__?.APP_ENV) {
    return window.__ENV__.APP_ENV;
  }

  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return "development";
  }
  if (hostname.includes("stage") || hostname.includes("staging") || hostname.includes("preview")) {
    return "staging";
  }
  return "production";
}

function resolveApiBaseUrl(env) {
  if (typeof window !== "undefined") {
    // 1. Explicit runtime override
    if (window.__ENV__?.API_BASE_URL) {
      return window.__ENV__.API_BASE_URL.replace(/\/+$/, "");
    }
    // 2. Local storage override for debugging/testing
    const localOverride = localStorage.getItem("sih_api_base_url");
    if (localOverride) {
      return localOverride.replace(/\/+$/, "");
    }

    // 3. Unified full-stack deployment check:
    // If loaded on the unified backend server (port 8000 or any non-dev port/domain), use same-origin /api
    if (window.location.port !== "3000" && window.location.port !== "5173") {
      return "/api";
    }
  }

  // 4. Environment-based defaults
  switch (env) {
    case "production":
      // In production, use same-origin /api (standard reverse-proxy pattern)
      return "/api";
    case "staging":
      return "/api";
    case "development":
    default:
      // Local development default pointing to P3 FastAPI server
      return "http://127.0.0.1:8000/api";
  }
}

const APP_ENV = detectEnvironment();
const API_BASE_URL = resolveApiBaseUrl(APP_ENV);
const IS_PRODUCTION = APP_ENV === "production";
const ALLOW_MOCK = !IS_PRODUCTION; // Strictly disabled in production

export const ENV = Object.freeze({
  APP_ENV,
  API_BASE_URL,
  IS_PRODUCTION,
  ALLOW_MOCK,
});

export default ENV;
