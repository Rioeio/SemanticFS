# AGENTS.md — SemanticFS

## Project

SemanticFS (`sfind`) is a local, offline semantic file-search CLI + background daemon for Windows. Python core + a currently-unused Rust crate in `native_core/`. Packaging via `pyproject.toml` (setuptools). Entry points: `sfind` (CLI, `semanticfs/cli.py`), `semanticfs` (daemon, `semanticfs/daemon.py`).

Stack: `click` (CLI), `rich` (terminal UI), `sentence-transformers` + `chromadb` (embeddings/vector store), `watchdog` (file system events), `pygetwindow` (Windows window control). Optional: `transformers`/`torch` (CLIP vision), `pytesseract`/`easyocr` (OCR), `optimum` (ONNX export), `datasets`/`accelerate` (local fine-tuning via `sfind train`).

## Current known state (read before making claims in docs)

Phases 0–8 are done and merged. Phase 9 (audit follow-up) is not — read it before touching CI, the README's OS claims, or the benchmark eval set.

- `native_core/` (Rust) is correctly labeled experimental in the README and badge — still not wired into Python (`scan_and_chunk()` still returns placeholder zero-vectors). That's fine as-is; don't silently claim it's integrated, and don't remove it.
- `vision.py`, `ocr.py`, `onnx_embedder.py`, `trainer.py` are real implementations with their dependencies now correctly declared as optional extras (`vision`, `ocr`, `onnx`, `train`) in `pyproject.toml`.
- `benchmarks/` (fixtures + `eval_set.json` + `run_benchmarks.py`) is a real, portable, held-out benchmark — a genuine improvement over the old personal-data-derived scripts (`tests/test_suite_100.py` etc., still present but no longer the credibility source). Known gap: only 10 queries, too small for the p95/p99 logic to produce real percentiles — see Phase 9.
- **CI is not trustworthy yet**: `ruff` runs with `--exit-zero` (always passes) and only 3 of the test files run in `pytest`. Don't treat a green CI badge as meaning the full suite/lint actually passed until Phase 9 fixes this.
- README claims "Linux/macOS (Supported)" but the code has zero OS branching and still calls `os.startfile()`/`explorer.exe` directly, and `pygetwindow` isn't even a declared dependency. This claim is currently false — see Phase 9 before repeating or building on it.

## Conventions

- Tests use `pytest`, live in `tests/`.
- CLI commands are added via `click` in `semanticfs/cli.py`; keep the existing operator syntax (`ext:`, `+term`, `-term`, `score:`) intact — it's covered by benchmark queries.
- No code documentation comment blocks unless explicitly asked for — keep code clean, use docstrings only where the project already does.
- Prefer editing `pyproject.toml`'s `[project.optional-dependencies]` over adding new top-level required dependencies.

## Deny rules (ask before doing these, don't do them autonomously)

- Don't delete or rewrite `tests/test_suite_100.py`, `tests/test_suite_10000_real.py`, or `tests/run_drive_stress_fast.py` outright — superseded by `benchmarks/` as the credibility source, but keep them unless a task explicitly says to remove them.
- Don't force-push, rewrite git history, or delete branches.
- Don't publish to PyPI or tag a release without explicit confirmation.
- Don't modify `LICENSE` content (only verify it's present/correct).
- Don't remove `native_core/` outright — either wire it in or keep it clearly relabeled; deleting it is not a sanctioned option.
- Don't fix a CI or benchmark check by weakening it further (e.g. adding more `--exit-zero`-style flags, shrinking test scope, or excluding failing tests) — fix the underlying issue.

## Workflow files

Step-by-step fix plans live in `.agents/workflows/`, one file per phase (`phase-0-credibility-fixes.md` through `phase-9-post-implementation-fixes.md`). Work through them one at a time, in the order given in each file's context — don't combine multiple phases into a single session/Task List.
