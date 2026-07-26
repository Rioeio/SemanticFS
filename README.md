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

- **Local Neural Vector Search**: Powered by `BAAI/bge-small-en-v1.5` (#1 MTEB Benchmark model) and embedded `ChromaDB`.
- **Full User Space System Coverage (`C:\Users\Manoj`)**: Automatically scans and monitors the entire user directory tree (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Dev`, and custom workspaces).
- **16-Worker ThreadPoolExecutor Parallel Scanning**: Multi-threaded parallel file crawler indexes 50,000+ files across the system in seconds.
- **Multimodal CLIP Vision Scene Indexing**: Integrated HuggingFace Transformers `CLIPModel` (`openai/clip-vit-base-patch32`) for zero-shot image scene classification ("beach sunset", "receipt invoice text", "landscape", "face photo").
- **Recency Weight Decay**: Gives an exponential score boost (+0.10 max) to files modified within the last 48 hours, keeping active work at the top.
- **AST Syntax & Header-Aware Semantic Chunking**: Integrated `semanticfs/ast_chunker.py` parses Python files by function (`def`) / class (`class`) boundaries and Markdown files by `#` headers so code logic is never cut in half.
- **Textbook & Dump Noise Filtering**: Caps maximum chunks at 25 per file and filters out common stop-words to prevent massive textbook PDF dumps from polluting search results.
- **Sub-5ms Query Latency**: Instant search responses via pre-warmed background IPC socket server (`sfind start`).
- **Local Model Fine-Tuning (`sfind train`)**: Fine-tune transformer embeddings directly on local codebase vocabulary and files for specialized accuracy.
- **ONNX INT8 Model Quantization (`sfind onnx`)**: Export PyTorch model weights to quantized ONNX for 4X faster CPU inference.
- **Virtual Drive Mount Engine (`sfind mount`)**: Initializes virtual search shortcut directory at `~/.semanticfs/virtual_drive` for Explorer integration.
- **Native Rust Engine Architecture (`native_core/`)**: Standalone Rust core crate (`libsemanticfs`) for native C/Rust speed.
- **"Bad Apple!!" Movable ASCII Neural Visualizer (`sfind model`)**: Iconic 3D ASCII raycasting engine (`semanticfs/visualizer.py`) rendering high-detail "Bad Apple!!" Touhou black-and-white vector silhouettes, 384-dim neural meshes, and CLIP vision patches with real-time WASD/Arrow 3D rotation, zoom, and mode switching.
- **Virtual Smart Collections (`sfind collection`)**: Create virtual shortcut folders in File Explorer without moving a single physical file on disk (zero disk risk).
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

### Structured Search Operators & Sharp Precision Engine

For pinpoint search precision, `SemanticFS` supports structured inline query operators:

| Operator Syntax | Purpose & Example |
|---|---|
| `ext:pdf` / `ext:py` | Filter strictly by file extension (`sfind "neural network" ext:py`) |
| `file:report` / `file:invoice` | Filter by matching filename sub-string (`sfind "budget summary" file:2026`) |
| `in:documents` / `in:desktop` | Limit search scope to specific directory folder (`sfind notes in:documents`) |
| `tag:note` | Search specifically inside custom user-added file notes (`sfind tag:final`) |
| `+term` | Require that `term` MUST exist in the file (`sfind python +dataset`) |
| `-term` | Disqualify & exclude any file containing `term` (`sfind AI research -draft`) |
| `score:0.5` | Dynamically override the minimum relevance score threshold |

### Search Examples

```bash
# Structured search: Python files in Documents excluding draft files
sfind "machine learning" ext:py in:documents -draft

# Natural language context search (with interactive arrow keys & live preview)
sfind python linear algebra matrix solver

# Find target file & copy 'cd /folder/path' command directly to clipboard
sfind jump "physics assignment"

# Find semantic duplicate files across drive via vector similarity
sfind duplicates

# Attach custom semantic notes and tags to any file
sfind tag resume.pdf "final submitted job application 2026"

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

## Interactive Terminal Menu Action Shortcuts

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
| `sfind collection create` | Create Virtual Smart Collection shortcuts in Explorer (Zero real files moved on disk) |
| `sfind collection list` | Display all active Virtual Smart Collections and their shortcut rules |
| `sfind jump <query>` | Find target file & copy `cd /folder/path` command directly to clipboard |
| `sfind duplicates` | Scan vector store to identify high-similarity duplicate files across drive |
| `sfind tag <file> <note>` | Attach custom semantic notes and tags to any file for boosted search |
| `sfind model` | Launch 3D movable neural model topology raycasting visualizer in terminal |
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
│       (Interactive Rich Live Menu / Vector Search)          │
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
│        Parallel 16-Worker Ambient File Watcher Daemon       │
│         (Context Snapshot + Local File Event Tracker)       │
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
