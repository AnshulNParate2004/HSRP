const API_BASE = import.meta.env.VITE_API_URL ?? "/api/v1";
const TOKEN_KEY = "hsrp_access_token";

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/** Build query string with optional vehicle_type and extra params. */
export function buildQuery(
  vehicleType: string | null,
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  const search = new URLSearchParams();
  if (vehicleType) search.set("vehicle_type", vehicleType);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        search.set(key, String(value));
      }
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function vehicleQuery(vehicleType: string | null): string {
  return buildQuery(vehicleType);
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    if (!window.location.pathname.startsWith("/login")) {
      window.location.href = "/login";
    }
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

export function getApiBase(): string {
  return API_BASE;
}
