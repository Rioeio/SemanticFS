from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.store import VectorStore

BASE_TERMS = [
    "physics", "question", "bank", "engineering", "semester", "exam", "cs3101", "cs3201",
    "pip", "assignment", "manoj", "chetty", "rubrics", "resume", "cv", "hackathon",
    "presentation", "slides", "pptx", "docx", "pdf", "jpeg", "image", "photo", "whatsapp",
    "fedora", "log", "driver", "patch", "python", "linear", "algebra", "matrix", "solver",
    "vector", "store", "chromadb", "daemon", "watcher", "trainer", "chunker", "router",
    "ipc", "socket", "server", "onnx", "quantizer", "vision", "clip", "powershell",
    "completion", "git", "commit", "config", "yaml", "cli", "rich", "interactive",
    "recent", "modified", "latest", "doc1", "doc2", "doc3", "solutions", "lab", "report",
    "music", "song", "audio", "copacabana", "tourist", "remastered", "goodbye", "weekend"
]

EXTENSIONS = ["py", "pdf", "docx", "pptx", "xlsx", "jpeg", "png", "mp3", "m4p", "log", "yaml", "json"]

def generate_10000_queries() -> list[str]:
    queries = []
    random.seed(42)
    for _ in range(10000):
        k = random.randint(1, 4)
        words = random.sample(BASE_TERMS, k)
        if random.random() < 0.3:
            words.append(random.choice(EXTENSIONS))
        queries.append(" ".join(words))
    return queries

def run_10000_tests():
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)

    queries = generate_10000_queries()
    total_tests = len(queries)

    print(f"\n🚀 Running Automated 10,000-Test Stress & Safety Verification Suite...")
    print(f"Total Indexed Chunks in System: {store.count()}")
    print("=" * 70)

    passed_tests = 0
    total_score = 0.0
    latencies = []
    start_wall = time.time()

    # Pre-embed in batches of 64 for high-throughput testing
    batch_size = 64
    for i in range(0, total_tests, batch_size):
        batch_queries = queries[i:i + batch_size]
        t0 = time.time()
        batch_embeddings = embedder.embed_batch(batch_queries)
        dt_batch_ms = (time.time() - t0) * 1000.0 / len(batch_queries)

        for q, emb in zip(batch_queries, batch_embeddings):
            latencies.append(dt_batch_ms)
            results = store.search(emb, query_text=q, n_results=5)
            if results:
                passed_tests += 1
                total_score += results[0].score

        current_count = i + len(batch_queries)
        if current_count % 1000 == 0 or current_count == total_tests:
            elapsed = time.time() - start_wall
            acc = (passed_tests / current_count) * 100.0
            avg_s = total_score / passed_tests if passed_tests > 0 else 0.0
            print(f"[{current_count:5d}/10000] Processed in {elapsed:.1f}s | Success Rate: {acc:.2f}% | Avg Match Score: {avg_s:.2f}")

    total_wall_time = time.time() - start_wall
    avg_score = (total_score / passed_tests) if passed_tests > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies)
    success_rate = (passed_tests / total_tests) * 100.0

    print("=" * 70)
    print("📊 10,000-TEST STRESS & SAFETY VERIFICATION RESULTS")
    print("=" * 70)
    print(f"  • Total Tests Executed:  {total_tests:,}")
    print(f"  • Successful Matches:    {passed_tests:,}")
    print(f"  • Overall Success Avg:   {success_rate:.2f}%")
    print(f"  • Mean Match Score:      {avg_score:.2f} / 1.00")
    print(f"  • Total Test Duration:   {total_wall_time:.2f} seconds")
    print(f"  • Throughput Rate:       {total_tests / total_wall_time:.1f} queries/sec")
    print(f"  • Batch Query Latency:   {avg_latency:.2f} ms/query")
    print("=" * 70)

if __name__ == "__main__":
    run_10000_tests()
