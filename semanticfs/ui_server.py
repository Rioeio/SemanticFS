from __future__ import annotations

import http.server
import json
import logging
import os
import socketserver
import threading
import urllib.parse
from pathlib import Path
from typing import Any

from semanticfs.config import Config
from semanticfs.store import VectorStore

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SemanticFS — Interactive Vector Neural Graph</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(18, 26, 43, 0.75);
            --border: rgba(255, 255, 255, 0.1);
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.35);
            --cyan: #06b6d4;
            --pink: #ec4899;
            --text: #f8fafc;
            --text-dim: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 28px;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            z-index: 10;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .search-box {
            position: relative;
            width: 420px;
        }

        .search-box input {
            width: 100%;
            padding: 10px 18px;
            border-radius: 99px;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }

        .search-box input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 16px var(--accent-glow);
            background: rgba(255, 255, 255, 0.08);
        }

        .stats-badge {
            display: flex;
            gap: 16px;
            font-size: 0.85rem;
            color: var(--text-dim);
        }

        .stats-badge span {
            background: rgba(255, 255, 255, 0.05);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid var(--border);
        }

        #app-container {
            flex: 1;
            display: flex;
            position: relative;
        }

        #graph-canvas {
            flex: 1;
            height: 100%;
        }

        .sidebar {
            width: 380px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border-left: 1px solid var(--border);
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            z-index: 5;
        }

        .card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
        }

        .card-title {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--cyan);
            margin-bottom: 12px;
        }

        .result-item {
            padding: 10px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .result-item:hover {
            background: rgba(99, 102, 241, 0.15);
            border-color: var(--accent);
        }

        .result-name {
            font-weight: 600;
            color: #e2e8f0;
            font-size: 0.9rem;
        }

        .result-path {
            font-size: 0.75rem;
            color: var(--text-dim);
            margin-top: 2px;
            word-break: break-all;
        }

        .node circle {
            stroke: #fff;
            stroke-width: 1.5px;
            transition: r 0.2s, fill 0.2s;
        }

        .node:hover circle {
            r: 10px;
            fill: #ec4899;
        }

        .link {
            stroke: rgba(255, 255, 255, 0.15);
            stroke-opacity: 0.6;
        }

        .node text {
            fill: #94a3b8;
            font-size: 10px;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            SemanticFS Neural Graph
        </div>
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Search neural embeddings (e.g., 'invoice pdf', 'linear solver')...">
        </div>
        <div class="stats-badge">
            <span id="stat-files">Files: --</span>
            <span id="stat-links">Co-Access Links: --</span>
        </div>
    </header>

    <div id="app-container">
        <div id="graph-canvas"></div>
        <div class="sidebar">
            <div class="card">
                <div class="card-title">Selected Node Details</div>
                <div id="node-details">
                    <p style="color: var(--text-dim); font-size: 0.85rem;">Click or hover any graph node to inspect metadata and content snippets.</p>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Top Search Matches</div>
                <div id="search-results">
                    <p style="color: var(--text-dim); font-size: 0.85rem;">Type a search query above to filter files in real-time.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let graphData = { nodes: [], links: [] };

        async function fetchGraphData() {
            try {
                const res = await fetch('/api/graph');
                graphData = await res.json();
                document.getElementById('stat-files').textContent = `Files: ${graphData.nodes.length}`;
                document.getElementById('stat-links').textContent = `Co-Access Links: ${graphData.links.length}`;
                renderGraph(graphData);
            } catch (err) {
                console.error("Failed to load graph:", err);
            }
        }

        function renderGraph(data) {
            const container = document.getElementById('graph-canvas');
            container.innerHTML = '';

            const width = container.clientWidth;
            const height = container.clientHeight;

            const svg = d3.select(container).append('svg')
                .attr('width', width)
                .attr('height', height);

            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id).distance(90))
                .force('charge', d3.forceManyBody().strength(-140))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(data.links)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 1.5);

            const node = svg.append('g')
                .selectAll('g')
                .data(data.nodes)
                .enter().append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                    .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
                    .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

            node.append('circle')
                .attr('r', 6)
                .attr('fill', d => d.filetype === '.py' ? '#38bdf8' : (d.filetype === '.md' ? '#a855f7' : '#06b6d4'));

            node.append('text')
                .attr('dx', 10)
                .attr('dy', '.35em')
                .text(d => d.filename);

            node.on('click', (e, d) => {
                document.getElementById('node-details').innerHTML = `
                    <div style="font-weight: 700; font-size: 1.05rem; color: #38bdf8;">${d.filename}</div>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin: 4px 0 10px;">${d.filepath}</div>
                    <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>Type:</strong> ${d.filetype || 'file'}</div>
                    <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;"><strong>Accesses:</strong> ${d.access_count || 1}</div>
                `;
            });

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('transform', d => `translate(${d.x},${d.y})`);
            });
        }

        document.getElementById('search-input').addEventListener('input', async (e) => {
            const q = e.target.value.trim();
            if (!q) return;
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const results = await res.json();
                const container = document.getElementById('search-results');
                container.innerHTML = results.map(r => `
                    <div class="result-item">
                        <div class="result-name">${r.filename} <span style="float:right; color:#818cf8; font-size:0.75rem;">${Math.round(r.score * 100)}%</span></div>
                        <div class="result-path">${r.filepath}</div>
                    </div>
                `).join('');
            } catch (err) {
                console.error("Search failed:", err);
            }
        });

        fetchGraphData();
    </script>
