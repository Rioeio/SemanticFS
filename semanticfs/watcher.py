from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

class DebouncedEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str, Path], None], debounce_seconds: float = 0.5):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.events: dict[Path, str] = {}
        self.timer: threading.Timer | None = None
        self.lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        src = event.src_path.decode("utf-8") if isinstance(event.src_path, bytes) else str(event.src_path)
        path = Path(src)
        with self.lock:
            self.events[path] = event.event_type

            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.debounce_seconds, self.flush)
            self.timer.start()

    def flush(self) -> None:
        with self.lock:
            events_to_process = self.events.copy()
            self.events.clear()

        for path, event_type in events_to_process.items():
            try:
                self.callback(event_type, path)
            except Exception as e:
                logger.error(f"Error processing event for {path}: {e}")

class FileWatcher:
    """Watches the file system for changes."""
    def __init__(self, directories: list[Path], callback: Callable[[str, Path], None], debounce_ms: int = 500):
        self.directories = directories
        self.observer = Observer()
        self.handler = DebouncedEventHandler(callback, debounce_seconds=debounce_ms / 1000.0)

    def start(self) -> None:
        """Start watching directories."""
        for d in self.directories:
            if d.exists() and d.is_dir():
                self.observer.schedule(self.handler, str(d), recursive=True)
                logger.info(f"Watching directory: {d}")
            else:
                logger.warning(f"Directory not found: {d}")
        self.observer.start()

    def stop(self) -> None:
        """Stop watching."""
        self.observer.stop()
        self.observer.join()
