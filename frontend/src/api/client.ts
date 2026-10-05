import type { Result } from "../types/search";

const API_BASE =
  typeof window !== "undefined" && window.location.port === "5173"
    ? "http://127.0.0.1:8000"
    : "";

export interface SearchResponse {
  query: string;
  total: number;
  latency_ms: number;
  results: Result[];
}

export async function searchAPI(
  query: string,
  filters?: Record<string, any>,
  limit: number = 20,
  signal?: AbortSignal
): Promise<SearchResponse | null> {
  if (!query.trim()) {
    return { query: "", total: 0, latency_ms: 0, results: [] };
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
      return null;
    }

    const data: SearchResponse = await res.json();
    return data;
  } catch (err: any) {
    if (err.name === "AbortError") {
      throw err;
    }
    return null;
  }
}

export async function fetchStatus(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // fallback
  }
  return null;
}

export async function fetchStats(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // fallback
  }
  return null;
}
