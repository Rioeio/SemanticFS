from __future__ import annotations

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from semanticfs.config import Config, WatcherConfig, DEFAULT_WATCH_DIRS
from semanticfs.daemon import DaemonContext
from semanticfs.store import VectorStore
from semanticfs.watcher import (
    DebouncedEventHandler,
    FileWatcher,
    is_file_allowed,
    is_path_excluded,
    is_path_included,
)


def test_default_config_watch_directories_and_watcher_settings():
    """Verify default watch_directories and watcher config settings match specifications."""
    Config._instance = None
    cfg = Config._load()

    # Check watch directories match the expected specific folders
    expected_subdirs = ["Documents", "Desktop", "Downloads", "Pictures", "Videos", "Music", "Dev"]
    actual_subdirs = [p.name for p in cfg.watcher.watch_directories]
    for expected in expected_subdirs:
        assert expected in actual_subdirs

    # Check include_patterns, exclude_patterns, and max_file_size_mb
    assert "*.py" in cfg.watcher.include_patterns
    assert "*.md" in cfg.watcher.include_patterns
    assert "**/node_modules/**" in cfg.watcher.exclude_patterns
    assert "**/.*/**" in cfg.watcher.exclude_patterns
    assert cfg.watcher.max_file_size_mb == 50
    assert cfg.watcher.max_file_size == 50 * 1024 * 1024


def test_custom_config_loading(tmp_path: Path):
    """Verify Config._load correctly parses custom include/exclude patterns and max_file_size_mb."""
    custom_yaml = tmp_path / "custom.yaml"
    custom_yaml.write_text(
        yaml.dump({
            "watch_directories": [str(tmp_path / "custom_watch")],
            "include_patterns": ["*.py", "*.rs"],
            "exclude_patterns": ["**/build/**", "*.cache"],
            "watcher": {
                "max_file_size_mb": 15,
                "debounce_ms": 250,
            }
        }),
        encoding="utf-8"
    )

    cfg = Config._load(custom_yaml)
    assert len(cfg.watcher.watch_directories) == 1
    assert cfg.watcher.watch_directories[0] == tmp_path / "custom_watch"
    assert cfg.watcher.include_patterns == ["*.py", "*.rs"]
    assert cfg.watcher.exclude_patterns == ["**/build/**", "*.cache"]
    assert cfg.watcher.max_file_size_mb == 15
    assert cfg.watcher.max_file_size == 15 * 1024 * 1024
    assert cfg.watcher.debounce_ms == 250


def test_pattern_matching_helpers():
    """Test is_path_included, is_path_excluded, and is_file_allowed helpers."""
    inc = ["*.py", "*.ts", "*.md"]
    exc = ["**/.*/**", "**/node_modules/**", "**/__pycache__/**", "*.tmp", ".git*"]

    # Included & not excluded
    assert is_path_included(Path("C:/code/main.py"), inc) is True
    assert is_path_excluded(Path("C:/code/main.py"), exc) is False
    assert is_file_allowed(Path("C:/code/main.py"), inc, exc) is True

    # Excluded by node_modules
    assert is_path_excluded(Path("C:/code/node_modules/pkg/index.ts"), exc) is True
    assert is_file_allowed(Path("C:/code/node_modules/pkg/index.ts"), inc, exc) is False

    # Excluded by hidden folder
    assert is_path_excluded(Path("C:/code/.git/config"), exc) is True
    assert is_file_allowed(Path("C:/code/.git/config"), inc, exc) is False

    # Excluded by extension
    assert is_path_excluded(Path("C:/code/temp.tmp"), exc) is True
    assert is_file_allowed(Path("C:/code/temp.tmp"), inc, exc) is False

    # Excluded by not matching include_patterns
    assert is_path_included(Path("C:/code/data.unknown"), inc) is False
    assert is_file_allowed(Path("C:/code/data.unknown"), inc, exc) is False


def test_file_size_filtering(tmp_path: Path):
    """Test that is_file_allowed respects max_file_size_bytes."""
    small_file = tmp_path / "small.txt"
    small_file.write_text("hello small file", encoding="utf-8")

    big_file = tmp_path / "big.txt"
    big_file.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB

    inc = ["*.txt"]
    exc = []
    max_bytes = 1 * 1024 * 1024  # 1 MB limit

    assert is_file_allowed(small_file, inc, exc, max_file_size_bytes=max_bytes) is True
    assert is_file_allowed(big_file, inc, exc, max_file_size_bytes=max_bytes) is False


