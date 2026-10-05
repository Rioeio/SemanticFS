from __future__ import annotations

import json
import logging
import os
import platform
import socket
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from semanticfs.config import Config
from semanticfs.doctor import (
    get_cargo_path,
    get_tesseract_path,
    is_daemon_reachable,
    is_startup_daemon_installed,
)
from semanticfs.linker import FileLinker
from semanticfs.store import VectorStore

logger = logging.getLogger("semanticfs.api")

DAEMON_IPC_PORT = 9876
DAEMON_PID_FILE = Path("~/.semanticfs/daemon.pid").expanduser()
AUTH_TOKEN_PATH = Path("~/.semanticfs/auth_token").expanduser()

app = FastAPI(
    title="SemanticFS API",
    description="Minimal HTTP API bridging SemanticFS daemon/vector store with frontend UI.",
    version="0.9.4",
)

# Enable CORS for React frontend (Vite dev server, local origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── IPC Client Helper ────────────────────────────────────────────────────────


def get_auth_token() -> str:
    """Retrieve shared secret auth token for daemon IPC."""
    if AUTH_TOKEN_PATH.exists():
        try:
            return AUTH_TOKEN_PATH.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return ""


def query_daemon_embedding(query: str, port: int = DAEMON_IPC_PORT, timeout: float = 3.0) -> list[float] | None:
    """
    Fetch pre-warmed vector embedding from running daemon over IPC socket.
    Does NOT load or duplicate the model inside this API process.
    """
    token = get_auth_token()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(("127.0.0.1", port))
        payload = json.dumps({"query": query, "token": token}).encode("utf-8")
        sock.sendall(payload)

        data = b""
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
        sock.close()

        res = json.loads(data.decode("utf-8"))
        return res.get("embedding")
    except Exception as e:
        logger.debug(f"IPC embedding query error: {e}")
        return None


def is_pid_running(pid: int) -> bool:
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        return False


def get_dir_size_mb(path: Path) -> float:
    """Calculate total size of directory in megabytes matching cli.py."""
    if not path.exists():
        return 0.0
    total = 0
    try:
        for p in path.iterdir():
            if p.is_file():
                total += p.stat().st_size
            elif p.is_dir():
                for subp in p.iterdir():
                    if subp.is_file():
                        total += subp.stat().st_size
        return round(total / (1024 * 1024), 2)
    except Exception:
        return 0.0


# ─── Request / Response Models ────────────────────────────────────────────────


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query or operator expression")
    filters: dict[str, Any] | None = Field(default=None, description="Metadata filters (e.g. {'filetype': '.py'})")
    limit: int = Field(default=10, ge=1, le=100, description="Max number of search results to return")


class CitationItem(BaseModel):
    term: str
    source: str = "body"
    confidence: float = 0.9
    lineNo: int | None = None


class SearchResultItem(BaseModel):
    id: str
    fileName: str
    ext: str
    folder: str
    snippet: str
    score: float
    minutesAgo: int
    sizeBytes: int
    lineCount: int
    citations: list[CitationItem] = []
    fullContent: str = ""
    # Raw compatibility fields
    filepath: str
    filetype: str
    start_line: int
    end_line: int
    metadata: dict[str, Any] = {}


class SearchResponse(BaseModel):
    query: str
    total: int
    latency_ms: float
    results: list[SearchResultItem]


