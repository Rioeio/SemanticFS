from __future__ import annotations

import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

import click
from rich.logging import RichHandler

from semanticfs.config import Config
from semanticfs.context import ContextCapture
from semanticfs.embedder import Embedder
from semanticfs.linker import FileLinker
from semanticfs.store import VectorStore
from semanticfs.watcher import FileWatcher

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("semanticfs")

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

    def on_file_event(self, event_type: str, filepath: Path) -> None:
        if event_type in ("created", "modified"):
            # Skip hidden files or system paths
            if any(part.startswith('.') or part in ('AppData', 'node_modules', '__pycache__', 'venv') for part in filepath.parts):
                return

            logger.info(f"Processing {event_type}: {filepath}")
            try:
                # 1. Capture context
                context_text = ""
                ctx_snapshot = None
                if self.context_capture:
                    ctx_snapshot = self.context_capture.capture()
                    context_text = ctx_snapshot.to_text()

                # 2. Generate embedding
                content_embedding = self.embedder.embed_file(filepath)
                
                # 3. Read snippet safely
                snippet = ""
                try:
                    if filepath.exists() and filepath.suffix.lower() in ('.txt', '.md', '.py', '.js', '.json', '.yaml'):
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            snippet = f.read(200).replace('\n', ' ')
                except Exception:
                    pass

                # 4. Upsert to VectorStore
                file_id = VectorStore.generate_id(filepath)
                
                file_size = 0
                if filepath.exists():
                    file_size = filepath.stat().st_size
                
                metadata = {
                    "filename": filepath.name,
                    "filepath": str(filepath.absolute()),
                    "filetype": filepath.suffix.lower(),
                    "file_size": file_size,
                    "created_at": time.time(),
                    "modified_at": time.time(),
                    "context_window": ctx_snapshot.active_window if ctx_snapshot else "",
                    "context_processes": ",".join(ctx_snapshot.running_processes) if ctx_snapshot else "",
                    "context_time_bucket": ctx_snapshot.time_bucket if ctx_snapshot else "",
                    "content_snippet": snippet
                }
                
                self.store.upsert(file_id, content_embedding, metadata)
                
                # 5. Record access
                self.linker.record_access(file_id)
            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")

        elif event_type == "deleted":
            logger.info(f"Processing deleted: {filepath}")
            file_id = VectorStore.generate_id(filepath)
            self.store.delete(file_id)

    def compute_links_loop(self):
        while self._running:
            time.sleep(60)
            self.linker.compute_links()

    def initial_scan(self):
        logger.info("Starting initial scan of watched user directories...")
        ignored_names = {'AppData', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', 'target', 'site-packages'}
        allowed_exts = {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".js", ".ts", ".tsx", ".jsx", ".c", ".cpp", ".h", ".java", ".rs", ".go", ".pdf", ".docx", ".sql", ".ipynb"}
        
        for d in self.config.watcher.watch_directories:
            if not d.exists() or not d.is_dir():
                continue
            for root, dirs, files in os.walk(d):
                # Prune ignored directories in-place to avoid walking into dot-directories
                dirs[:] = [dr for dr in dirs if not dr.startswith('.') and dr not in ignored_names]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    filepath = Path(root) / file
                    if filepath.suffix.lower() in allowed_exts:
                        self.on_file_event("created", filepath)
        logger.info("Initial scan complete.")

    def start(self):
        logger.info(r"""
   _____                           _   _      ______  _____ 
  / ____|                         | | (_)    |  ____|/ ____|
 | (___   ___ _ __ ___   __ _ _ __| |_ _  ___| |__  | (___  
  \___ \ / _ \ '_ ` _ \ / _` | '__| __| |/ __|  __|  \___ \ 
  ____) |  __/ | | | | | (_| | |  | |_| | (__| |     ____) |
 |_____/ \___|_| |_| |_|\__,_|_|   \__|_|\___|_|    |_____/ 
        """)
        logger.info("Starting SemanticFS Daemon...")
        
        self.initial_scan()
        
        self.watcher = FileWatcher(self.config.watcher.watch_directories, self.on_file_event)
        self.watcher.start()
        
        threading.Thread(target=self.compute_links_loop, daemon=True).start()

    def stop(self):
        logger.info("Stopping SemanticFS Daemon...")
        self._running = False
        if self.watcher:
            self.watcher.stop()

@click.command()
@click.option("--watch", multiple=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--config", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def main(watch: tuple[Path], config: Path | None):
    cfg = Config.get_instance(config)
    if watch:
        cfg.watcher.watch_directories.extend(watch)

    daemon = DaemonContext(cfg)
    
    def handle_sigint(sig, frame):
        daemon.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)
    
    daemon.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()

if __name__ == "__main__":
    main()
