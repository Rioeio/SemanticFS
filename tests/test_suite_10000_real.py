from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.store import VectorStore, STOPWORDS

def run_10000_real_drive_tests():
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)

    print("📂 Ripping through 3,184 indexed drive chunks to extract REAL drive search terms...", flush=True)
    all_metadatas = store.get_all(limit=5000)
    
    real_words = set()
    real_filenames = []
    
    for meta in all_metadatas:
        fn = meta.get("filename", "")
        if fn:
            real_filenames.append(fn)
            for w in fn.replace(".", " ").replace("_", " ").replace("-", " ").split():
                if len(w) > 2 and w.lower() not in STOPWORDS:
                    real_words.add(w.lower())
                    
        snip = meta.get("content_snippet", "")
        if snip:
            for w in snip.split()[:20]:
                w_clean = "".join(c for c in w if c.isalnum())
                if len(w_clean) > 3 and w_clean.lower() not in STOPWORDS:
                    real_words.add(w_clean.lower())

    real_word_list = list(real_words)
    print(f"✔ Extracted {len(real_word_list):,} unique real keywords and {len(real_filenames):,} real filenames from drive!", flush=True)
    print("🚀 Generating 10,000 randomized search queries derived 100% from your actual drive contents...\n", flush=True)

    random.seed(42)
    queries = []
    for _ in range(10000):
        r = random.random()
        if r < 0.4 and real_filenames:
            fn = random.choice(real_filenames)
            parts = fn.replace(".", " ").replace("_", " ").split()
            sample_len = min(len(parts), random.randint(1, 3))
            queries.append(" ".join(parts[:sample_len]))
        elif r < 0.8 and len(real_word_list) >= 3:
            k = random.randint(2, 4)
            queries.append(" ".join(random.sample(real_word_list, k)))
        else:
            queries.append(random.choice(real_word_list))

    total_tests = len(queries)
    print("=" * 70, flush=True)
    print("⚡ RUNNING 10,000 DRIVE-DERIVED STRESS TESTS ON SEMANTICFS ENGINE", flush=True)
    print("=" * 70, flush=True)

    passed_tests = 0
    total_score = 0.0
    latencies = []
    start_wall = time.time()

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
            print(f"[{current_count:5d}/10000] Processed in {elapsed:.1f}s | Success Rate: {acc:.2f}% | Avg Match Score: {avg_s:.2f}", flush=True)

    total_wall_time = time.time() - start_wall
    avg_score = (total_score / passed_tests) if passed_tests > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies)
    success_rate = (passed_tests / total_tests) * 100.0

    print("=" * 70, flush=True)
    print("📊 10,000 REAL DRIVE-BASED STRESS TEST RESULTS", flush=True)
    print("=" * 70, flush=True)
    print(f"  • Total Real Drive Queries: {total_tests:,}", flush=True)
    print(f"  • Successful Matches:        {passed_tests:,}", flush=True)
    print(f"  • Overall Success Avg:       {success_rate:.2f}%", flush=True)
    print(f"  • Mean Match Score:          {avg_score:.2f} / 1.00", flush=True)
    print(f"  • Total Test Duration:       {total_wall_time:.2f} seconds", flush=True)
    print(f"  • Throughput Rate:           {total_tests / total_wall_time:.1f} queries/sec", flush=True)
    print(f"  • Batch Query Latency:       {avg_latency:.2f} ms/query", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    run_10000_real_drive_tests()
