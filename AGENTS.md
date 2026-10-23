# AGENTS.md — SemanticFS

## Project Overview

SemanticFS (`sfind`) is an ambient, local-first semantic search engine and retrieval interface for files and documents on Windows. It replaces rigid folder hierarchies with vector-based semantic retrieval, temporal co-access linking, and instant explorer navigation.

- **Canonical Version**: `0.1.0` (declared in `pyproject.toml` and propagated to `semanticfs/api.py`, `frontend/package.json`, and `README.md`).
- **Core Package**: `semanticfs` (`semanticfs/cli.py`, `semanticfs/daemon.py`, `semanticfs/store.py`, `semanticfs/embedder.py`, `semanticfs/api.py`).
- **Web UI**: `frontend/` (React 19, TypeScript, Tailwind CSS v4, `@fontsource-variable/inter`, `@fontsource-variable/jetbrains-mono`, Vite).

## Key Architecture & Components

1. **Ambient Background Daemon (`semanticfs/daemon.py`)**:
   - Listens on `127.0.0.1:9876` for IPC queries.
   - Pre-warms neural embedding model (`BAAI/bge-small-en-v1.5`) in memory for sub-5ms embedding inference.
   - Protected with token-based authentication (`~/.semanticfs/auth_token`).
   - Monitors filesystem events via `watchdog` and maintains vector index.

2. **Vector Store & Association Engine**:
   - ChromaDB persistent storage at `~/.semanticfs/chromadb/`.
   - File linker SQLite database at `~/.semanticfs/links.db` tracking temporal co-access.

3. **HTTP API Server (`semanticfs/api.py`)**:
   - FastAPI HTTP bridge for the React UI.
   - Strictly locked down via `CORSMiddleware` (allowing only `http://127.0.0.1:8000`, `http://localhost:8000`, `http://127.0.0.1:5173`, `http://localhost:5173` with `allow_credentials=False`) and `TrustedHostMiddleware` (allowing only `127.0.0.1` and `localhost`).
   - Endpoints: `GET /health`, `POST /search`, `POST /reveal`, `GET /status`, `GET /stats`, `GET /`, and `GET /assets/{path}`.
   - Serves frontend static build when present, or returns graceful fallback json when not built.

4. **React Frontend (`frontend/`)**:
   - Fully self-hosted fonts (`@fontsource-variable/inter`, `@fontsource-variable/jetbrains-mono`).
   - Zero external CDN dependencies or tracking telemetry.
   - Real-time search with discriminated status handling (`daemon_offline` with `sfind start` hint, `error`, `no results`).
   - Live backend status panel polling `/status` and `/stats` every 5 seconds.

## CLI & Entry Points

- `sfind <query>`: Command-line semantic search with rich ranking table and interactive selection.
- `sfind start`: Launch the background ambient daemon.
- `sfind stop`: Terminate the running background daemon.
- `sfind ui`: Launch the React web UI on `http://127.0.0.1:8000` (use `--dev` for Vite dev server on `:5173`).
- `sfind graph`: Launch the standalone Web Node Graph Dashboard on `http://127.0.0.1:9877/ui`.
- `sfind stats`: Terminal display of indexing and daemon telemetry.
- `sfind doctor`: Diagnostic environment and dependency check.

## Verification & Quality Gates

- **Backend Tests**: `pytest tests/ -v` (includes `test_api.py`, `test_store.py`, `test_embedder.py`, `test_linker.py`, etc.).
- **Frontend Type Check**: `pnpm --dir frontend exec tsc --noEmit`
- **Frontend Build**: `pnpm --dir frontend build`
- **Launchers**: `scripts/launch_ui.ps1` and `scripts/launch_ui.bat` auto-check dependencies and trigger frontend builds if `dist/` is missing.
