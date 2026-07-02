const BASE_URL = import.meta.env.VITE_BFF_URL || "http://localhost:8000";

export interface ApiError {
  errorCode?: string;
  message: string;
  details?: unknown;
}

export interface ApiCallResult<T> {
  ok: boolean;
  status: number;
  durationMs: number;
  data?: T;
  raw: unknown;
  error?: ApiError;
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<ApiCallResult<T>> {
  const started = performance.now();
  const headers = new Headers(init.headers);
  headers.set("Authorization", "Bearer demo-token");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  try {
    const response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
    const raw = await readJson(response);
    const durationMs = Math.round((performance.now() - started) * 100) / 100;
    const envelope = raw as { success?: boolean; data?: T; errorCode?: string; message?: string; details?: unknown } | null;

    if (!response.ok || envelope?.success === false) {
      return {
        ok: false,
        status: response.status,
        durationMs,
        raw,
        error: {
          errorCode: envelope?.errorCode,
          message: envelope?.message || response.statusText || "Request failed",
          details: envelope?.details
        }
      };
    }

    return {
      ok: true,
      status: response.status,
      durationMs,
      data: envelope?.data as T,
      raw
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      durationMs: Math.round((performance.now() - started) * 100) / 100,
      raw: null,
      error: {
        errorCode: "NETWORK_ERROR",
        message: error instanceof Error ? error.message : "Network request failed"
      }
    };
  }
}

export function apiGet<T>(path: string) {
  return apiRequest<T>(path);
}

export function apiPost<T>(path: string, payload?: unknown) {
  return apiRequest<T>(path, {
    method: "POST",
    body: payload === undefined ? undefined : JSON.stringify(payload)
  });
}

export function apiPatch<T>(path: string, payload?: unknown) {
  return apiRequest<T>(path, {
    method: "PATCH",
    body: payload === undefined ? undefined : JSON.stringify(payload)
  });
}

