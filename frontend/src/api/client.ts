import type { Result } from "../types/search";
import type { StatusResponse, StatsResponse } from "../types/status";

const API_BASE = "";

export interface SearchResponse {
  query: string;
  total: number;
  latency_ms: number;
  results: Result[];
}

export type SearchResult =
  | { ok: true; data: SearchResponse }
  | { ok: false; kind: "daemon_offline" | "error" | "network"; message: string };

export async function searchAPI(
  query: string,
  filters?: Record<string, any>,
  limit: number = 20,
  signal?: AbortSignal
): Promise<SearchResult> {
  if (!query.trim()) {
    return {
      ok: true,
      data: { query: "", total: 0, latency_ms: 0, results: [] },
    };
  }

  try {
    const res = await fetch(`${API_BASE}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, filters, limit }),
      signal,
    });

    if (!res.ok) {
      let message = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errJson = await res.json();
        if (errJson && typeof errJson.detail === "string") {
          message = errJson.detail;
        }
      } catch {
        // fallback to HTTP status text
      }

      if (res.status === 503) {
        return {
          ok: false,
          kind: "daemon_offline",
          message,
        };
      }

      return {
        ok: false,
        kind: "error",
        message,
      };
    }

    const data: SearchResponse = await res.json();
    return { ok: true, data };
  } catch (err: any) {
    if (err.name === "AbortError") {
      throw err;
    }
    return {
      ok: false,
      kind: "network",
      message: err?.message || "Failed to reach SemanticFS API service.",
    };
  }
}

export async function fetchStatus(): Promise<StatusResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (res.ok) {
      return (await res.json()) as StatusResponse;
    }
  } catch {
    // fallback
  }
  return null;
}

export async function fetchStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (res.ok) {
      return (await res.json()) as StatsResponse;
    }
  } catch {
    // fallback
  }
  return null;
}

export async function revealAPI(filepath: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/reveal`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ filepath }),
    });
    return res.ok;
  } catch {
    return false;
  }
}