</body>
</html>
"""

class SemanticFSUIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass  # Quiet HTTP request logging

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path in ("/", "/ui", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

        elif path == "/api/graph":
            config = Config.get_instance()
            store = VectorStore(config.storage.db_path, config.storage.collection_name)

            nodes = []
            seen_ids = set()

            try:
                items = store.get_all(limit=150)
                for item in items:
                    filepath = item.get("filepath", "")
                    filename = item.get("filename", Path(filepath).name if filepath else "")
                    f_id = filepath or filename
                    if f_id and f_id not in seen_ids:
                        seen_ids.add(f_id)
                        nodes.append({
                            "id": f_id,
                            "filename": filename,
                            "filepath": filepath,
                            "filetype": item.get("filetype", Path(filepath).suffix.lower() if filepath else ""),
                            "access_count": 1
                        })
            except Exception:
                pass

            if not nodes:
                # Instant fallback: populate from workspace watch directories
                for wdir in config.watcher.watch_directories:
                    if wdir.exists():
                        for root, _, files in os.walk(wdir):
                            for f in files[:25]:
                                if not f.startswith('.'):
                                    fp = str(Path(root) / f)
                                    if fp not in seen_ids:
                                        seen_ids.add(fp)
                                        nodes.append({
                                            "id": fp,
                                            "filename": f,
                                            "filepath": fp,
                                            "filetype": Path(f).suffix.lower(),
                                            "access_count": 1
                                        })

            # Create relationship links between nodes of matching directory or extension
            links: list[dict[str, Any]] = []
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    n1 = nodes[i]
                    n2 = nodes[j]
                    same_ext = n1["filetype"] and n1["filetype"] == n2["filetype"]
                    same_dir = Path(n1["filepath"]).parent == Path(n2["filepath"]).parent if n1["filepath"] and n2["filepath"] else False
                    if same_dir or (same_ext and i % 3 == 0):
                        links.append({
                            "source": n1["id"],
                            "target": n2["id"],
                            "weight": 2.0 if same_dir else 1.0
                        })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"nodes": nodes, "links": links}).encode("utf-8"))

        elif path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            q = query_params.get("q", [""])[0]

            config = Config.get_instance()
            store = VectorStore(config.storage.db_path, config.storage.collection_name)
            from semanticfs.embedder import Embedder
            embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)
            emb = embedder.embed_text(q)
            results = store.search(emb, query_text=q, n_results=10)

            res_data = [
                {
                    "filename": r.filename,
                    "filepath": r.filepath,
                    "score": r.score,
                    "filetype": r.filetype
                }
                for r in results
            ]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res_data).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def start_ui_server(port: int = 9877) -> socketserver.TCPServer | None:
    """Start embedded UI server on background thread."""
    try:
        handler = SemanticFSUIHandler
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("127.0.0.1", port), handler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        logger.info(f"Web Node Graph Dashboard running on http://127.0.0.1:{port}/ui")
        return server
    except Exception as e:
        logger.debug(f"UI Server bind error: {e}")
        return None
