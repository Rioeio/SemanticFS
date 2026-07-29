from __future__ import annotations

import tempfile
import sys
from pathlib import Path

from semanticfs.store import VectorStore

def test_store_cycle():
    kwargs = {"ignore_cleanup_errors": True} if sys.version_info >= (3, 10) else {}
    with tempfile.TemporaryDirectory(**kwargs) as tmpdir:
        db_path = Path(tmpdir)
        store = VectorStore(db_path)
        
        file_id = "test_id"
        embedding = [0.1] * 384
        metadata = {"filepath": str(db_path / "test.txt"), "filename": "test.txt", "filetype": ".txt"}
        
        store.upsert(file_id, embedding, metadata)
        
        fetched = store.get(file_id)
        assert fetched is not None
        assert fetched["filename"] == "test.txt"
        
        # Test search
        results = store.search([0.1] * 384, query_text="test", n_results=1, min_score_threshold=0.0)
        assert len(results) == 1
        assert results[0].id == file_id
        
        store.delete(file_id)
        assert store.get(file_id) is None
