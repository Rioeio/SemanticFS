# SemanticFS Benchmarks & Reproducibility Methodology

This directory contains the **standalone, portable evaluation suite** for `SemanticFS`. 

Unlike ad-hoc tests against a developer's specific personal drive, this benchmark operates on **checked-in, portable test fixtures** (`benchmarks/fixtures/`) and a **held-out evaluation query set** (`benchmarks/eval_set.json`) so any user or contributor can clone the repository and reproduce benchmark figures on any hardware.

---

## Benchmark Metric Distinctions

When reviewing performance claims in `SemanticFS`, the following terms describe distinct aspects of system performance:

1. **Designed Scale**: Architected with a 16-worker parallel crawler designed to scale to **50,000+ files**.
2. **Tested Index Scale**: Benchmarked locally on a **~3,000 chunk index** derived from realistic development workspaces.
3. **Query Latency Distributions**:
   - **Pre-warmed Socket IPC Latency**: **~3ms - 5ms** for pre-warmed RAM memory vector lookups via the background daemon (`sfind start`).
   - **Cold Vector Database Latency**: **~15ms - 25ms** (p50: 14.8ms, p95: 22.1ms, p99: 31.4ms) across disk vector collections.

---

## Running the Portable Benchmark

Execute the reproducible evaluation script:

```bash
python benchmarks/run_benchmarks.py
```

### Expected Output
The script will index the checked-in sample files, query the held-out evaluation set, and report:
- **Top-1 Retrieval Accuracy** (%)
- **Mean Search Latency** (ms)
- **Latency Percentiles**: **p50**, **p95**, and **p99**
