from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

import socket

console = Console()

def is_daemon_reachable(port: int = 9876, host: str = "127.0.0.1", timeout: float = 0.2) -> bool:
    """Check whether the background daemon IPC server is reachable on the specified port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False

def is_startup_daemon_installed() -> bool:
    """Check if the Windows Startup task / VBScript is present in the user Startup folder."""
    if platform.system() != "Windows":
        return False
    try:
        appdata = os.environ.get("APPDATA")
        if appdata:
            startup_folder = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        else:
            startup_folder = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        vbs_path = startup_folder / "SemanticFS_Daemon.vbs"
        return vbs_path.exists()
    except Exception:
        return False

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

def run_environment_doctor() -> bool:
    """Runs a comprehensive diagnostic check of python packages, background daemon, and system binaries."""
    console.print("\n🩺 [bold bright_cyan]SemanticFS System Diagnostics & Environment Doctor[/bold bright_cyan]\n")

    table = Table(title="Component & Dependency Status", border_style="cyan", expand=True)
    table.add_column("Component", style="bold green", width=24)
    table.add_column("Type", style="bold yellow", width=12)
    table.add_column("Status", style="bold magenta", width=16)
    table.add_column("Details & Action Items", style="white")

    # 1. Operating System
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    table.add_row("Operating System", "System", "[green]✔ Supported[/green]", os_info)

    # 2. Python Runtime
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_status = "[green]✔ OK[/green]" if sys.version_info >= (3, 11) else "[red]✘ Outdated[/red]"
    py_note = f"Python {py_ver} (Requires >= 3.11)"
    table.add_row("Python Version", "Runtime", py_status, py_note)

    # 3. Ambient Daemon & IPC Fast Path (Port 9876)
    daemon_reachable = is_daemon_reachable(port=9876)
    if daemon_reachable:
        daemon_status = "[green]✔ Active[/green]"
        daemon_note = "Listening on 127.0.0.1:9876 (Sub-5ms fast IPC search active)"
    else:
        daemon_status = "[bold red]✘ Offline (Fallback)[/bold red]"
        daemon_note = (
            "Port 9876 unreachable. CLI falling back to slow cold model load (~300-800ms). "
            "Fix: 'sfind start' or 'powershell -ExecutionPolicy Bypass -File scripts/setup_startup_daemon.ps1'"
        )
    table.add_row("Ambient Daemon IPC", "Daemon Service", daemon_status, daemon_note)

    # 4. Windows Startup Persistence
    if platform.system() == "Windows":
        startup_installed = is_startup_daemon_installed()
        if startup_installed:
            persist_status = "[green]✔ Configured[/green]"
            persist_note = "SemanticFS_Daemon.vbs installed in Windows Startup folder (24/7 ambient)"
        else:
            persist_status = "[yellow]⚪ Not Configured[/yellow]"
            persist_note = (
                "Not in Windows Startup. Run: powershell -ExecutionPolicy Bypass -File scripts/setup_startup_daemon.ps1"
            )
        table.add_row("Startup Persistence", "Windows Task", persist_status, persist_note)

    # 5. Core Package: sentence-transformers
    try:
        import sentence_transformers
        st_ver = getattr(sentence_transformers, "__version__", "Installed")
        table.add_row("SentenceTransformers", "Core Pip", "[green]✔ Installed[/green]", f"v{st_ver}")
    except ImportError:
        table.add_row("SentenceTransformers", "Core Pip", "[red]✘ Missing[/red]", "Run: pip install sentence-transformers")

    # 6. Core Package: chromadb
    try:
        import chromadb
        cdb_ver = getattr(chromadb, "__version__", "Installed")
        table.add_row("ChromaDB Vector Store", "Core Pip", "[green]✔ Installed[/green]", f"v{cdb_ver}")
    except ImportError:
        table.add_row("ChromaDB Vector Store", "Core Pip", "[red]✘ Missing[/red]", "Run: pip install chromadb")

    # 7. Core Package: PyMuPDF / docx / pptx / openpyxl
    docs_ok = True
    try:
        import docx  # noqa: F401
        import fitz  # noqa: F401
        import openpyxl  # noqa: F401
        import pptx  # noqa: F401
    except ImportError:
        docs_ok = False

    doc_status = "[green]✔ Installed[/green]" if docs_ok else "[yellow]⚠ Partial[/yellow]"
    table.add_row("Document Extractors", "Core Pip", doc_status, "PDF, DOCX, PPTX, XLSX extractors")

    # 8. Optional Extra: Vision (torch + transformers + PIL)
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        from PIL import Image  # noqa: F401
        vis_status = "[green]✔ Installed[/green]"
        vis_note = "CLIP Vision model available (pip install -e '.[vision]')"
    except ImportError:
        vis_status = "[yellow]⚪ Optional[/yellow]"
        vis_note = "Not installed. Install extra: pip install -e '.[vision]'"
    table.add_row("CLIP Vision Extra", "Pip Extra", vis_status, vis_note)

    # 9. System Binary: Tesseract OCR
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

    # 10. System Binary: Rust Toolchain (Cargo)
    cargo_path = get_cargo_path()
    if cargo_path:
        rust_status = "[green]✔ Available[/green]"
        rust_note = f"Binary path: {cargo_path}"
    else:
        rust_status = "[yellow]⚪ Optional[/yellow]"
        rust_note = "Not installed. Only needed for native_core standalone Rust build."
    table.add_row("Rust Toolchain", "System Binary", rust_status, rust_note)

    # 11. Storage Directory Access
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

    if not daemon_reachable:
        from rich.panel import Panel
        warn_msg = (
            "[bold red]⚠️ Daemon is currently OFFLINE on port 9876[/bold red]\n\n"
            "[yellow]Impact:[/yellow] CLI searches are currently falling back to cold PyTorch model loading\n"
            "on every command invocation (~300ms–800ms latency penalty instead of sub-5ms IPC).\n\n"
            "[bold cyan]Actionable Fix Commands:[/bold cyan]\n"
            "  • [bold green]Start daemon for current session:[/bold green]\n"
            "      [bold white]sfind start[/bold white]\n\n"
            "  • [bold green]Enable persistent 24/7 background startup (Recommended):[/bold green]\n"
            "      [bold white]powershell -ExecutionPolicy Bypass -File scripts/setup_startup_daemon.ps1[/bold white]\n"
        )
        console.print(Panel(warn_msg, title="[bold red]Action Required: Ambient Daemon Offline[/bold red]", border_style="red"))

    console.print("\n[dim]Run 'sfind doctor' anytime to verify your environment.[/dim]\n")
    return daemon_reachable

if __name__ == "__main__":
    run_environment_doctor()
