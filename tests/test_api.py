from __future__ import annotations

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from semanticfs.api import app
from semanticfs.store import SearchResult

client = TestClient(app)


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "SemanticFS API"


def test_frontend_mount():
    res = client.get("/")
    assert res.status_code == 200
    # Should serve frontend index.html
    assert "html" in res.headers.get("content-type", "").lower()


def test_api_status():
    res = client.get("/status")
    assert res.status_code == 200
    data = res.json()
    assert "daemon" in data
    assert "index" in data
    assert "watched_directories" in data
    assert "diagnostics" in data


def test_api_stats():
    res = client.get("/stats")
    assert res.status_code == 200
    data = res.json()
    assert "daemon_status" in data
    assert "total_files_indexed" in data
    assert "neural_vector_model" in data
    assert "vector_db_disk_size_mb" in data


def test_api_search_offline_daemon():
    with patch("semanticfs.api.is_daemon_reachable", return_value=False):
        with patch("semanticfs.api.query_daemon_embedding", return_value=None):
            res = client.post("/search", json={"query": "test query"})
            assert res.status_code == 503
            assert "Start the daemon with 'sfind start'" in res.json()["detail"]


def test_api_search_with_mocked_daemon():
    fake_embedding = [0.1] * 384
    fake_result = SearchResult(
        id="chunk_test_123",
        filename="notes.md",
        filepath="C:/test/notes.md",
        score=0.92,
        metadata={
            "content_snippet": "Discussed semantic search benchmarks and vector indexing.",
            "file_size": 1024,
            "modified_at": 1725400000.0,
            "start_line": 5,
            "end_line": 20,
        },
        filetype=".md",
        start_line=5,
        end_line=20,
    )

    with patch("semanticfs.api.query_daemon_embedding", return_value=fake_embedding):
        with patch("semanticfs.store.VectorStore.search", return_value=[fake_result]):
            res = client.post("/search", json={"query": "benchmarks", "limit": 5})
            assert res.status_code == 200
            data = res.json()
            assert data["query"] == "benchmarks"
            assert data["total"] == 1
            assert len(data["results"]) == 1

            first = data["results"][0]
            assert first["id"] == "chunk_test_123"
            assert first["fileName"] == "notes.md"
            assert first["ext"] == "md"
            assert first["score"] == 0.92
            assert "semantic search benchmarks" in first["snippet"]
            assert len(first["citations"]) > 0
