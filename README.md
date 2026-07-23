# SemanticFS

> **A Temporal-Associative Terminal Utility & Local Neural Vector Engine for Context-Aware File Retrieval.**

```text
   _____                           _   _      ______  _____ 
  / ____|                         | | (_)    |  ____|/ ____|
 | (___   ___ _ __ ___   __ _ _ __| |_ _  ___| |__  | (___  
  \___ \ / _ \ '_ ` _ \ / _` | '__| __| |/ __|  __|  \___ \ 
  ____) |  __/ | | | | | (_| | |  | |_| | (__| |     ____) |
 |_____/ \___|_| |_| |_|\__,_|_|   \__|_|\___|_|    |_____/ 
```

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Embeddings](https://img.shields.io/badge/embeddings-384D%20Neural-purple)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Local-green)

---

## System Overview

**SemanticFS** eliminates the cognitive friction of hierarchical file system retrieval. Instead of requiring exact folder paths (e.g., `C:/Users/Documents/v1/final.py`), SemanticFS allows users to retrieve files based on ambient context, semantic content concepts, and activity history.

---

## Core Features

- **Local Neural Vector Search**: Powered by `SentenceTransformers` (`all-MiniLM-L6-v2`) and embedded `ChromaDB`.
- **Local Model Fine-Tuning (`sfind train`)**: Fine-tune transformer embeddings directly on local codebase vocabulary and files for specialized accuracy.
- **Hybrid Keyword & Vector Scoring**: Combines dense vector similarity with token match reranking for sub-millisecond precision.
- **On-Demand Service Control**: Zero persistent CPU or battery overhead. Start and stop background event tracking on demand via `sfind start` and `sfind stop`.
- **Terminal Interface**: Interactive CLI menu with arrow-key navigation, quick-pick keys (`1`-`5`), and VS Code integration (`--code`).
- **Universal Format Extraction**: Parses code files, Markdown, TXT, PDF, DOCX, XLSX, PPTX, JSON, CSV, and metadata for media binaries.
- **Privacy & Offline Isolation**: Operates completely offline with zero telemetry or cloud dependencies.

---

## Quick Start

### Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Rioeio/SemanticFS.git
cd SemanticFS
pip install -e .
```

### Usage Examples

```bash
# Natural language context search
sfind python linear algebra matrix solver

# Search and open top result directly in VS Code
sfind medical research paper --code

# Display system analytics and vector database stats
sfind stats
```

---

## Command Reference (`sfind`)

| Command | Action |
|---|---|
| `sfind <query>` | Context search with interactive terminal menu |
| `sfind stats` | Display master analytics (file count, 384D vectors, DB size) |
| `sfind train` | Fine-tune local neural embedding model on indexed files |
| `sfind reindex` | Force full file re-scan and vector re-indexing |
| `sfind start` | Launch ambient background tracking daemon on demand |
| `sfind stop` | Stop ambient background tracking daemon |
| `sfind status` | Check active status of background daemon |
| `sfind recent` | List 10 most recently modified files |
| `sfind list-dirs` | List all monitored workspace directories |
| `sfind add-dir <path>` | Register a new directory for indexing |
| `sfind --clear` | Reset vector collection |

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       sfind CLI                             │
│       (Interactive Rich Live Menu / Vector Search)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
  ┌─────────────────────────┐     ┌─────────────────────────┐
  │ Local AI Embedder       │     │ Vector Store (ChromaDB) │
  │ (all-MiniLM-L6-v2 /     │ ──► │ 384-Dim Neural Dense    │
  │ Custom Trained Weights) │     │ Vector Persistence      │
  └─────────────────────────┘     └─────────────────────────┘
               ▲                               ▲
               │                               │
┌──────────────┴───────────────────────────────┴──────────────┐
│                  Ambient File Watcher Daemon                 │
│         (Context Snapshot + Local File Event Tracker)        │
└─────────────────────────────────────────────────────────────┘
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