def test_debounced_event_handler_filtering(tmp_path: Path):
    """Test DebouncedEventHandler drops excluded, non-matching, and oversized files on events."""
    callback = MagicMock()
    handler = DebouncedEventHandler(
        callback=callback,
        debounce_seconds=0.05,
        include_patterns=["*.py", "*.md"],
        exclude_patterns=["**/node_modules/**", "*.tmp"],
        max_file_size_mb=1,  # 1 MB
    )

    class MockEvent:
        def __init__(self, src_path: str, event_type: str = "modified", is_directory: bool = False):
            self.src_path = src_path
            self.event_type = event_type
            self.is_directory = is_directory

    # 1. Allowed file
    good_file = tmp_path / "app.py"
    good_file.write_text("print('hello')", encoding="utf-8")
    handler.on_any_event(MockEvent(str(good_file), "modified"))

    # 2. Excluded by pattern (node_modules)
    nm_file = tmp_path / "node_modules" / "mod.py"
    nm_file.parent.mkdir(parents=True, exist_ok=True)
    nm_file.write_text("print('nm')", encoding="utf-8")
    handler.on_any_event(MockEvent(str(nm_file), "modified"))

    # 3. Excluded by extension pattern (*.tmp)
    tmp_file = tmp_path / "test.tmp"
    tmp_file.write_text("temp", encoding="utf-8")
    handler.on_any_event(MockEvent(str(tmp_file), "modified"))

    # 4. Non-matching include pattern (*.bin)
    bin_file = tmp_path / "data.bin"
    bin_file.write_bytes(b"\x00\x01")
    handler.on_any_event(MockEvent(str(bin_file), "modified"))

    # 5. Oversized file (> 1 MB)
    oversized = tmp_path / "large.py"
    oversized.write_bytes(b"#" * (2 * 1024 * 1024))
    handler.on_any_event(MockEvent(str(oversized), "modified"))

    # Wait for debounce flush
    time.sleep(0.15)

    # Only good_file should have triggered callback
    assert callback.call_count == 1
    call_args = callback.call_args_list[0][0]
    assert call_args[0] == "modified"
    assert call_args[1] == good_file


def test_initial_scan_skips_excluded_and_oversized_files(tmp_path: Path):
    """Test daemon initial_scan skips non-matching, excluded, and oversized files."""
    watch_dir = tmp_path / "workspace"
    watch_dir.mkdir()

    # Valid files
    f_py = watch_dir / "script.py"
    f_py.write_text("import sys", encoding="utf-8")
    f_md = watch_dir / "notes.md"
    f_md.write_text("# Notes", encoding="utf-8")

    # Excluded directories and files
    nm_dir = watch_dir / "node_modules" / "pkg"
    nm_dir.mkdir(parents=True)
    f_nm = nm_dir / "index.js"
    f_nm.write_text("module.exports = {}", encoding="utf-8")

    git_dir = watch_dir / ".git"
    git_dir.mkdir(parents=True)
    f_git = git_dir / "config"
    f_git.write_text("[core]", encoding="utf-8")

    # Excluded extension
    f_tmp = watch_dir / "cache.tmp"
    f_tmp.write_text("temp", encoding="utf-8")

    # Non-matching include pattern
    f_raw = watch_dir / "binary.raw"
    f_raw.write_bytes(b"\x12\x34")

    # Oversized file (> 1 MB)
    f_big = watch_dir / "huge.py"
    f_big.write_bytes(b"#" * (2 * 1024 * 1024))

    # Setup config
    cfg = Config()
    cfg.watcher.watch_directories = [watch_dir]
    cfg.watcher.include_patterns = ["*.py", "*.md", "*.js"]
    cfg.watcher.exclude_patterns = ["**/node_modules/**", "**/.*/**", "*.tmp"]
    cfg.watcher.max_file_size_mb = 1
    cfg.watcher.max_file_size = 1 * 1024 * 1024

    indexed_files: list[Path] = []
    daemon = DaemonContext(cfg)
    daemon.index_file = MagicMock(side_effect=lambda fp: indexed_files.append(fp))

    daemon.initial_scan()

    # Verify only script.py and notes.md were indexed
    assert len(indexed_files) == 2
    assert f_py in indexed_files
    assert f_md in indexed_files
    assert f_nm not in indexed_files
    assert f_git not in indexed_files
    assert f_tmp not in indexed_files
    assert f_raw not in indexed_files
    assert f_big not in indexed_files


