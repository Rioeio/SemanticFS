from __future__ import annotations

import json
import logging
import os
import signal
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rich.logging import RichHandler

from semanticfs.config import Config
from semanticfs.context import ContextCapture
from semanticfs.embedder import Embedder
from semanticfs.linker import FileLinker
from semanticfs.store import VectorStore
from semanticfs.watcher import FileWatcher, is_file_allowed, is_path_excluded

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("semanticfs")

AUTH_TOKEN_PATH = Path("~/.semanticfs/auth_token").expanduser()
PID_DIR = Path("~/.semanticfs").expanduser()
DAEMON_PID_FILE = PID_DIR / "daemon.pid"

def get_or_create_auth_token() -> str:
    """Generate or retrieve a secure shared-secret auth token saved with 0o600 permissions."""
    AUTH_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    if AUTH_TOKEN_PATH.exists():
        try:
            with open(AUTH_TOKEN_PATH, "r", encoding="utf-8") as f:
                token = f.read().strip()
                if token:
                    return token
        except Exception:
            pass
    import secrets
    token = secrets.token_hex(32)
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = 0o600
        fd = os.open(AUTH_TOKEN_PATH, flags, mode)
        with open(fd, "w", encoding="utf-8") as f:
            f.write(token)
    except Exception:
        with open(AUTH_TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(token)
    return token

def _worker_init() -> None:
    """Initialize worker thread environment and configure PyTorch thread limits."""
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass


class DaemonContext:
    def __init__(self, config: Config):
        self.config = config
        self.embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)
        self.store = VectorStore(config.storage.db_path, config.storage.collection_name)
        self.context_capture = ContextCapture() if config.context.enabled else None
        self.linker = FileLinker(
            config.linker.db_path,
            config.linker.co_access_window_seconds,
            config.linker.min_link_weight
        )
        self.watcher: FileWatcher | None = None
        self._running = True
        self.auth_token = get_or_create_auth_token()

    def start_ipc_server(self, port: int = 9876):
        """Pre-warmed background IPC socket server for instant search embeddings with token authentication."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("127.0.0.1", port))
            server.listen(10)
            logger.info(f"Instant Search IPC Server listening on 127.0.0.1:{port}")
        except Exception as e:
            logger.debug(f"IPC socket bind error: {e}")
            return

        def handle_client(conn):
            try:
                conn.settimeout(2.5)
                data = conn.recv(8192).decode("utf-8")
                if data:
                    req = json.loads(data)
                    token = req.get("token", "")
                    if token != self.auth_token:
                        conn.sendall(json.dumps({"error": "Unauthorized: Invalid auth token"}).encode("utf-8"))
                        return
                    query = req.get("query", "")
                    if query:
                        emb = self.embedder.embed_text(query)
                        conn.sendall(json.dumps({"embedding": emb}).encode("utf-8"))
            except Exception:
                pass
            finally:
                conn.close()

        def listen_loop():
            while self._running:
                try:
                    conn, _ = server.accept()
                    t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
                    t.start()
                except Exception:
                    break
            server.close()

        t = threading.Thread(target=listen_loop, daemon=True)
        t.start()

    def index_file(self, filepath: Path) -> None:
        """Index a single file with dynamic semantic chunking."""
        try:
            chunks = self.embedder.extract_chunks(filepath)
            ctx_snapshot = self.context_capture.capture() if self.context_capture else None

            file_stat = filepath.stat() if filepath.exists() else None
            file_size = file_stat.st_size if file_stat else 0
            mtime = file_stat.st_mtime if file_stat else time.time()

            chunk_texts = [c.text for c in chunks]
            embeddings = self.embedder.embed_batch(chunk_texts)

            parent_id = VectorStore.generate_id(filepath)

            for chunk, emb in zip(chunks, embeddings):
                metadata = {
                    "filename": filepath.name,
                    "filepath": str(filepath.absolute()),
                    "filetype": filepath.suffix.lower(),
                    "file_size": file_size,
                    "created_at": time.time(),
                    "modified_at": mtime,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": len(chunks),
                    "context_window": ctx_snapshot.active_window if ctx_snapshot else "",
                    "content_snippet": chunk.text[:300].replace('\n', ' ')
                }

                chunk_file_id = f"{parent_id}#chunk_{chunk.chunk_index}"
                self.store.upsert(chunk_file_id, emb, metadata)

            self.linker.record_access(parent_id)
        except Exception as e:
            logger.debug(f"Failed to index {filepath}: {e}")

    def on_file_event(self, event_type: str, filepath: Path) -> None:
        max_bytes = getattr(self.config.watcher, "max_file_size", None)
        if max_bytes is None:
            max_mb = getattr(self.config.watcher, "max_file_size_mb", 50)
            max_bytes = max_mb * 1024 * 1024

        if not is_file_allowed(
            filepath,
            include_patterns=self.config.watcher.include_patterns,
            exclude_patterns=self.config.watcher.exclude_patterns,
            max_file_size_bytes=max_bytes,
            check_size=(event_type != "deleted"),
        ):
            return

        if event_type in ("created", "modified"):
            logger.info(f"Processing {event_type}: {filepath}")
            self.index_file(filepath)

        elif event_type == "deleted":
            logger.info(f"Processing deleted: {filepath}")
            parent_id = VectorStore.generate_id(filepath)
            self.store.delete(parent_id)

    def initial_scan(self) -> None:
        logger.info("Starting multi-threaded high-throughput directory scan with dynamic semantic chunking...")
        include_patterns = self.config.watcher.include_patterns
        exclude_patterns = self.config.watcher.exclude_patterns
        max_bytes = getattr(self.config.watcher, "max_file_size", None)
        if max_bytes is None:
            max_mb = getattr(self.config.watcher, "max_file_size_mb", 50)
            max_bytes = max_mb * 1024 * 1024

        file_queue: list[Path] = []
        skipped_unchanged = 0
        for watch_dir in self.config.watcher.watch_directories:
            if not watch_dir.exists():
                logger.warning(f"Watch directory does not exist: {watch_dir}")
                continue

            logger.info(f"Collecting files from directory tree: {watch_dir}")
            for root, dirs, files in os.walk(watch_dir):
                dirs[:] = [
                    dr for dr in dirs
                    if not dr.startswith('.') and not is_path_excluded(Path(root) / dr, exclude_patterns)
                ]
                for file in files:
                    if file.startswith('.'):
                        continue
                    filepath = Path(root) / file
                    if is_file_allowed(filepath, include_patterns, exclude_patterns, max_bytes, check_size=True):
                        # Incremental indexing: skip re-embedding if file is unchanged
                        try:
                            file_id = VectorStore.generate_id(filepath)
                            stored_meta = self.store.get_metadata(file_id)
                            if stored_meta and "modified_at" in stored_meta:
                                current_mtime = filepath.stat().st_mtime
                                stored_mtime = float(stored_meta["modified_at"])
                                if abs(current_mtime - stored_mtime) < 1e-4:
                                    skipped_unchanged += 1
                                    continue
                        except Exception as e:
                            logger.debug(f"Metadata lookup error for {filepath}: {e}")

                        file_queue.append(filepath)

        if skipped_unchanged > 0:
            logger.info(f"Incremental scan: skipped {skipped_unchanged:,} unchanged files.")

        max_workers = max(2, min(os.cpu_count() or 4, 8))
        logger.info(f"Dispatched {len(file_queue):,} files to {max_workers}-worker thread pool for parallel indexing...")
        with ThreadPoolExecutor(max_workers=max_workers, initializer=_worker_init) as executor:
            list(executor.map(self.index_file, file_queue))

        logger.info(f"Initial scan complete. {len(file_queue):,} files dynamically chunked and indexed.")

    def run(self) -> None:
        logger.info("SemanticFS Daemon initializing...")
        PID_DIR.mkdir(parents=True, exist_ok=True)
        try:
            DAEMON_PID_FILE.write_text(str(os.getpid()))
        except Exception as e:
            logger.debug(f"Could not write PID file: {e}")

        self.start_ipc_server()
        from semanticfs.ui_server import start_ui_server
        start_ui_server(port=9877)
        threading.Thread(target=self.initial_scan, daemon=True).start()

        max_mb = getattr(self.config.watcher, "max_file_size_mb", None)
        if max_mb is None:
            max_bytes = getattr(self.config.watcher, "max_file_size", 50 * 1024 * 1024)
            max_mb = max_bytes // (1024 * 1024)

        self.watcher = FileWatcher(
            directories=self.config.watcher.watch_directories,
            callback=self.on_file_event,
            debounce_ms=self.config.watcher.debounce_ms,
            include_patterns=self.config.watcher.include_patterns,
            exclude_patterns=self.config.watcher.exclude_patterns,
            max_file_size_mb=max_mb,
        )
        self.watcher.start()
        logger.info("FileWatcher started. Listening for ambient file events...")

        def signal_handler(sig, frame):
            logger.info("Shutting down daemon...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while self._running:
            time.sleep(1.0)

    def stop(self) -> None:
        self._running = False
        try:
            DAEMON_PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        if self.watcher:
            self.watcher.stop()
        logger.info("Daemon stopped.")

def main():
    config = Config.get_instance()
    daemon_ctx = DaemonContext(config)
    daemon_ctx.run()

if __name__ == "__main__":
    main()
