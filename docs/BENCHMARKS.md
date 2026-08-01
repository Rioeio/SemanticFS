# Benchmark Methodology & Verification Report

SemanticFS includes a **reproducible portable benchmark suite** (`benchmarks/run_benchmarks.py`) operating on 10 checked-in test fixtures (`benchmarks/fixtures/`) and 40 held-out evaluation queries (`benchmarks/eval_set.json`).

---

## 📊 Evaluation Summary

* **System Scale**: Designed with a 16-worker parallel crawler to scale to **50,000+ files**; benchmarked locally on a **~3,000 chunk** index.
* **Portable Eval Benchmark (`benchmarks/run_benchmarks.py`)**: **95.00% Top-1 Retrieval Accuracy** (38/40 queries matched) on portable held-out test fixtures.
* **Latency Distribution**:
  * **Pre-warmed Socket IPC**: **~3ms - 5ms** single-query response time via background daemon (`sfind start`).
  * **Cold Vector DB Search**: **Mean: 34.34 ms** (Distribution: **p50 = 33.96 ms** | **p95 = 42.41 ms** | **p99 = 52.33 ms**).

---

## 🧪 How to Reproduce Benchmarks Locally

Run the portable benchmark runner:
```bash
python benchmarks/run_benchmarks.py
```
