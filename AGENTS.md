# AGENTS.md — SemanticFS

## Project

SemanticFS (`sfind`) is a local, offline semantic file-search CLI + background daemon for Windows. Python core + a currently-unused Rust crate in `native_core/`. Packaging via `pyproject.toml` (setuptools). Entry points: `sfind` (CLI, `semanticfs/cli.py`), `semanticfs` (daemon, `semanticfs/daemon.py`).

Stack: `click` (CLI), `rich` (terminal UI), `sentence-transformers` + `chromadb` (embeddings/vector store), `watchdog` (file system events), `pygetwindow` (Windows window control). Optional: `transformers`/`torch` (CLIP vision), `pytesseract`/`easyocr` (OCR), `optimum` (ONNX export), `datasets`/`accelerate` (local fine-tuning via `sfind train`).

## Current known state (read before making claims in docs)

- `native_core/` (Rust) is **not wired into the Python code** — `scan_and_chunk()` returns placeholder zero-vectors, nothing calls it. Treat as experimental/disconnected until a task explicitly integrates it via PyO3.
- `vision.py`, `ocr.py`, `onnx_embedder.py`, `trainer.py` are real, working implementations already called from `embedder.py`/`cli.py` — not stubs. Their dependencies just aren't declared in `pyproject.toml` yet (see `.agents/workflows/phase-2-scope-split.md`).
- Benchmark scripts (`tests/test_suite_100.py`, `tests/test_suite_10000_real.py`, `tests/run_drive_stress_fast.py`) are real and runnable, but their query sets are derived from the developer's own personal files/index — not portable or blind. Don't cite their output numbers as generally reproducible until `.agents/workflows/phase-1-benchmark-methodology.md` is done.
- Windows-only today (Explorer integration, Windows Clipboard, `pygetwindow`). Don't imply cross-platform support in docs unless a task explicitly adds it.

## Conventions

- Tests use `pytest`, live in `tests/`.
- CLI commands are added via `click` in `semanticfs/cli.py`; keep the existing operator syntax (`ext:`, `+term`, `-term`, `score:`) intact — it's covered by benchmark queries.
- No code documentation comment blocks unless explicitly asked for — keep code clean, use docstrings only where the project already does.
- Prefer editing `pyproject.toml`'s `[project.optional-dependencies]` over adding new top-level required dependencies.

## Deny rules (ask before doing these, don't do them autonomously)

- Don't delete or rewrite `tests/test_suite_100.py`, `tests/test_suite_10000_real.py`, or `tests/run_drive_stress_fast.py` outright — they contain real (if flawed) methodology; fix/replace deliberately per the Phase 1 workflow, don't just remove.
- Don't force-push, rewrite git history, or delete branches.
- Don't publish to PyPI or tag a release without explicit confirmation.
- Don't modify `LICENSE` content (only verify it's present/correct).
- Don't remove `native_core/` outright — either wire it in or clearly relabel it per Phase 0; deleting it is not one of the sanctioned options.

## Workflow files

Step-by-step fix plans live in `.agents/workflows/`, one file per phase (`phase-0-credibility-fixes.md` through `phase-8-perception-positioning.md`). Work through them one at a time, in the order given in each file's context — don't combine multiple phases into a single session/Task List.
