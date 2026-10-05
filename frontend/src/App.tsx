import { useState, useEffect, useCallback } from "react";
import { SearchScreen } from "./components/search";
import { PreviewPanel } from "./components/detail";
import { StatusPanel } from "./components/status";
import { searchAPI } from "./api/client";
import type { Result } from "./types/search";

// ─── Data ───────────────────────────────────────────────────────────────────

const ALL_RESULTS: Result[] = [
  {
    id: "1", fileName: "quarterly-retrospective.md", ext: "md",
    folder: "~/Documents/Work/Q3-2026",
    snippet: "Key themes: velocity slowed due to unclear ownership of the semantic indexing pipeline. Team adopted a RACI model.",
    score: 0.94, minutesAgo: 3,
    sizeBytes: 8420, lineCount: 214,
    citations: [
      { term: "quarterly report", source: "body", confidence: 0.92, lineNo: 3 },
      { term: "semantic", source: "body", confidence: 0.88, lineNo: 47 },
      { term: "retrospective", source: "filename", confidence: 1.0 },
    ],
    fullContent: `# Q3 2026 Retrospective

**Date:** 2026-08-28  **Facilitator:** Priya Menon  **Team:** Platform

---

## What went well

- Shipped the semantic search alpha two weeks ahead of schedule.
- Embedding pipeline latency dropped from 340ms to 18ms p99 after the HNSW migration.
- On-call burden reduced by 40% following the new runbook process.

## What slowed us down

Key themes: velocity slowed due to unclear ownership of the **semantic indexing pipeline**. The quarterly report review surfaced three unresolved ownership gaps that delayed two feature launches by a combined 11 days.

Team adopted a RACI model for cross-functional features going forward. First owner assignments ship in the next sprint.

## Action items

| Owner       | Item                                  | Due       |
|-------------|---------------------------------------|-----------|
| @dan        | Draft RACI for indexing pipeline      | 2026-09-06 |
| @priya      | Review embedding model eval results   | 2026-09-10 |
| @anon       | Deprecate legacy flat-index fallback  | 2026-09-20 |

## Sentiment

Overall team mood: cautiously optimistic. Confidence in Q4 roadmap is high.`,
  },
  {
    id: "2", fileName: "interview-notes-maya.md", ext: "md",
    folder: "~/Documents/Hiring",
    snippet: "Strong semantic reasoning skills. Mentioned experience with vector search, embedding models, and local-first tooling.",
    score: 0.88, minutesAgo: 47,
    sizeBytes: 3102, lineCount: 78,
    citations: [
      { term: "semantic", source: "body", confidence: 0.88, lineNo: 12 },
      { term: "vector search", source: "body", confidence: 0.85, lineNo: 19 },
    ],
    fullContent: `# Interview Notes — Maya Osei
**Role:** Senior ML Engineer  **Date:** 2026-09-02  **Interviewer:** @anon

---

## First impression

Arrived prepared. Had already read our open-source embedding benchmarks and had specific questions about our HNSW config.

## Technical depth

Strong semantic reasoning skills throughout. Walked through her experience building a local-first document search tool at her previous company — notably, she chose to compute embeddings on-device and cited privacy as a first-class constraint, not an afterthought.

Mentioned experience with vector search (FAISS, Qdrant), embedding models (nomic, e5-large), and local-first tooling in general. Discussed trade-offs between retrieval precision and recall with confidence.

## Soft skills

Clear communicator. Answered questions directly, acknowledged gaps honestly. Asked good questions about team structure.

## Concerns

None major. Salary expectations are at the top of the band.

## Recommendation

**Strong hire.** Schedule final round with @priya.`,
  },
  {
    id: "3", fileName: "index-benchmark.py", ext: "py",
    folder: "~/Research/embeddings",
    snippet: "Compares HNSW vs flat cosine at 50k, 250k, and 1M vectors. HNSW holds <8ms p99 up to ~600k entries on M3 Pro.",
    score: 0.79, minutesAgo: 60 * 5,
    sizeBytes: 4871, lineCount: 143,
    citations: [
      { term: "semantic", source: "body", confidence: 0.74, lineNo: 8 },
      { term: "index", source: "filename", confidence: 1.0 },
    ],
    fullContent: `"""
Benchmark: HNSW vs flat cosine similarity index
Sizes: 50k, 250k, 1M vectors (dim=768)
Hardware: Apple M3 Pro, 36GB unified memory
"""

import time
import numpy as np
from typing import Literal

# Semantic embedding dimension — matches nomic-embed-text-v1.5
DIM = 768
SIZES = [50_000, 250_000, 1_000_000]
TOP_K = 10

def build_flat_index(vecs: np.ndarray):
    """Brute-force cosine index. O(n) per query."""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms

def query_flat(index, q: np.ndarray, k: int = TOP_K):
    q = q / np.linalg.norm(q)
    scores = index @ q
    return np.argpartition(scores, -k)[-k:]

def build_hnsw(vecs: np.ndarray):
    import hnswlib
    idx = hnswlib.Index(space="cosine", dim=DIM)
    idx.init_index(max_elements=len(vecs), ef_construction=200, M=16)
    idx.add_items(vecs)
    idx.set_ef(50)
    return idx

def run_benchmark(kind: Literal["flat", "hnsw"], n: int):
    vecs = np.random.rand(n, DIM).astype("float32")
    query = np.random.rand(DIM).astype("float32")

    if kind == "flat":
        idx = build_flat_index(vecs)
        t0 = time.perf_counter()
        for _ in range(100):
            query_flat(idx, query)
        return (time.perf_counter() - t0) / 100 * 1000
    else:
        idx = build_hnsw(vecs)
        t0 = time.perf_counter()
        for _ in range(100):
            idx.knn_query(query, k=TOP_K)
        return (time.perf_counter() - t0) / 100 * 1000

for n in SIZES:
    flat_ms = run_benchmark("flat", n)
    hnsw_ms = run_benchmark("hnsw", n)
    print(f"n={n:>9,}  flat={flat_ms:6.1f}ms  hnsw={hnsw_ms:6.1f}ms")`,
  },
  {
    id: "4", fileName: "design-tokens.json", ext: "json",
    folder: "~/Projects/semanticfs/src",
    snippet: "Color palette, spacing scale, and typographic tokens for the SemanticFS design system. Synced from Figma on last export.",
    score: 0.71, minutesAgo: 60 * 72,
    sizeBytes: 2240, lineCount: 61,
    citations: [
      { term: "semantic", source: "body", confidence: 0.66, lineNo: 2 },
    ],
    fullContent: `{
  "meta": {
    "name": "SemanticFS Design System",
    "version": "0.9.4",
    "exportedAt": "2026-08-31T14:22:00Z"
  },
  "color": {
    "base":          "#16161D",
    "surface":       "#1E1F29",
    "border":        "#2A2B38",
    "textPrimary":   "#F2F1ED",
    "textSecondary": "#8B8D98",
    "accent":        "#9D7CFF",
    "success":       "#7FBF6B",
    "warning":       "#E6C265",
    "danger":        "#E5637A",
    "highlight":     "#FF6FA8",
    "mono":          "#6FD3E8"
  },
  "spacing": [4, 8, 12, 16, 24, 32, 48],
  "fontSize": {
    "xs":  12,
    "sm":  14,
    "md":  16,
    "lg":  20,
    "xl":  28
  },
  "fontFamily": {
    "sans": "Inter",
    "mono": "JetBrains Mono"
  },
  "radius": {
    "sm": 4,
    "md": 6,
    "lg": 10
  }
}`,
  },
  {
    id: "5", fileName: "meeting-notes-2026-08-29.txt", ext: "txt",
    folder: "~/Documents/Work/Meetings",
    snippet: "Discussed roadmap priorities: semantic search accuracy, index freshness indicators, and the privacy trust model.",
    score: 0.67, minutesAgo: 60 * 24 * 5,
    sizeBytes: 1820, lineCount: 44,
    citations: [
      { term: "semantic", source: "body", confidence: 0.71, lineNo: 9 },
    ],
    experimental: { feature: "ocr", label: "Text extracted via OCR — scanned PDF source" },
    fullContent: `Meeting Notes — 2026-08-29
Attendees: @priya, @dan, @anon, @maya (guest)
Location: Remote / Zoom

AGENDA

1. Q4 roadmap priorities
2. Privacy model review
3. Open items

NOTES

Roadmap priorities confirmed for Q4:
- Semantic search accuracy: target 90%+ recall on the internal eval set
- Index freshness indicators: show users when results may be stale
- Privacy trust model: audit log, local-only badge, clear data flow docs

@maya raised a concern about OCR confidence scores not surfacing to users.
Team agreed: experimental features should be labeled, not hidden.
Action: @dan to add experimental warning to OCR-sourced results. Due 2026-09-10.

Privacy model review deferred to async — @priya to share draft by 2026-09-03.

OPEN ITEMS

- Flat index deprecation: still blocked on migration script (@anon)
- Daemon watchdog: intermittent restart loop on low-memory machines (tracking issue #441)`,
  },
  {
    id: "6", fileName: "embedding-model-eval.csv", ext: "csv",
    folder: "~/Research/embeddings",
    snippet: "Model comparison across MTEB tasks. nomic-embed-text-v1.5 leads on local inference speed with competitive semantic accuracy.",
    score: 0.61, minutesAgo: 60 * 24 * 12,
    sizeBytes: 3640, lineCount: 22,
    citations: [
      { term: "semantic", source: "body", confidence: 0.61, lineNo: 14 },
    ],
    experimental: { feature: "vision", label: "Indexed via Vision — image content inferred from chart/table" },
    fullContent: `model,params_m,dim,mteb_avg,local_ms_p50,local_ms_p99,size_mb,license
nomic-embed-text-v1.5,137,768,62.4,6.2,11.8,540,apache-2.0
e5-large-v2,335,1024,61.1,14.7,28.3,1340,mit
bge-m3,570,1024,63.8,22.1,41.5,2280,mit
gte-large,335,1024,61.7,15.9,31.2,1340,apache-2.0
multilingual-e5-large,560,1024,60.2,23.4,44.7,2240,mit
all-MiniLM-L6-v2,22,384,56.3,1.8,3.4,88,apache-2.0
mxbai-embed-large-v1,335,1024,64.1,16.3,32.8,1340,mit
jina-embeddings-v3,570,1024,65.3,24.6,48.1,2280,cc-by-nc-4.0
text-embedding-3-small,,-,62.3,api,api,-,commercial
text-embedding-3-large,,-,64.6,api,api,-,commercial`,
  },
  {
    id: "7", fileName: "privacy-model-draft.md", ext: "md",
    folder: "~/Projects/semanticfs/docs",
    snippet: "All embeddings are computed on-device. No file content, path, or vector ever leaves the local machine. Audit log is append-only.",
    score: 0.55, minutesAgo: 60 * 24 * 21,
    sizeBytes: 5130, lineCount: 131,
    citations: [
      { term: "semantic", source: "body", confidence: 0.55, lineNo: 22 },
      { term: "privacy", source: "filename", confidence: 1.0 },
    ],
    fullContent: `# Privacy Model

> SemanticFS is local-first. This document defines exactly what that means.

## Principles

1. **No data leaves the device** — ever. Not embeddings, not file paths, not query terms.
2. **Auditability** — every index operation is logged to \`~/.semanticfs/audit.log\`.
3. **User control** — any folder can be excluded at any time. Exclusion takes effect immediately.
4. **Transparency** — experimental features (OCR, vision indexing) are labeled clearly in results.

## What is indexed

- File content (text extraction only — binary data is skipped)
- File metadata: name, path, size, modification date
- Embeddings computed locally using nomic-embed-text-v1.5

All embeddings are computed on-device. No file content, path, or vector ever leaves the local machine. Audit log is append-only and stored at \`~/.semanticfs/audit.log\`.

## What is never collected

- File content transmitted to any server
- Query terms or search history
- Usage telemetry of any kind (not even crash reports — opt-in only)

## Experimental features

Vision and OCR indexing are opt-in. When active, they extract text from images and scanned PDFs locally using a bundled model. Results derived via these methods are labeled \`experimental\` in the UI.`,
  },
];

