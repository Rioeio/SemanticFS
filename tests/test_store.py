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
        
        # Test get_metadata lookup
        meta = store.get_metadata(file_id)
        assert meta is not None
        assert meta["filename"] == "test.txt"

        # Test chunk_0 lookup via parent id
        parent_id = "parent_doc"
        store.upsert(f"{parent_id}#chunk_0", embedding, {"filename": "chunked.txt", "modified_at": 12345.0})
        chunk_meta = store.get_metadata(parent_id)
        assert chunk_meta is not None
        assert chunk_meta["filename"] == "chunked.txt"
        assert chunk_meta["modified_at"] == 12345.0

        # Non-existent metadata returns None
        assert store.get_metadata("non_existent_id") is None

        store.delete(file_id)
        assert store.get(file_id) is None
        assert store.get_metadata(file_id) is None
        store.close()
