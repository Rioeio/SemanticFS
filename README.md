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

![Status](https://img.shields.io/badge/status-Active%20Alpha-orange)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Rust](https://img.shields.io/badge/rust-experimental-lightgrey)
![Embeddings](https://img.shields.io/badge/embeddings-BAAI%2Fbge--small--en--v1.5-purple)
![Multimodal](https://img.shields.io/badge/multimodal-CLIP%20Vision-pink)
![OCR](https://img.shields.io/badge/OCR-Tesseract%2FEasyOCR-yellow)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Local-green)

---

## System Overview

**SemanticFS** eliminates the cognitive friction of hierarchical file system retrieval. Instead of requiring exact folder paths (e.g., `Documents/v1/final.py`), SemanticFS allows users to retrieve files based on ambient activity context, semantic concepts, visual image scenes, printed OCR text, and activity history across all user drive locations.

---

## Core Capabilities & Features

- **Local Neural Vector Search (`BAAI/bge-small-en-v1.5`)**: Powered by `BAAI/bge-small-en-v1.5` (a compact, high-throughput 384-dimensional embedding model optimized for local offline vector search) and embedded `ChromaDB`.
- **Latency Benchmarks**:
  - **Sub-5ms Pre-Warmed Socket IPC**: IPC socket server on `127.0.0.1:9876` (`sfind start`) returns pre-warmed memory embeddings in **~3ms - 5ms**.
  - **18.97ms Batch Vector Query**: Cold vector database queries across 3,000+ indexed chunks average **18.97ms / query** in stress benchmarks.
- **AST Syntax & Header-Aware Semantic Chunker (`semanticfs/ast_chunker.py`)**: Parses Python files strictly by function (`def`) and class (`class`) AST boundaries and Markdown files by `#` headers so code logic is never cut in half mid-function.
- **Multimodal CLIP Vision Scene Indexing**: Integrated HuggingFace Transformers `CLIPModel` (`openai/clip-vit-base-patch32`) for zero-shot image scene classification ("beach sunset", "receipt invoice text", "landscape", "face photo").
- **Offline OCR Text Extraction Engine (`semanticfs/ocr.py`)**: Tesseract / EasyOCR pipeline extracts printed text inside scanned PDFs, receipts, invoices, code error screenshots, and images for full-text searchability.
- **Full User Space System Coverage (`%USERPROFILE%` / `~`)**: Automatically scans and monitors the entire user directory tree (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Dev`, and custom workspaces).
- **16-Worker ThreadPoolExecutor Parallel Scanning**: Multi-threaded parallel file crawler in `daemon.py` indexes 50,000+ files across the system in parallel.
- **Virtual Smart Collections (`sfind collection`)**: Create virtual shortcut folders in File Explorer without moving a single physical file on disk (**Zero Disk Modification Risk**).
- **Structured Search Operators & Sharp Precision Engine**: Pinpoint search using inline operators (`ext:`, `file:`, `in:`, `tag:`, `+must`, `-exclude`, `score:0.5`) alongside 100% natural language search with zero mandatory file format typing.
- **Interactive Terminal Interface**: Arrow-key navigation, live `monokai` syntax-highlighted code preview box, `Enter` to open File Explorer and highlight the selected file, `o` for App launch, `c` for VS Code, and `y`/`p` for Clipboard path/snippet copy.
- **Terminal Folder Jump (`sfind jump <query>`)**: Finds the target file and copies the `cd "/folder/path"` command directly to the Windows Clipboard for instant shell navigation.
- **Semantic Duplicate File Finder (`sfind duplicates`)**: Scans the vector store to identify high-similarity duplicate files across your drive via vector similarity.
- **Custom File Annotations & Tags (`sfind tag <file> <note>`)**: Attach custom semantic notes and tags to any file for boosted retrieval relevance.
- **3D Movable "Bad Apple!!" ASCII Raycasting Visualizer (`sfind model`)**: Standalone 3D ASCII raycasting engine (`semanticfs/visualizer.py`) projects rotating 384-dimensional vector topology, Touhou black-and-white silhouettes, and CLIP vision patches with real-time WASD/Arrow controls, zoom, and mode switching.
- **Recency Weight Decay**: Gives an exponential score boost (+0.10 max) to files modified within the last 48 hours, keeping active work at the top.
- **Universal Format Extraction**: Parses code files, Markdown, TXT, PDF, Word (`.docx`), PowerPoint (`.pptx`), Excel (`.xlsx`), JSON, CSV, OCR text, and EXIF/CLIP metadata for media binaries (`.png`, `.jpg`, `.mp4`, `.mp3`).
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

---

## Structured Search Operators & Precision Guide

For pinpoint search precision, `SemanticFS` supports structured inline query operators alongside natural language:

| Operator Syntax | Purpose & Description | Example Usage |
|---|---|---|
| `ext:pdf` / `ext:py` | Filter strictly by file extension | `sfind "neural network" ext:py` |
| `file:report` / `file:invoice` | Filter by matching filename sub-string | `sfind "budget summary" file:2026` |
| `in:documents` / `in:desktop` | Limit search scope to specific directory folder | `sfind notes in:documents` |
| `tag:note` | Search specifically inside custom user-added file notes | `sfind tag:final` |
| `+term` | Require mandatory keyword matching | `sfind python +dataset` |
| `-term` | Disqualify and exclude any file containing `term` | `sfind AI research -draft` |
| `score:0.5` | Dynamically override the minimum relevance score threshold | `sfind physics score:0.55` |

### Search Examples

```bash
# Structured search: Python files in Documents excluding draft files
sfind "machine learning" ext:py in:documents -draft

# Natural language context search (with interactive arrow keys & live preview)
sfind python linear algebra matrix solver

# Find target file & copy 'cd /folder/path' command directly to clipboard
sfind jump "physics assignment"

# Create Virtual Smart Collection shortcuts in Explorer (Zero real files moved on disk)
sfind collection create "Tax Receipts" "invoice receipt ext:pdf"

# Find semantic duplicate files across drive via vector similarity
sfind duplicates

# Attach custom semantic notes and tags to any file
sfind tag resume.pdf "final submitted job application 2026"

# Multimodal visual scene search for images across Pictures/Downloads
sfind beach sunset vacation

# Launch 3D Movable "Bad Apple!!" ASCII Neural Model Visualizer
sfind model

# Search git commits across all monitored repositories
sfind commit "fix authentication bug"

# Export ONNX INT8 Quantized model weights
sfind onnx

# Mount Virtual Drive directory in Windows File Explorer
sfind mount

# Filter by modification time (--since)
sfind research notes --since 7d

# Search and open top match directly in VS Code
sfind main application entrypoint --code

# Display system analytics and vector database stats
sfind stats
```

---

## Interactive Terminal Action Shortcuts

When navigating search results in the terminal (`sfind <query>`), press any of the following action keys:

| Shortcut Key | Action Performed |
|---|---|
| `Enter` or `e` | Open Windows File Explorer and highlight the selected file |
| `o` | Launch file directly in its default application (Word, PDF reader, Photos) |
| `c` | Open file directly in VS Code |
| `y` | Copy absolute file path directly to Windows Clipboard |
| `p` | Copy matching text snippet directly to Windows Clipboard |
| `1` - `5` | Quick-pick rank number 1 through 5 |
| `q` / `Esc` | Quit interactive selection menu |

---

## Command Reference (`sfind`)

| Command / Option | Description |
|---|---|
| `sfind <query>` | Natural language context search + interactive arrow menu & live code preview |
| `sfind jump <query>` | Find target file & copy `cd /folder/path` command directly to clipboard |
| `sfind collection create` | Create Virtual Smart Collection shortcuts in Explorer (Zero real files moved) |
| `sfind collection list` | Display all active Virtual Smart Collections and their shortcut rules |
| `sfind duplicates` | Scan vector store to identify high-similarity duplicate files across drive |
| `sfind tag <file> <note>` | Attach custom semantic notes and tags to any file for boosted search |
| `sfind model` / `sfind visualize` | Launch 3D Movable "Bad Apple!!" ASCII Neural Model Visualizer in terminal |
| `sfind start` | Launch pre-warmed background IPC server & tracking daemon for sub-5ms search |
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
| `sfind list-dirs` | List all currently monitored workspace directories |
| `sfind add-dir <path>` | Register a new directory for indexing |
| `sfind --type pdf` | Filter search results by file extension (`pdf`, `py`, `docx`, `xlsx`, etc.) |
| `sfind --since 7d` | Filter search results by modification time (e.g. `7d`, `24h`, `30m`) |
| `sfind --code` | Automatically open top search result directly in VS Code |
| `sfind --clear` | Reset vector store collection |

---

## Detailed System Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   sfind CLI                                            │
│      (Interactive Arrow Menu / Live Monokai Code Preview / Action Keys / IPC Client)    │
└───────────────────────────┬────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
  ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
  │   Neural Embedding Engine         │           │   Vector Store (ChromaDB + RAM)   │
  │   • Model: BAAI/bge-small-en-v1.5 │ ────────► │   • 384-Dim Neural Vector Vectors │
  │   • CLIP Vision (Patch-32)        │           │   • Fast Matrix Dot-Product Cache │
  │   • Tesseract / EasyOCR Engine    │           │   • Recency Boost (+0.10 Decay)   │
  │   • AST Code Syntax Chunker       │           │   • Intent Category Boost (+0.50) │
  └───────────────────────────────────┘           └───────────────────────────────────┘
                    ▲                                               ▲
                    │                                               │
┌───────────────────┴───────────────────────────────────────────────┴───────────────────┐
│              16-Worker ThreadPoolExecutor Parallel Ambient Daemon                      │
│                  (IPC Socket Server 127.0.0.1:9876 / Sub-5ms Queries)                  │
└───────────────────────────┬───────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
  ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
  │    Virtual Smart Collections      │           │    Implicit File Linker           │
  │  (Zero Disk Modification Risk)    │           │   (SQLite Co-Access Relationship) │
  │  • ~/.semanticfs/virtual_drive    │           │   • Recorded File Interactions    │
  └───────────────────────────────────┘           └───────────────────────────────────┘
```

---

## Native Rust Core Crate (`native_core/`) [Experimental / Planned Integration]

> [!NOTE]
> The native Rust engine crate (`libsemanticfs`) in `native_core/` is currently experimental and standalone (`native_core/Cargo.toml`, `native_core/src/lib.rs`). Python vector search currently utilizes embedded ChromaDB; PyO3 bindings for native Rust core acceleration are planned for Phase 2.

To build the native Rust release binary:
```bash
cd native_core
cargo build --release
```

---

## Benchmark Verification Results

* **100-Query Automated Benchmark Suite (`tests/test_suite_100.py`)**: **95.00% Overall Success Average** (0.82 Mean Match Score out of 1.00).
* **1,000 Real Drive-Derived Stress Test (`tests/run_drive_stress_fast.py`)**: **88.10% Overall Success Average** (**18.97 ms / query search latency**).

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
