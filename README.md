# 🧠 SemanticFS

> **A Temporal-Associative Terminal Tool & Local Neural Vector Engine for Context-Aware File Retrieval.**

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
![Vectors](https://img.shields.io/badge/embeddings-384D%20Neural-purple)
![Offline](https://img.shields.io/badge/privacy-100%25%20Local-green)

---

## 🌟 Overview

**SemanticFS** bridges the cognitive friction between human mental models and deterministic storage. Instead of forcing users to remember exact file paths (`C:/Users/Documents/v1/final.py`), SemanticFS allows you to search files based on **what you were doing, content concepts, and ambient activity context**.

---

## ✨ Features

- 🧠 **100% Local Neural Vector Search**: Powered by `SentenceTransformers` (`all-MiniLM-L6-v2`) & `ChromaDB`.
- 🎓 **Local Model Fine-Tuning (`sfind train`)**: Fine-tune AI model weights directly on your local files for personalized domain accuracy.
- ⚡ **Hybrid Keyword & Vector Scoring**: Combines dense vector embeddings with exact/partial token reranking for sub-millisecond precision.
- 🎮 **On-Demand Service Control**: Zero 24/7 battery/CPU drain. Start and stop background ambient tracking on demand with `sfind start` and `sfind stop`.
- ⌨️ **Terminal-Native Selection**: Interactive Rich terminal menu with arrow-key navigation, quick-number keys (`1`-`5`), and VS Code integration (`c`).
- 📁 **Universal File Format Support**: Extracts text and metadata from Code, Markdown, TXT, PDF, DOCX, XLSX, PPTX, JSON, CSV, and media/binary files.
- 🔒 **100% Private & Offline**: No cloud APIs, no data transmission, no subscription keys required.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/your-username/SemanticFS.git
cd SemanticFS
pip install -e .
```

### 2. Search your files

```bash
# Search using natural language context
sfind python linear algebra matrix solver

# Search and automatically open in VS Code
sfind medical research paper --code

# View master system & vector analytics
sfind stats
```

---

## 💻 Terminal Commands Summary (`sfind`)

| Command | Action |
|---|---|
| `sfind <query>` | Natural language context search + interactive arrow-key menu |
| `sfind stats` | Show master analytics: indexed files, 384D vector count, DB disk size |
| `sfind train` | Fine-tune local neural embedding model on your local files |
| `sfind reindex` | Force full re-scan & vector re-indexing across all directories |
| `sfind start` | Launch ambient background tracking process on demand |
| `sfind stop` | Stop all background daemon processes |
| `sfind status` | Check running/stopped status of background services |
| `sfind recent` | Display 10 most recently modified files |
| `sfind list-dirs` | Show all monitored workspace directories |
| `sfind add-dir <path>` | Add a new folder path to monitored watch list |
| `sfind --clear` | Reset vector collection |

---

## 🛠️ Architecture

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

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
