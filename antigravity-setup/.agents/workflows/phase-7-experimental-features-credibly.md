# Phase 7 — Doing the "experimental" features credibly (future work, don't rush)

**Objective:** For each roadmap item from Phase 2, define what "done credibly" looks like *before* building more of it — this is the step that was skipped the first time around.

Task hints (treat each as its own future objective, not one big task):
- **CLIP vision scene search**: needs its own small labeled eval set (e.g. 50 images with expected scene tags) and an accuracy number reported the same rigorous way as Phase 1's core search benchmark.
- **OCR pipeline**: needs accuracy reporting on a representative mix of clean scans vs. noisy phone-photo receipts — OCR accuracy varies enormously by input quality, and a single blended number will be misleading.
- **`sfind train` (local fine-tuning)**: this is the riskiest experimental feature — fine-tuning on personal files without a held-out eval set can silently make search *worse*. Don't ship this without a before/after eval on the Phase 1 benchmark set, and a clear rollback path if fine-tuning degrades results.
- **`sfind onnx` export**: report the actual latency/accuracy tradeoff of the quantized model vs. the full model — "we export to ONNX" isn't a benefit on its own without that comparison.
- **Git commit search / virtual drive mount / visualizer**: lower risk, mostly need basic tests and honest scope statements in docs (e.g. which git log formats are supported).

**Acceptance criteria:**
- No experimental feature gets promoted to "Core" in the README until it has the same kind of benchmark/methodology backing as Phase 1.

---
