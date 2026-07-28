from __future__ import annotations

from semanticfs.store import SearchResult

def test_search_result_dataclass():
    sr = SearchResult(
        id="chunk_1",
        filename="sample.py",
        filepath="C:/Dev/SemanticFS/sample.py",
        score=0.85,
        metadata={"text": "def test(): pass"},
        filetype=".py",
        start_line=1,
        end_line=5
    )
    assert sr.filepath == "C:/Dev/SemanticFS/sample.py"
    assert sr.score == 0.85
    assert sr.filename == "sample.py"
