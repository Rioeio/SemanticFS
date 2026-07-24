from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    id: str
    filename: str
    filepath: str
    score: float
    metadata: dict[str, Any]
    filetype: str

class VectorStore:
    """Wraps ChromaDB for storing file embeddings and metadata with lazy client connection."""
    def __init__(self, db_path: Path, collection_name: str = "file_embeddings"):
        self.db_path = db_path
        self.collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None

    def _get_collection(self):
        """Lazy load ChromaDB client and collection."""
        if self._client is None or self._collection is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(self.db_path))
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
        return self._collection

    @staticmethod
    def generate_id(filepath: Path) -> str:
        return hashlib.sha256(str(filepath.absolute()).encode("utf-8")).hexdigest()

    def upsert(self, file_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Add or update a file in the store."""
        safe_metadata = {k: v for k, v in metadata.items() if isinstance(v, (str, int, float, bool))}
        try:
            coll = self._get_collection()
            coll.upsert(
                ids=[file_id],
                embeddings=[embedding],
                metadatas=[safe_metadata]
            )
        except Exception as e:
            logger.debug(f"upsert error: {e}")

    def delete(self, file_id: str) -> None:
        """Remove a file from the store."""
        try:
            coll = self._get_collection()
            coll.delete(ids=[file_id])
        except Exception as e:
            logger.debug(f"delete error: {e}")

    def search(self, query_embedding: list[float], query_text: str = "", n_results: int = 20, filters: dict[str, Any] | None = None) -> list[SearchResult]:
        """Semantic search with hybrid keyword boosting for filename & path matches."""
        try:
            coll = self._get_collection()
            fetch_limit = max(n_results * 3, 50)
            results = coll.query(
                query_embeddings=[query_embedding],
                n_results=fetch_limit,
                where=filters
            )
        except Exception as e:
            logger.error(f"search error: {e}")
            return []
        
        search_results = []
        query_words = [w.lower() for w in query_text.split() if len(w) > 1]

        if results and results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                file_id = results['ids'][0][i]
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0.0
                
                score = max(0.0, 1.0 - distance)
                
                filename_lower = metadata.get("filename", "").lower()
                filepath_lower = metadata.get("filepath", "").lower()
                
                if query_words:
                    for word in query_words:
                        if word in filename_lower:
                            score += 0.45
                        elif word in filepath_lower:
                            score += 0.20
                
                score = min(1.0, score)
                
                search_results.append(SearchResult(
                    id=file_id,
                    filename=metadata.get("filename", ""),
                    filepath=metadata.get("filepath", ""),
                    score=score,
                    metadata=metadata,
                    filetype=metadata.get("filetype", "")
                ))

        search_results.sort(key=lambda r: r.score, reverse=True)
        return search_results[:n_results]

    def get(self, file_id: str) -> dict[str, Any] | None:
        """Get single file metadata."""
        try:
            coll = self._get_collection()
            results = coll.get(ids=[file_id])
            if results and results['ids']:
                return results['metadatas'][0] if results['metadatas'] else None
        except Exception as e:
            logger.debug(f"get error: {e}")
        return None

    def get_all(self, limit: int = 1000) -> list[dict[str, Any]]:
        """Get multiple files."""
        try:
            coll = self._get_collection()
            results = coll.get(limit=limit)
            return results['metadatas'] if results and results['metadatas'] else []
        except Exception as e:
            logger.debug(f"get_all error: {e}")
            return []

    def get_all_with_ids(self, limit: int = 1000) -> list[tuple[str, dict[str, Any]]]:
        """Get multiple files with their IDs."""
        try:
            coll = self._get_collection()
            results = coll.get(limit=limit)
            items = []
            if results and results['ids'] and results['metadatas']:
                for i in range(len(results['ids'])):
                    items.append((results['ids'][i], results['metadatas'][i]))
            return items
        except Exception as e:
            logger.debug(f"get_all_with_ids error: {e}")
            return []

    def clear(self) -> None:
        """Clear all entries in collection."""
        try:
            coll = self._get_collection()
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
        except Exception as e:
            logger.error(f"clear error: {e}")

    def count(self) -> int:
        """Count files in store using ultra-fast direct SQLite query if available."""
        sqlite_file = self.db_path / "chroma.sqlite3"
        if sqlite_file.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_file, timeout=2.0)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM embeddings')
                row = cursor.fetchone()
                conn.close()
                if row:
                    return row[0]
            except Exception:
                pass

        try:
            coll = self._get_collection()
            return coll.count()
        except Exception as e:
            logger.debug(f"count error: {e}")
            return 0
