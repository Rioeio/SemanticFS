# Changelog

All notable changes to the **SemanticFS** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-07-28

### Added
- **Core Vector Search**: Integrated `BAAI/bge-small-en-v1.5` dense neural embedding model with embedded `ChromaDB`.
- **Pre-Warmed Socket IPC**: Pre-warmed IPC socket server on `127.0.0.1:9876` (`sfind start`) delivering sub-5ms query latency.
- **AST & Header Chunker**: `semanticfs/ast_chunker.py` for Python function (`def`)/class (`class`) and Markdown `#` header boundaries.
- **Virtual Smart Collections**: Zero disk modification shortcut folders inside `~/.semanticfs/virtual_drive/` (`sfind collection`).
- **Structured Query Parser**: Support for inline operators (`ext:`, `file:`, `in:`, `tag:`, `+must`, `-exclude`, `score:`).
- **Environment Diagnostics**: Added `sfind doctor` diagnostic dashboard for environment and dependency verification.
- **Complete Data Purge**: Added `sfind purge` for full storage reset.
- **Portable Benchmark Suite**: Added `benchmarks/run_benchmarks.py` with portable test fixtures and p50/p95/p99 latency distribution reporting.
- **3D ASCII Neural Visualizer**: Added interactive 3D Movable "Bad Apple!!" ASCII raycasting visualizer (`sfind model`).
- **Optional Dependency Extras**: Added `[vision]`, `[ocr]`, `[onnx]`, `[train]`, and `[all]` extras in `pyproject.toml`.
- **Automated CI Pipeline**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) for automated pytest and benchmark runs.

### Changed
- Refactored `config/default.yaml` and `semanticfs/config.py` to resolve user home directories (`~`) dynamically across operating systems.
- Restructured `README.md` to separate Core Product features from Roadmap/Experimental extras.
