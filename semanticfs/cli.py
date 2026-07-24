from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live
from rich.prompt import IntPrompt
from rich.table import Table

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.linker import FileLinker
from semanticfs.store import VectorStore

console = Console()

PID_DIR = Path("~/.semanticfs").expanduser()
DAEMON_PID_FILE = PID_DIR / "daemon.pid"

def print_banner():
    banner = [
        "[bold cyan]      /\\_/\\ [/bold cyan]      [bold bright_magenta] _____                           _   _      ______  _____[/bold bright_magenta]",
        "[bold cyan]     ( o.o )[/bold cyan]     [bold bright_magenta]/ ____|                         | | (_)    |  ____|/ ____|[/bold bright_magenta]",
        "[bold cyan]      > ^ < [/bold cyan]    [bold bright_magenta]| (___   ___ _ __ ___   __ _ _ __| |_ _  ___| |__  | (___  [/bold bright_magenta]",
        "[bold cyan]     /     \\ [/bold cyan]    [bold bright_magenta]\\___ \\ / _ \\ '_ ` _ \\ / _` | '__| __| |/ __|  __|  \\___ \\ [/bold bright_magenta]",
        "[bold cyan]    (       )[/bold cyan]   [bold bright_magenta] ____) |  __/ | | | | | (_| | |  | |_| | (__| |     ____) |[/bold bright_magenta]",
        "[bold cyan]     `-----' [/bold cyan]   [bold bright_magenta]|_____/ \\___|_| |_| |_|\\__,_|_|   \\__|_|\\___|_|    |_____/[/bold bright_magenta]",
        "                 [bold green]● Local Neural Vector & Context Engine[/bold green] [dim cyan]v0.1.0[/dim cyan]\n"
    ]
    for line in banner:
        console.print(line, highlight=False)

def print_score_bar(score: float) -> str:
    filled = int(score * 10)
    empty = 10 - filled
    return f"[{'█' * filled}{'░' * empty}]"

def get_dir_size_mb(path: Path) -> float:
    """Calculate total size of directory in megabytes."""
    if not path.exists():
        return 0.0
    total = 0
    try:
        for p in path.iterdir():
            if p.is_file():
                total += p.stat().st_size
            elif p.is_dir():
                for subp in p.iterdir():
                    if subp.is_file():
                        total += subp.stat().st_size
    except Exception:
        pass
    return round(total / (1024 * 1024), 2)

def open_path(filepath: str, open_with_code: bool = False):
    if open_with_code:
        console.print(f"\n[bold blue]💻 Opening in VS Code:[/bold blue] {filepath}")
        subprocess.run(["code", filepath], shell=True)
        return

    console.print(f"\n[bold green]🚀 Opening:[/bold green] {filepath}")
    if os.name == 'nt':
        os.startfile(filepath)
    elif sys.platform == 'darwin':
        os.system(f"open '{filepath}'")
    else:
        os.system(f"xdg-open '{filepath}'")

def render_table(results, selected_index: int | None = None) -> Table:
    table = Table(title="SemanticFS Search Results", expand=True)
    table.add_column("Rank", justify="right", style="cyan", width=6)
    table.add_column("Score", style="magenta", width=14)
    table.add_column("Filename / Line Range", style="green")
    table.add_column("Filepath", style="dim")
    table.add_column("Match Snippet", style="yellow")

    for i, res in enumerate(results):
        score_str = print_score_bar(res.score)
        
        line_info = ""
        start_line = getattr(res, "start_line", 1)
        end_line = getattr(res, "end_line", 1)
        if start_line and end_line and (start_line > 1 or end_line > 1):
            line_info = f" [yellow]#L{start_line}-L{end_line}[/yellow]"
            
        filename_display = f"{res.filename}{line_info}"
        snippet = str(res.metadata.get("content_snippet", res.metadata.get("context_window", "")))[:60]
        
        if selected_index is not None and i == selected_index:
            table.add_row(
                f"[bold cyan]➔ {i+1}[/bold cyan]",
                f"[bold cyan]{score_str}[/bold cyan]",
                f"[bold cyan underline]{filename_display}[/bold cyan underline]",
                f"[bold cyan]{res.filepath}[/bold cyan]",
                f"[bold cyan]{snippet}[/bold cyan]"
            )
        else:
            table.add_row(
                str(i + 1),
                score_str,
                filename_display,
                res.filepath,
                snippet
            )
    return table

