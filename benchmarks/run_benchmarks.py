from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.store import VectorStore
from semanticfs.chunker import chunk_file_content

BENCHMARK_DIR = Path(__file__).parent
FIXTURES_DIR = BENCHMARK_DIR / "fixtures"
EVAL_SET_PATH = BENCHMARK_DIR / "eval_set.json"
TEST_DB_PATH = BENCHMARK_DIR / "test_chroma"

def run_reproducible_benchmark():
    print("=" * 70)
    print("📊 SemanticFS Portable Benchmark Suite — Reproducibility & Latency Test")
    print("=" * 70)

    # Initialize isolated test vector store
    store = VectorStore(db_path=TEST_DB_PATH, collection_name="benchmark_eval")
    embedder = Embedder("BAAI/bge-small-en-v1.5", 512)

    # Index sample fixture files
    fixture_files = list(FIXTURES_DIR.glob("*"))
    print(f"\n📂 Indexing {len(fixture_files)} sample fixture files from {FIXTURES_DIR.name}...")
    
    total_chunks = 0
    for file_path in fixture_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            chunks = chunk_file_content(file_path, content)
            for c in chunks:
                emb = embedder.embed_text(c.text)
                store.add_chunk(
                    chunk_id=c.chunk_id,
                    filepath=str(file_path),
                    embedding=emb,
                    text=c.text,
                    metadata={"filename": file_path.name, "start_line": c.start_line, "end_line": c.end_line}
                )
                total_chunks += 1
        except Exception as e:
            print(f"Error indexing {file_path.name}: {e}")

    print(f"✔ Indexed {total_chunks} total chunks across {len(fixture_files)} files into benchmark collection.")

    # Load held-out evaluation set
    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    print(f"\n🚀 Running {len(eval_set)} evaluation queries against held-out test set...")
    print("-" * 70)

    correct_top1 = 0
    latencies_ms = []

    for item in eval_set:
        query = item["query"]
        expected_filename = item["expected_file"]

        t0 = time.perf_counter()
        q_emb = embedder.embed_text(query)
        results = store.search(q_emb, query_text=query, n_results=3, min_score_threshold=0.01)
        t1 = time.perf_counter()

        latency_ms = (t1 - t0) * 1000.0
        latencies_ms.append(latency_ms)

        matched_filenames = [Path(r.filepath).name for r in results]
        is_hit = expected_filename in matched_filenames[:1]

        if is_hit:
            correct_top1 += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        top_match = matched_filenames[0] if matched_filenames else "NONE"
        print(f"[{status}] Query: '{query[:35]:<35}' | Expected: {expected_filename} | Got: {top_match} ({latency_ms:.2f} ms)")

    latencies_ms.sort()
    n = len(latencies_ms)
    p50 = latencies_ms[int(n * 0.50)]
    p95 = latencies_ms[int(n * 0.95)] if n >= 20 else latencies_ms[-1]
    p99 = latencies_ms[int(n * 0.99)] if n >= 100 else latencies_ms[-1]
    mean_lat = sum(latencies_ms) / n
    acc_pct = (correct_top1 / n) * 100.0

    print("\n" + "=" * 70)
    print("📈 BENCHMARK RESULTS SUMMARY")
    print("=" * 70)
    print(f"• Evaluation Queries Count: {n}")
    print(f"• Test Fixtures Count:     {len(fixture_files)} files ({total_chunks} chunks)")
    print(f"• Top-1 Retrieval Accuracy: {acc_pct:.2f}% ({correct_top1}/{n})")
    print(f"• Mean Search Latency:      {mean_lat:.2f} ms")
    print(f"• Latency Distribution:    p50 = {p50:.2f} ms | p95 = {p95:.2f} ms | p99 = {p99:.2f} ms")
    print("=" * 70 + "\n")

    # Cleanup temporary test database
    import shutil
    if TEST_DB_PATH.exists():
        shutil.rmtree(TEST_DB_PATH, ignore_errors=True)

if __name__ == "__main__":
    run_reproducible_benchmark()