def test_initial_scan_thread_pool_worker_count_and_torch_threads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify initial_scan sets dynamic worker count based on os.cpu_count() and initializes torch threads."""
    import os
    from unittest.mock import patch
    from semanticfs.daemon import _worker_init

    # Test _worker_init sets torch thread count
    with patch("torch.set_num_threads") as mock_set_num_threads:
        _worker_init()
        mock_set_num_threads.assert_called_once_with(1)

    watch_dir = tmp_path / "workspace"
    watch_dir.mkdir()
    (watch_dir / "sample.py").write_text("x = 1", encoding="utf-8")

    cfg = Config()
    cfg.watcher.watch_directories = [watch_dir]
    daemon = DaemonContext(cfg)
    daemon.index_file = MagicMock()

    # Simulate CPU count = 16 (should cap at 8)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    with patch("semanticfs.daemon.ThreadPoolExecutor") as mock_executor_cls:
        mock_executor = MagicMock()
        mock_executor_cls.return_value.__enter__.return_value = mock_executor
        daemon.initial_scan()
        mock_executor_cls.assert_called_once_with(max_workers=8, initializer=_worker_init)

    # Simulate CPU count = 1 (should floor at 2)
    monkeypatch.setattr(os, "cpu_count", lambda: 1)
    with patch("semanticfs.daemon.ThreadPoolExecutor") as mock_executor_cls:
        mock_executor = MagicMock()
        mock_executor_cls.return_value.__enter__.return_value = mock_executor
        daemon.initial_scan()
        mock_executor_cls.assert_called_once_with(max_workers=2, initializer=_worker_init)


def test_initial_scan_incremental_skips_unchanged_files(tmp_path: Path):
    """Verify initial_scan compares file mtime against stored modified_at metadata and skips re-embedding unchanged files."""
    watch_dir = tmp_path / "workspace"
    watch_dir.mkdir()

    f1 = watch_dir / "file1.py"
    f1.write_text("print('hello')", encoding="utf-8")
    f2 = watch_dir / "file2.py"
    f2.write_text("print('world')", encoding="utf-8")

    cfg = Config()
    cfg.storage.db_path = tmp_path / "chroma_db"
    cfg.watcher.watch_directories = [watch_dir]
    cfg.watcher.include_patterns = ["*.py"]
    cfg.watcher.exclude_patterns = []

    daemon = DaemonContext(cfg)

    indexed_files: list[Path] = []
    f1_id = VectorStore.generate_id(f1)
    f2_id = VectorStore.generate_id(f2)

    # First run: f1 is already stored with matching mtime, f2 is not in store
    daemon.store.get_metadata = MagicMock(side_effect=lambda fid: {
        f1_id: {"modified_at": f1.stat().st_mtime, "filename": "file1.py"},
    }.get(fid))

    daemon.index_file = MagicMock(side_effect=lambda fp: indexed_files.append(fp))
    daemon.initial_scan()

    # f1 should be skipped as unchanged, f2 should be indexed
    assert len(indexed_files) == 1
    assert indexed_files == [f2]

    # Second run: f1 mtime changed, f2 is now up to date in store
    indexed_files.clear()
    daemon.store.get_metadata = MagicMock(side_effect=lambda fid: {
        f1_id: {"modified_at": f1.stat().st_mtime - 100.0, "filename": "file1.py"},
        f2_id: {"modified_at": f2.stat().st_mtime, "filename": "file2.py"},
    }.get(fid))

    daemon.initial_scan()
    # f1 should be indexed because its mtime changed; f2 should be skipped because unchanged
    assert len(indexed_files) == 1
    assert indexed_files == [f1]