# ─── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "SemanticFS API",
        "version": "0.9.4",
        "daemon_reachable": is_daemon_reachable(DAEMON_IPC_PORT),
    }


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    """
    Search indexed files using semantic embeddings.
    Queries the running daemon over 127.0.0.1:9876 for fast pre-warmed embeddings.
    """
    start_time = time.perf_counter()

    if not req.query.strip():
        return SearchResponse(query="", total=0, latency_ms=0.0, results=[])

    # 1. Talk to running daemon over IPC socket (no model reloading)
    embedding = query_daemon_embedding(req.query.strip())
    if embedding is None:
        daemon_online = is_daemon_reachable(DAEMON_IPC_PORT)
        if not daemon_online:
            raise HTTPException(
                status_code=503,
                detail=(
                    "SemanticFS daemon is not running on 127.0.0.1:9876. "
                    "Start the daemon with 'sfind start' to enable fast embeddings."
                ),
            )
        else:
            raise HTTPException(
                status_code=502,
                detail="Daemon IPC connection failed or returned an empty embedding.",
            )

    # 2. Call vector store search with retrieved embedding
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)

    try:
        raw_results = store.search(
            query_embedding=embedding,
            query_text=req.query,
            n_results=req.limit,
            filters=req.filters,
        )
    except Exception as e:
        logger.error(f"Vector store search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    # 3. Format results into rich schema required by React UI
    now = time.time()
    formatted: list[SearchResultItem] = []
    query_tokens = [t.lower() for t in req.query.split() if len(t) > 2]

    for r in raw_results:
        p = Path(r.filepath)
        meta = r.metadata or {}

        # Safe file stats and preview snippet
        size_bytes = int(meta.get("file_size", 0))
        mod_time = float(meta.get("modified_at", now))
        minutes_ago = max(0, int((now - mod_time) / 60))
        ext = r.filetype.lstrip(".").lower() if r.filetype else (p.suffix.lstrip(".").lower() if p.suffix else "")

        snippet = meta.get("content_snippet", "")
        full_content = ""
        line_count = max(1, r.end_line - r.start_line + 1)

        if p.exists() and p.is_file():
            try:
                if size_bytes == 0:
                    size_bytes = p.stat().st_size
                # Read text previews if file is reasonably sized (<256 KB)
                if size_bytes < 256 * 1024 and p.suffix.lower() not in (
                    ".exe", ".dll", ".bin", ".db", ".sqlite", ".zip", ".tar", ".gz", ".png", ".jpg", ".pdf"
                ):
                    with open(p, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        full_content = "".join(lines[:400])
                        if not snippet and lines:
                            s_idx = max(0, r.start_line - 1)
                            e_idx = max(s_idx + 1, min(len(lines), r.end_line))
                            snippet = "".join(lines[s_idx:e_idx]).strip()
            except Exception:
                pass

        if not snippet:
            snippet = f"{r.filename} match with score {round(r.score, 2)}"

        # Generate citations for matched query terms
        citations: list[CitationItem] = []
        for token in query_tokens[:3]:
            if token in r.filename.lower():
                citations.append(CitationItem(term=token, source="filename", confidence=1.0))
            elif token in snippet.lower():
                citations.append(CitationItem(term=token, source="body", confidence=0.88, lineNo=r.start_line))

        formatted.append(
            SearchResultItem(
                id=r.id,
                fileName=r.filename,
                ext=ext,
                folder=str(p.parent),
                snippet=snippet,
                score=round(float(r.score), 4),
                minutesAgo=minutes_ago,
                sizeBytes=size_bytes,
                lineCount=line_count,
                citations=citations,
                fullContent=full_content,
                filepath=r.filepath,
                filetype=r.filetype,
                start_line=r.start_line,
                end_line=r.end_line,
                metadata=meta,
            )
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return SearchResponse(
        query=req.query,
        total=len(formatted),
        latency_ms=latency_ms,
        results=formatted,
    )


@app.get("/status")
def get_status() -> dict[str, Any]:
    """
    Returns daemon and index status, file counts, and watched directories.
    Reuses checks from doctor.py and active configuration.
    """
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)

    daemon_reachable = is_daemon_reachable(DAEMON_IPC_PORT)
    startup_installed = is_startup_daemon_installed()

    # Watched directories metadata
    watched_dirs: list[dict[str, Any]] = []

    for wdir in config.watcher.watch_directories:
        exists = wdir.exists()
        count = 0
        if exists:
            try:
                # Fast shallow count of direct children
                count = sum(1 for _ in wdir.iterdir())
            except Exception:
                pass
        watched_dirs.append({
            "path": str(wdir),
            "name": wdir.name,
            "exists": exists,
            "shallow_file_count": count,
        })

    indexed_count = 0
    try:
        indexed_count = store.count()
    except Exception:
        pass

    return {
        "daemon": {
            "status": "RUNNING" if daemon_reachable else "OFFLINE",
            "reachable": daemon_reachable,
            "port": DAEMON_IPC_PORT,
            "startup_installed": startup_installed,
        },
        "index": {
            "indexed_count": indexed_count,
            "storage_path": str(config.storage.db_path),
            "collection_name": config.storage.collection_name,
            "model_name": config.embedding.model_name,
        },
        "watched_directories": watched_dirs,
        "diagnostics": {
            "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "tesseract_available": bool(get_tesseract_path()),
            "cargo_available": bool(get_cargo_path()),
        },
    }


@app.get("/stats")
def get_stats() -> dict[str, Any]:
    """
    Reports all master index and telemetry statistics identical to 'sfind stats'.
    """
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    linker = FileLinker(config.linker.db_path)

    d_reachable = is_daemon_reachable(DAEMON_IPC_PORT)
    pid: int | None = None
    if DAEMON_PID_FILE.exists():
        try:
            val = int(DAEMON_PID_FILE.read_text().strip())
            if is_pid_running(val):
                pid = val
        except Exception:
            pass

    file_count = 0
    try:
        file_count = store.count()
    except Exception:
        pass

    access_count = 0
    total_links = 0
    try:
        access_count = linker.get_access_count()
        total_links = linker.get_total_links()
    except Exception:
        pass

    db_size_mb = get_dir_size_mb(config.storage.db_path)

    return {
        "daemon_status": "RUNNING" if d_reachable else "STOPPED",
        "daemon_reachable": d_reachable,
        "daemon_pid": pid,
        "daemon_port": DAEMON_IPC_PORT,
        "total_files_indexed": file_count,
        "vector_embeddings_stored": file_count,
        "neural_vector_model": config.embedding.model_name,
        "multimodal_vision_model": "openai/clip-vit-base-patch32",
        "vector_db_disk_size_mb": db_size_mb,
        "file_accesses_logged": access_count,
        "co_access_links_formed": total_links,
        "monitored_directories_count": len(config.watcher.watch_directories),
        "monitored_directories": [str(d) for d in config.watcher.watch_directories],
    }


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def root_fallback() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "SemanticFS API",
            "version": "0.9.4",
            "frontend": "not built (run 'pnpm --dir frontend build')",
            "daemon_reachable": is_daemon_reachable(DAEMON_IPC_PORT),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("semanticfs.api:app", host="127.0.0.1", port=8000, reload=True)