function filterResults(query: string): Result[] {
  if (!query.trim()) return [];
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  return ALL_RESULTS.filter((r) =>
    terms.some(
      (t) =>
        r.fileName.toLowerCase().includes(t) ||
        r.snippet.toLowerCase().includes(t) ||
        r.folder.toLowerCase().includes(t)
    )
  ).sort((a, b) => b.score - a.score);
}




export default function App() {
  const [query, setQuery] = useState("semantic");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [latencyMs, setLatencyMs] = useState<number | null>(14);
  const [panelOpen, setPanelOpen] = useState(false);
  const [previewResult, setPreviewResult] = useState<Result | null>(null);
  const [liveResults, setLiveResults] = useState<Result[] | null>(null);

  const fallbackResults = filterResults(query);
  const results = liveResults !== null ? liveResults : fallbackResults;
  const terms = query.trim().split(/\s+/).filter(Boolean);

  useEffect(() => {
    if (!query.trim()) {
      setLiveResults([]);
      setLatencyMs(0);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await searchAPI(query, undefined, 20, controller.signal);
        if (res && res.results.length > 0) {
          setLiveResults(res.results);
          setLatencyMs(res.latency_ms);
          setSelectedIdx(0);
        } else if (res && res.results.length === 0) {
          const local = filterResults(query);
          if (local.length > 0) {
            setLiveResults(null);
          } else {
            setLiveResults([]);
          }
          setLatencyMs(res.latency_ms);
          setSelectedIdx(0);
        } else {
          setLiveResults(null);
          setSelectedIdx(0);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setLiveResults(null);
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
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, results.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && results[selectedIdx]) {
        setPreviewResult(results[selectedIdx]);
      } else if (e.key === "Escape") {
        if (previewResult) { setPreviewResult(null); return; }
        if (panelOpen) { setPanelOpen(false); return; }
        setQuery("");
        setLatencyMs(null);
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

  return (
    <>
      <SearchScreen
        query={query}
        onQueryChange={handleQueryChange}
        results={results}
        selectedIdx={selectedIdx}
        onSelectIdx={setSelectedIdx}
        latencyMs={latencyMs}
        isIndexing={true}
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
