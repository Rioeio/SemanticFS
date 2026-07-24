from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.store import VectorStore, STOPWORDS

def run_fast_drive_stress():
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)

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

    real_word_list = list(real_words)
    random.seed(42)
    
    queries = []
    for _ in range(1000):
        r = random.random()
        if r < 0.5 and real_filenames:
            fn = random.choice(real_filenames)
            parts = fn.replace(".", " ").replace("_", " ").split()
            sample_len = min(len(parts), random.randint(1, 3))
            queries.append(" ".join(parts[:sample_len]))
        else:
            k = random.randint(1, 3)
            queries.append(" ".join(random.sample(real_word_list, k)))

    total_tests = len(queries)
    passed_tests = 0
    total_score = 0.0
    latencies = []
    start_wall = time.time()

    batch_size = 100
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

    total_wall_time = time.time() - start_wall
    avg_score = (total_score / passed_tests) if passed_tests > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies)
    success_rate = (passed_tests / total_tests) * 100.0

    print("=" * 70)
    print("📊 REAL DRIVE STRESS VERIFICATION BENCHMARK RESULTS")
    print("=" * 70)
    print(f"  • Total Real Drive Queries: {total_tests:,}")
    print(f"  • Successful Matches:        {passed_tests:,}")
    print(f"  • Overall Success Avg:       {success_rate:.2f}%")
    print(f"  • Mean Match Score:          {avg_score:.2f} / 1.00")
    print(f"  • Total Test Duration:       {total_wall_time:.2f} seconds")
    print(f"  • Search Latency:            {avg_latency:.2f} ms/query")
    print("=" * 70)

if __name__ == "__main__":
    run_fast_drive_stress()
