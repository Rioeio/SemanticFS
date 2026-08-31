from __future__ import annotations

import fnmatch
import logging
import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

def is_path_excluded(path: Path, exclude_patterns: list[str]) -> bool:
    """Check if path matches any exclude pattern."""
    if not exclude_patterns:
        return False
    posix_path = path.as_posix()
    native_path = str(path)
    filename = path.name

    for pat in exclude_patterns:
        if fnmatch.fnmatch(filename, pat):
            return True
        if fnmatch.fnmatch(posix_path, pat) or fnmatch.fnmatch(native_path, pat):
            return True
        clean_pat = pat.replace("**/", "").replace("/**", "").strip("/")
        if clean_pat:
            for part in path.parts:
                if fnmatch.fnmatch(part, clean_pat):
                    return True
    return False

def is_path_included(path: Path, include_patterns: list[str]) -> bool:
    """Check if path matches any include pattern."""
    if not include_patterns or "*" in include_patterns:
        return True
    posix_path = path.as_posix()
    native_path = str(path)
    filename = path.name

    for pat in include_patterns:
        if fnmatch.fnmatch(filename, pat) or fnmatch.fnmatch(posix_path, pat) or fnmatch.fnmatch(native_path, pat):
            return True
    return False

def is_file_allowed(
    path: Path,
    include_patterns: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    max_file_size_bytes: int | float | None = None,
    check_size: bool = True,
) -> bool:
    """Check if a file should be indexed based on include/exclude patterns and max file size."""
    if exclude_patterns and is_path_excluded(path, exclude_patterns):
        return False
    if include_patterns and not is_path_included(path, include_patterns):
        return False
    if check_size and max_file_size_bytes is not None and max_file_size_bytes > 0:
        try:
            if path.exists() and path.is_file() and path.stat().st_size > max_file_size_bytes:
                return False
        except (OSError, ValueError):
            return False
    return True

class DebouncedEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        callback: Callable[[str, Path], None],
        debounce_seconds: float = 0.5,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        max_file_size_mb: int | float | None = None,
    ):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = exclude_patterns or []
        self.max_file_size_mb = max_file_size_mb
        self.max_file_size_bytes = (max_file_size_mb * 1024 * 1024) if max_file_size_mb is not None else None
        self.events: dict[Path, str] = {}
        self.timer: threading.Timer | None = None
        self.lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        src = event.src_path.decode("utf-8") if isinstance(event.src_path, bytes) else str(event.src_path)
        path = Path(src)

        check_size = (event.event_type != "deleted")
        if not is_file_allowed(
            path,
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            max_file_size_bytes=self.max_file_size_bytes,
            check_size=check_size,
        ):
            return

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
    def __init__(
        self,
        directories: list[Path],
        callback: Callable[[str, Path], None],
        debounce_ms: int = 500,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        max_file_size_mb: int | float | None = None,
    ):
        self.directories = directories
        self.observer = Observer()
        self.handler = DebouncedEventHandler(
            callback,
            debounce_seconds=debounce_ms / 1000.0,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_file_size_mb=max_file_size_mb,
        )

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
