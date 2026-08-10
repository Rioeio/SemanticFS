# Phase 1 — Benchmark methodology & reproducibility

**Objective:** The benchmark scripts already exist (`tests/test_suite_100.py`, `tests/test_suite_10000_real.py`, `tests/run_drive_stress_fast.py`) and are real, not fabricated — but the query methodology has a specific problem that likely inflates the reported numbers. Fix the methodology, move these into a proper `/benchmarks` directory, and make the numbers reproducible by someone who isn't you.

Task hints:
- **The core problem:** `test_suite_100.py`'s query list includes queries built directly from your own filenames and identity (e.g. `"resume cv Manoj Chetty"`, `"CS3303A assignment Manoj Chetty"`) — hand-written to match files you already knew existed. `test_suite_10000_real.py` goes further and *auto-generates* its queries by sampling words out of the same index it then searches against (`"Ripping through 3,184 indexed drive chunks to extract REAL drive search terms"`). Both approaches make the task easier than the real use case ("I don't remember the filename") and make the numbers non-reproducible by anyone without your exact drive contents. This is worth fixing before anything else in this phase.
- Build a **held-out, portable eval set**: a small folder of synthetic/sample files (checked into `benchmarks/fixtures/`) with queries written *before* looking at what's in the folder, or written by someone other than the one who created the test files. This is what makes a number defensible.
- Reconcile the README's "1,000 Real Drive-Derived Stress Test" against what the code actually runs — the real index in the test was ~3,184 chunks, not clearly 1,000 distinct queries. Pick the accurate number and state it precisely (query count, file count, and index size are three different numbers — don't conflate them).
- Soften "50,000+ files" — the code is architected to scale there (16-worker parallel scan), but the actual tested/benchmarked index was ~3,184 chunks. Say "designed to scale to 50,000+ files; benchmarked at ~3,000" rather than implying the benchmark numbers were measured at that scale.
- Move the (fixed) scripts into `benchmarks/`, add a `benchmarks/README.md` explaining the methodology plainly, including that these are self-reported numbers — that honesty reads better than unqualified claims.
- Add latency percentiles (p50/p95/p99), not just the mean — a single mean hides tail latency that matters more in practice.
- Scrub personal identifiers (full name, course codes) from the query set once it's rebuilt as a portable fixture — solves this and the Phase 0 privacy note at once.

**Acceptance criteria:**
- Query set for the core benchmark is not derived from the same personal files/index it's tested against.
- A stranger can clone the repo, run one command against the checked-in fixtures, and reproduce numbers in the same ballpark as the README.
- File count, chunk count, and query count are reported as distinct, correctly labeled numbers.
- Latency is reported as a distribution (p50/p95/p99), not just a single mean or best-case number.

---
