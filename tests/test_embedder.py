from __future__ import annotations

from semanticfs.embedder import Embedder

def test_embed_text():
    embedder = Embedder()
    vector = embedder.embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384  # MiniLM dimension
    assert isinstance(vector[0], float)

def test_embed_batch():
    embedder = Embedder()
    vectors = embedder.embed_batch(["hello", "world"])
    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert len(vectors[0]) == 384
