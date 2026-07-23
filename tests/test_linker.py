from __future__ import annotations

import tempfile
from pathlib import Path

from semanticfs.linker import FileLinker

def test_linker():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_linker.db"
        linker = FileLinker(db_path, co_access_window_seconds=10)
        
        linker.record_access("file1")
        linker.record_access("file2")
        
        linker.compute_links()
        
        links = linker.get_links("file1")
        assert len(links) == 1
        assert links[0].target_id == "file2"
        assert links[0].weight == 1.0
