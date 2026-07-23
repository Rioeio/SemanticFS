from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class Link:
    source_id: str
    target_id: str
    weight: float

@dataclass
class Node:
    id: str

@dataclass
class Edge:
    source: str
    target: str
    weight: float

class FileLinker:
    """Implicit file association engine using SQLite with fallback WAL mode and concurrency timeouts."""
    def __init__(self, db_path: Path, co_access_window_seconds: int = 300, min_link_weight: float = 1.0):
        self.db_path = db_path
        self.co_access_window_seconds = co_access_window_seconds
        self.min_link_weight = min_link_weight
        
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        """Create sqlite connection with 30s timeout and safe WAL fallback."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        return conn

    def _init_db(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS links (
                        source_id TEXT,
                        target_id TEXT,
                        weight REAL,
                        last_seen TEXT,
                        PRIMARY KEY(source_id, target_id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS access_log (
                        file_id TEXT,
                        timestamp TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.debug(f"_init_db error: {e}")

    def record_access(self, file_id: str) -> None:
        """Log a file access."""
        now = datetime.now().isoformat()
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO access_log (file_id, timestamp) VALUES (?, ?)', (file_id, now))
                conn.commit()
        except Exception as e:
            logger.debug(f"record_access error: {e}")

    def compute_links(self) -> None:
        """Find files accessed within co_access_window_seconds of each other."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT file_id, timestamp FROM access_log ORDER BY timestamp ASC')
                logs = cursor.fetchall()

                new_links = []
                for i, (f1, t1_str) in enumerate(logs):
                    t1 = datetime.fromisoformat(t1_str)
                    for j in range(i + 1, len(logs)):
                        f2, t2_str = logs[j]
                        if f1 == f2:
                            continue
                        t2 = datetime.fromisoformat(t2_str)
                        if (t2 - t1).total_seconds() <= self.co_access_window_seconds:
                            new_links.append((f1, f2))
                            new_links.append((f2, f1))
                        else:
                            break

                now = datetime.now().isoformat()
                for source, target in new_links:
                    cursor.execute('''
                        INSERT INTO links (source_id, target_id, weight, last_seen)
                        VALUES (?, ?, 1.0, ?)
                        ON CONFLICT(source_id, target_id) DO UPDATE SET
                        weight = weight + 1.0, last_seen = ?
                    ''', (source, target, now, now))
                
                cursor.execute('DELETE FROM access_log')
                conn.commit()
        except Exception as e:
            logger.debug(f"compute_links error: {e}")

    def get_links(self, file_id: str) -> list[Link]:
        """Get all links for a file."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT source_id, target_id, weight FROM links WHERE source_id = ? AND weight >= ?', 
                               (file_id, self.min_link_weight))
                rows = cursor.fetchall()
                return [Link(source_id=r[0], target_id=r[1], weight=r[2]) for r in rows]
        except Exception as e:
            logger.debug(f"get_links error: {e}")
            return []

    def get_access_count(self) -> int:
        """Count total logged file accesses."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM access_log')
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception:
            return 0

    def get_total_links(self) -> int:
        """Count total co-access association links formed."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM links')
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception:
            return 0

    def get_graph(self) -> tuple[list[Node], list[Edge]]:
        """Get full graph nodes and edges."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT source_id, target_id, weight FROM links WHERE weight >= ?', (self.min_link_weight,))
                rows = cursor.fetchall()

                edges = []
                node_ids = set()
                for r in rows:
                    source, target, weight = r
                    edges.append(Edge(source=source, target=target, weight=weight))
                    node_ids.add(source)
                    node_ids.add(target)

                nodes = [Node(id=n) for n in node_ids]
                return nodes, edges
        except Exception as e:
            logger.debug(f"get_graph error: {e}")
            return [], []