def interactive_select(results, query: str, open_with_code: bool = False) -> None:
    """Interactive arrow-key menu powered by Rich Live display."""
    if not results or not sys.stdin.isatty():
        return

    total = len(results)
    selected_index = 0

    if os.name == 'nt':
        import msvcrt
        
        console.print("\n[bold cyan]Use ↑/↓ Arrow Keys to select, [Enter] to open, [c] for VS Code, [1-5] quick pick, [q/Esc] to exit:[/bold cyan]\n")
        
        with Live(render_table(results, selected_index), console=console, refresh_per_second=10) as live:
            while True:
                key = msvcrt.getch()
                if key in (b'\r', b'\n'):  # Enter
                    live.stop()
                    open_path(results[selected_index].filepath, open_with_code)
                    return
                elif key in (b'c', b'C'):  # Open in VS Code
                    live.stop()
                    open_path(results[selected_index].filepath, open_with_code=True)
                    return
                elif key in (b'\x1b', b'q', b'Q'):  # Quit
                    live.stop()
                    console.print("[dim]Exited selection.[/dim]")
                    return
                elif key.isdigit():  # Quick select by number
                    idx = int(key.decode('ascii')) - 1
                    if 0 <= idx < total:
                        selected_index = idx
                        live.update(render_table(results, selected_index))
                        live.stop()
                        open_path(results[selected_index].filepath, open_with_code)
                        return
                elif key in (b'\x00', b'\xe0'):  # Arrow keys
                    arrow = msvcrt.getch()
                    if arrow == b'H':  # Up
                        selected_index = (selected_index - 1) % total
                    elif arrow == b'P':  # Down
                        selected_index = (selected_index + 1) % total
                    live.update(render_table(results, selected_index))

    else:
        console.print(render_table(results))
        try:
            choice = IntPrompt.ask("\n[bold cyan]Enter file rank number to open (or 0 to exit)[/bold cyan]", default=0)
            if 1 <= choice <= total:
                open_path(results[choice - 1].filepath, open_with_code)
        except Exception:
            pass

def is_pid_running(pid: int) -> bool:
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        return False

