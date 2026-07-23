from __future__ import annotations

import tempfile
from pathlib import Path

from semanticfs.store import VectorStore

def test_store_cycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir)
        store = VectorStore(db_path)
        
        file_id = "test_id"
        embedding = [0.1] * 384
        metadata = {"filename": "test.txt", "filetype": ".txt"}
        
        store.upsert(file_id, embedding, metadata)
        
        fetched = store.get(file_id)
        assert fetched is not None
        assert fetched["filename"] == "test.txt"
        
        # Test search
        results = store.search([0.1] * 384, n_results=1)
        assert len(results) == 1
        assert results[0].id == file_id
        
        store.delete(file_id)
        assert store.get(file_id) is None
