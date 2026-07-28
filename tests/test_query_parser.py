from __future__ import annotations

from semanticfs.query_parser import parse_structured_query

def test_parse_structured_query():
    raw_q = "neural network ext:py file:model in:src tag:notes +learning -draft score:0.45"
    parsed = parse_structured_query(raw_q)
    
    assert ".py" in parsed.extensions
    assert "model" in parsed.filename_contains
    assert "src" in parsed.folder_contains
    assert parsed.tag_query == "notes"
    assert "learning" in parsed.must_include
    assert "draft" in parsed.must_exclude
    assert parsed.min_score == 0.45
    assert "neural network" in parsed.semantic_text