def start_daemon():
    print_banner()
    PID_DIR.mkdir(parents=True, exist_ok=True)
    python_exe = sys.executable

    if DAEMON_PID_FILE.exists():
        pid = int(DAEMON_PID_FILE.read_text().strip())
        if is_pid_running(pid):
            console.print("[yellow]Daemon is already running in background.[/yellow]")
            return
        else:
            DAEMON_PID_FILE.unlink(missing_ok=True)

    proc = subprocess.Popen([python_exe, "-m", "semanticfs.daemon"], cwd="C:/Dev/SemanticFS", creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    DAEMON_PID_FILE.write_text(str(proc.pid))
    console.print(f"[bold green]✔ Ambient Daemon started on demand (PID: {proc.pid})[/bold green]")

def stop_daemon():
    if DAEMON_PID_FILE.exists():
        try:
            pid = int(DAEMON_PID_FILE.read_text().strip())
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            console.print(f"[bold red]✘ Stopped Ambient Daemon (PID: {pid})[/bold red]")
        except Exception as e:
            console.print(f"[dim]Failed to stop daemon: {e}[/dim]")
        finally:
            DAEMON_PID_FILE.unlink(missing_ok=True)
    else:
        console.print("[yellow]No running daemon found.[/yellow]")

def show_status_and_analytics():
    print_banner()
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    linker = FileLinker(config.linker.db_path)

    d_running = DAEMON_PID_FILE.exists() and is_pid_running(int(DAEMON_PID_FILE.read_text().strip()))
    d_status = "[bold green]RUNNING[/bold green]" if d_running else "[bold red]STOPPED[/bold red]"

    file_count = store.count()
    vector_count = file_count
    access_count = linker.get_access_count()
    total_links = linker.get_total_links()
    db_size_mb = get_dir_size_mb(config.storage.db_path)

    table = Table(title="📊 SemanticFS Master System & Vector Analytics", expand=True)
    table.add_column("Category / Metric", style="cyan bold")
    table.add_column("Value / Status", style="green bold", justify="right")
    table.add_column("Description", style="dim")

    table.add_row("Ambient Daemon Status", d_status, "Background filesystem event tracker")
    table.add_row("Total Files Indexed", str(file_count), "Total user files indexed in semantic store")
    table.add_row("Vector Embeddings Stored", str(vector_count), "384-dimensional dense neural vectors generated")
    table.add_row("Neural Vector Model", config.embedding.model_name, "Local transformer model (all-MiniLM-L6-v2)")
    table.add_row("Vector DB Disk Size", f"{db_size_mb} MB", "ChromaDB vector store storage footprint")
    table.add_row("File Accesses Logged", str(access_count), "Total ambient file interactions recorded")
    table.add_row("Co-Access Links Formed", str(total_links), "Calculated implicit file association edges")
    table.add_row("Monitored Directories", str(len(config.watcher.watch_directories)), "Configured workspace watch paths")

    console.print(table)

def run_reindex():
    print_banner()
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    
    console.print("[bold yellow]⚡ Clearing existing vector store and re-indexing all files...[/bold yellow]")
    store.clear()
    
    from semanticfs.daemon import DaemonContext
    daemon_ctx = DaemonContext(config)
    daemon_ctx.initial_scan()
    
    count = store.count()
    console.print(f"[bold green]✔ Re-indexing complete! {count} files vector-indexed.[/bold green]")

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("query_parts", nargs=-1)
@click.option("--limit", "-l", default=5, help="Number of results")
@click.option("--type", "-t", "filetype", help="Filter by file extension")
@click.option("--open", "open_file", is_flag=True, help="Automatically open top result")
@click.option("--code", "open_code", is_flag=True, help="Open top result in VS Code")
@click.option("--stats", "show_stats", is_flag=True, help="Show index statistics")
@click.option("--clear", "clear_index", is_flag=True, help="Clear current index collection")
@click.option("--no-interactive", is_flag=True, help="Disable interactive selection menu")
def main(query_parts: tuple[str, ...], limit: int, filetype: str | None, open_file: bool, open_code: bool, show_stats: bool, clear_index: bool, no_interactive: bool):
    """SemanticFS CLI — Search your files using natural language context."""
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)

    if not query_parts and not (show_stats or clear_index or open_file):
        print_banner()
        console.print("[bold cyan]SemanticFS CLI — Terminal Commands[/bold cyan]\n")
        console.print("  [bold green]sfind <query>[/bold green]         - Search files by natural language context")
        console.print("  [bold green]sfind stats[/bold green]           - Master analytics: daemon status, vectors, DB size, file count")
        console.print("  [bold green]sfind train[/bold green]           - Fine-tune AI model on your local files")
        console.print("  [bold green]sfind reindex[/bold green]         - Force full re-scan & vector re-indexing")
        console.print("  [bold green]sfind start[/bold green]           - Launch Ambient Daemon on demand")
        console.print("  [bold green]sfind stop[/bold green]            - Stop Ambient Daemon")
        console.print("  [bold green]sfind add-dir <path>[/bold green]  - Add a directory to watch list")
        console.print("  [bold green]sfind list-dirs[/bold green]       - List all monitored directories")
        console.print("  [bold green]sfind recent[/bold green]          - Show recently modified files")
        console.print("  [bold green]sfind --clear[/bold green]         - Clear vector index")
        return

    lower_args = set(p.lower() for p in query_parts)

    if "train" in lower_args:
        print_banner()
        from semanticfs.trainer import train_local_model
        train_local_model(epochs=1)
        return
    elif "reindex" in lower_args or "scan" in lower_args:
        run_reindex()
        return
    elif "start" in lower_args:
        start_daemon()
        return
    elif "stop" in lower_args:
        stop_daemon()
        return
    elif "stats" in lower_args or "status" in lower_args or "info" in lower_args or "analytics" in lower_args or "vectors" in lower_args or show_stats:
        show_status_and_analytics()
        return
    elif "add-dir" in lower_args and len(query_parts) > 1:
        new_path = Path(query_parts[1]).resolve()
        if new_path.exists() and new_path.is_dir():
            if new_path not in config.watcher.watch_directories:
                config.watcher.watch_directories.append(new_path)
                config.save()
                console.print(f"[bold green]✔ Added to watch list:[/bold green] {new_path}")
            else:
                console.print(f"[yellow]Directory already monitored:[/yellow] {new_path}")
        else:
            console.print(f"[red]Directory does not exist:[/red] {new_path}")
        return
    elif "list-dirs" in lower_args:
        table = Table(title="Monitored Directories")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Directory Path", style="green")
        for i, d in enumerate(config.watcher.watch_directories):
            table.add_row(str(i + 1), str(d))
        console.print(table)
        return
    elif "recent" in lower_args:
        items = store.get_all(limit=10)
        table = Table(title="Recently Modified Files")
        table.add_column("Filename", style="green")
        table.add_column("Filepath", style="dim")
        table.add_column("Context Window", style="yellow")
        for item in items[:10]:
            table.add_row(item.get("filename", ""), item.get("filepath", ""), item.get("context_window", ""))
        console.print(table)
        return

    if clear_index:
        store.clear()
        console.print("[bold green]Index collection cleared successfully.[/bold green]")
        return

    query = " ".join(query_parts)
    
    embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)
    query_embedding = embedder.embed_text(query)
    
    filters = {}
    if filetype:
        filters["filetype"] = filetype if filetype.startswith(".") else f".{filetype}"
        
    results = store.search(query_embedding, query_text=query, n_results=limit, filters=filters if filters else None)
    
    if not results:
        console.print(f"[yellow]No results found for:[/yellow] '{query}'")
        return

    if open_file or open_code:
        console.print(render_table(results))
        open_path(results[0].filepath, open_with_code=open_code)
    elif no_interactive:
        console.print(render_table(results))
    else:
        interactive_select(results, query, open_with_code=open_code)

if __name__ == "__main__":
    main()
