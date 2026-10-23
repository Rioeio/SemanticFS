import { useState, useEffect, useCallback } from "react";
import { SearchScreen } from "./components/search";
import { PreviewPanel } from "./components/detail";
import { StatusPanel } from "./components/status";
import { searchAPI, revealAPI } from "./api/client";
import type { Result } from "./types/search";

export default function App() {
  const [query, setQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [previewResult, setPreviewResult] = useState<Result | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [searchError, setSearchError] = useState<{
    kind: "daemon_offline" | "error" | "network";
    message: string;
  } | null>(null);

  const terms = query.trim().split(/\s+/).filter(Boolean);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setLatencyMs(null);
      setSearchError(null);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await searchAPI(query, undefined, 20, controller.signal);
        if (res.ok) {
          setResults(res.data.results);
          setLatencyMs(res.data.latency_ms);
          setSearchError(null);
          setSelectedIdx(0);
        } else {
          setResults([]);
          setLatencyMs(null);
          setSearchError({ kind: res.kind, message: res.message });
          setSelectedIdx(0);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setResults([]);
          setLatencyMs(null);
          setSearchError({
            kind: "network",
            message: err?.message || "Search request failed",
          });
          setSelectedIdx(0);
        }
      }
    }, 120);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  const handleQueryChange = useCallback((q: string) => {
    setQuery(q);
    setLatencyMs(null);
    setSelectedIdx(0);
    if (!q.trim()) {
      setResults([]);
      setSearchError(null);
    }
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, Math.max(0, results.length - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && results[selectedIdx]) {
        setPreviewResult(results[selectedIdx]);
      } else if (e.key === "Escape") {
        if (previewResult) {
          setPreviewResult(null);
          return;
        }
        if (panelOpen) {
          setPanelOpen(false);
          return;
        }
        setQuery("");
        setLatencyMs(null);
        setSearchError(null);
        setResults([]);
      }
    },
    [results, selectedIdx, panelOpen, previewResult]
  );

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === ",") {
        e.preventDefault();
        setPanelOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const handleOpenInExplorer = useCallback(async (filepath: string) => {
    await revealAPI(filepath);
  }, []);

  return (
    <>
      <SearchScreen
        query={query}
        onQueryChange={handleQueryChange}
        results={results}
        selectedIdx={selectedIdx}
        onSelectIdx={setSelectedIdx}
        latencyMs={latencyMs}
        isIndexing={false}
        searchError={searchError}
        onOpenSettings={() => setPanelOpen(true)}
        onOpenResult={(r) => setPreviewResult(r)}
        onKeyDown={handleKeyDown}
      />

      {/* Status panel */}
      {panelOpen && (
        <StatusPanel
          onClose={() => setPanelOpen(false)}
          onSelectOperator={(op) => {
            setQuery((prev) => `${prev.trim()} ${op}`.trim());
            setPanelOpen(false);
          }}
          onSelectExample={(ex) => {
            setQuery(ex);
            setPanelOpen(false);
          }}
        />
      )}

      {/* Preview panel */}
      {previewResult && (
        <PreviewPanel
          result={previewResult}
          terms={terms}
          onClose={() => setPreviewResult(null)}
          onOpenInExplorer={handleOpenInExplorer}
        />
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </>
  );
}
