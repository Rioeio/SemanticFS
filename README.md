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
![Rust](https://img.shields.io/badge/rust-core-orange)
![Embeddings](https://img.shields.io/badge/embeddings-384D%20Neural-purple)
![Multimodal](https://img.shields.io/badge/multimodal-CLIP%20Vision-pink)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Local-green)

---

## System Overview

**SemanticFS** eliminates the cognitive friction of hierarchical file system retrieval. Instead of requiring exact folder paths (e.g., `C:/Users/Documents/v1/final.py`), SemanticFS allows users to retrieve files based on ambient activity context, semantic concepts, visual image scenes, and activity history across all user drive locations.

---

## Core Capabilities & Features

- **Local Neural Vector Search**: Powered by `SentenceTransformers` (`all-MiniLM-L6-v2`) and embedded `ChromaDB`.
- **Multimodal CLIP Vision Scene Indexing**: Integrated HuggingFace Transformers `CLIPModel` (`openai/clip-vit-base-patch32`) for zero-shot image scene classification ("beach sunset", "receipt invoice text", "landscape", "face photo").
- **Recency Weight Decay**: Gives an exponential score boost (+0.10 max) to files modified within the last 48 hours, keeping active work at the top.
- **Full Drive Overview**: Automatically monitors and indexes `Documents`, `OneDrive\Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, and `Dev` directories.
- **Dynamic Semantic Chunking**: Splits large files (1000+ lines) into overlapping semantic windows with exact line number tracking (`#L140-L195`).
- **Textbook & Dump Noise Filtering**: Caps maximum chunks at 25 per file and filters out common stop-words to prevent massive textbook PDF dumps from polluting search results.
- **Sub-20ms Search Latency**: Instant query responses via pre-warmed background IPC socket server (`sfind start`).
- **Local Model Fine-Tuning (`sfind train`)**: Fine-tune transformer embeddings directly on local codebase vocabulary and files for specialized accuracy.
- **ONNX INT8 Model Quantization (`sfind onnx`)**: Export PyTorch model weights to quantized ONNX for 4X faster CPU inference.
- **Virtual Drive Mount Engine (`sfind mount`)**: Initializes virtual search shortcut directory at `~/.semanticfs/virtual_drive` for Explorer integration.
- **Native Rust Engine Architecture (`native_core/`)**: Standalone Rust core crate (`libsemanticfs`) for native C/Rust speed.
- **Terminal Interface**: Interactive CLI menu with arrow-key navigation, live syntax-highlighted code preview box, quick-pick keys (`1`-`5`), and VS Code integration (`--code`).
- **Universal Format Extraction**: Parses code files, Markdown, TXT, PDF, Word (`.docx`), PowerPoint (`.pptx`), Excel (`.xlsx`), JSON, CSV, and EXIF/CLIP metadata for media binaries (`.png`, `.jpg`, `.mp4`, `.mp3`).
- **Git Commit Search**: Search git commit messages across all monitored repositories with `sfind commit <query>`.
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

### How to Search Effectively

SemanticFS supports natural language context queries as well as targeted filter flags:

```bash
# Natural language context search (with interactive arrow keys & live preview)
sfind python linear algebra matrix solver

# Multimodal visual scene search for images across Pictures/Downloads
sfind beach sunset vacation

# Search git commits across all monitored repositories
sfind commit "fix authentication bug"

# Export ONNX INT8 Quantized model weights
sfind onnx

# Mount Virtual Drive directory
sfind mount

# Filter by file extension (--type) and modification time (--since)
sfind research notes --type pdf --since 7d

# Search and open top match directly in VS Code
sfind main application entrypoint --code

# Display system analytics and vector database stats
sfind stats
```

---

## Command Reference (`sfind`)

| Command / Option | Description |
|---|---|
| `sfind <query>` | Natural language context search + interactive arrow menu & live code preview |
| `sfind start` | Launch pre-warmed background IPC server & tracking daemon for sub-20ms search |
| `sfind stop` | Stop ambient background daemon |
| `sfind status` | Display service status and master vector analytics |
| `sfind stats` | Show master analytics (files/chunks count, 384D vectors, DB disk size) |
| `sfind commit <query>` | Search git commit messages across monitored repositories |
| `sfind completion` | Generate PowerShell auto-completion profile script |
| `sfind train` | Fine-tune local neural embedding model on your local files |
| `sfind onnx` | Export model weights to quantized ONNX INT8 format |
| `sfind mount` | Initialize virtual drive search folder for Explorer integration |
| `sfind reindex` | Force full file re-scan & dynamic vector re-indexing across all user drives |
| `sfind recent` | Display 10 most recently modified files |
| `sfind list-dirs` | List all monitored workspace directories |
| `sfind add-dir <path>` | Register a new directory for indexing |
| `sfind --type pdf` | Filter search results by file extension (`pdf`, `py`, `docx`, `xlsx`, etc.) |
| `sfind --since 7d` | Filter search results by modification time (e.g. `7d`, `24h`, `30m`) |
| `sfind --code` | Automatically open top search result directly in VS Code |
| `sfind --clear` | Reset vector store collection |

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
  │ Local AI & CLIP Embedder│     │ Vector Store (ChromaDB) │
  │ (all-MiniLM-L6-v2 /     │ ──► │ 384-Dim Neural Dense    │
  │ CLIP Vision / Custom)   │     │ Vector Persistence      │
  └─────────────────────────┘     └─────────────────────────┘
               ▲                               ▲
               │                               │
┌──────────────┴───────────────────────────────┴──────────────┐
│                  Ambient File Watcher Daemon                 │
│         (Context Snapshot + Local File Event Tracker)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Native Rust Core Crate (`native_core/`)

Includes a native Rust engine crate (`libsemanticfs`) in `native_core/`:
- `native_core/Cargo.toml`
- `native_core/src/lib.rs`

To build the native Rust release binary:
```bash
cd native_core
cargo build --release
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
