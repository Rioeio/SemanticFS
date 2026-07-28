from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_tesseract_path() -> str | None:
    common_win_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
    ]
    for p in common_win_paths:
        if os.path.exists(p):
            return p
    return shutil.which("tesseract")

def get_cargo_path() -> str | None:
    return shutil.which("cargo")

def run_environment_doctor():
    """Runs a comprehensive diagnostic check of python packages and system-level binaries."""
    console.print("\n🩺 [bold bright_cyan]SemanticFS System Diagnostics & Environment Doctor[/bold bright_cyan]\n")

    table = Table(title="Component & Dependency Status", border_style="cyan", expand=True)
    table.add_column("Component", style="bold green", width=22)
    table.add_column("Type", style="bold yellow", width=12)
    table.add_column("Status", style="bold magenta", width=14)
    table.add_column("Details & Action Items", style="white")

    # 1. Operating System
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    table.add_row("Operating System", "System", "[green]✔ Supported[/green]", os_info)

    # 2. Python Runtime
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_status = "[green]✔ OK[/green]" if sys.version_info >= (3, 11) else "[red]✘ Outdated[/red]"
    py_note = f"Python {py_ver} (Requires >= 3.11)"
    table.add_row("Python Version", "Runtime", py_status, py_note)

    # 3. Core Package: sentence-transformers
    try:
        import sentence_transformers
        st_ver = getattr(sentence_transformers, "__version__", "Installed")
        table.add_row("SentenceTransformers", "Core Pip", "[green]✔ Installed[/green]", f"v{st_ver}")
    except ImportError:
        table.add_row("SentenceTransformers", "Core Pip", "[red]✘ Missing[/red]", "Run: pip install sentence-transformers")

    # 4. Core Package: chromadb
    try:
        import chromadb
        cdb_ver = getattr(chromadb, "__version__", "Installed")
        table.add_row("ChromaDB Vector Store", "Core Pip", "[green]✔ Installed[/green]", f"v{cdb_ver}")
    except ImportError:
        table.add_row("ChromaDB Vector Store", "Core Pip", "[red]✘ Missing[/red]", "Run: pip install chromadb")

    # 5. Core Package: PyMuPDF / docx / pptx / openpyxl
    docs_ok = True
    try:
        import fitz
        import docx
        import pptx
        import openpyxl
    except ImportError:
        docs_ok = False

    doc_status = "[green]✔ Installed[/green]" if docs_ok else "[yellow]⚠ Partial[/yellow]"
    table.add_row("Document Extractors", "Core Pip", doc_status, "PDF, DOCX, PPTX, XLSX extractors")

    # 6. Optional Extra: Vision (torch + transformers + PIL)
    try:
        import torch
        import transformers
        from PIL import Image
        vis_status = "[green]✔ Installed[/green]"
        vis_note = "CLIP Vision model available (pip install -e '.[vision]')"
    except ImportError:
        vis_status = "[yellow]⚪ Optional[/yellow]"
        vis_note = "Not installed. Install extra: pip install -e '.[vision]'"
    table.add_row("CLIP Vision Extra", "Pip Extra", vis_status, vis_note)

    # 7. System Binary: Tesseract OCR
    tess_path = get_tesseract_path()
    if tess_path:
        ocr_status = "[green]✔ Available[/green]"
        ocr_note = f"Binary path: {tess_path}"
    else:
        ocr_status = "[yellow]⚪ Not Found[/yellow]"
        if platform.system() == "Windows":
            ocr_note = "System binary missing. Install: winget install UB-Mannheim.TesseractOCR"
        elif platform.system() == "Darwin":
            ocr_note = "System binary missing. Install: brew install tesseract"
        else:
            ocr_note = "System binary missing. Install: sudo apt install tesseract-ocr"
    table.add_row("Tesseract OCR", "System Binary", ocr_status, ocr_note)

    # 8. System Binary: Rust Toolchain (Cargo)
    cargo_path = get_cargo_path()
    if cargo_path:
        rust_status = "[green]✔ Available[/green]"
        rust_note = f"Binary path: {cargo_path}"
    else:
        rust_status = "[yellow]⚪ Optional[/yellow]"
        rust_note = "Not installed. Only needed for native_core standalone Rust build."
    table.add_row("Rust Toolchain", "System Binary", rust_status, rust_note)

    # 9. Storage Directory Access
    chroma_dir = Path("~/.semanticfs/chroma").expanduser()
    try:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        store_status = "[green]✔ Writable[/green]"
        store_note = f"Storage path: {chroma_dir}"
    except Exception as e:
        store_status = "[red]✘ Error[/red]"
        store_note = f"Permission error: {e}"
    table.add_row("Vector Storage Dir", "FileSystem", store_status, store_note)

    console.print(table)
    console.print("\n[dim]Run 'sfind doctor' anytime to verify your environment.[/dim]\n")

if __name__ == "__main__":
    run_environment_doctor()
