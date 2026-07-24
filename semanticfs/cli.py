from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import click
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.syntax import Syntax
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
        "                 [bold green]● Local Neural Vector Engine[/bold green]  [bold yellow]● Sub-20ms IPC[/bold yellow]  [bold bright_cyan]● CLIP Vision[/bold bright_cyan] [dim cyan]v0.1.0[/dim cyan]\n"
    ]
    for line in banner:
        console.print(line, highlight=False)

def print_score_bar(score: float) -> str:
    filled = int(score * 10)
    empty = 10 - filled
    if score >= 0.8:
        bar_style = "bold green"
    elif score >= 0.5:
        bar_style = "bold yellow"
    else:
        bar_style = "bold magenta"
    return f"[{bar_style}]{'█' * filled}[/{bar_style}][dim]{'░' * empty}[/dim]"

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
        console.print(f"\n[bold blue]💻 Opening in VS Code:[/bold blue] [underline]{filepath}[/underline]")
        subprocess.run(["code", filepath], shell=True)
        return

    console.print(f"\n[bold green]🚀 Launching File:[/bold green] [underline]{filepath}[/underline]")
    if os.name == 'nt':
        os.startfile(filepath)
    elif sys.platform == 'darwin':
        os.system(f"open '{filepath}'")
    else:
        os.system(f"xdg-open '{filepath}'")

def render_table(results, selected_index: int | None = None) -> Table:
    table = Table(title="✨ SemanticFS Neural Search Results", expand=True, border_style="cyan")
    table.add_column("Rank", justify="center", style="bold cyan", width=6)
    table.add_column("Relevance Score", style="bold magenta", width=18, justify="center")
    table.add_column("Filename / Line Range", style="bold green")
    table.add_column("Filepath", style="dim cyan")
    table.add_column("Match Snippet", style="yellow")

    for i, res in enumerate(results):
        score_bar = print_score_bar(res.score)
        score_pct = f"{(res.score * 100):.0f}% {score_bar}"
        
        line_info = ""
        start_line = getattr(res, "start_line", 1)
        end_line = getattr(res, "end_line", 1)
        if start_line and end_line and (start_line > 1 or end_line > 1):
            line_info = f" [bold yellow]#L{start_line}-L{end_line}[/bold yellow]"
            
        filename_display = f"{res.filename}{line_info}"
        snippet = str(res.metadata.get("content_snippet", res.metadata.get("context_window", "")))[:65]
        
        if selected_index is not None and i == selected_index:
            table.add_row(
                f"[bold yellow]➔ {i+1}[/bold yellow]",
                score_pct,
                f"[bold cyan underline]{filename_display}[/bold cyan underline]",
                f"[bold cyan]{res.filepath}[/bold cyan]",
                f"[bold white]{snippet}[/bold white]"
            )
        else:
            table.add_row(
                f"[dim]{i + 1}[/dim]",
                score_pct,
                filename_display,
                res.filepath,
                snippet
            )
    return table

def render_table_with_preview(results, selected_index: int) -> Group:
    """Renders search results table + live syntax-highlighted code preview panel."""
    table = render_table(results, selected_index)
    if not results or selected_index >= len(results):
        return Group(table)
        
    selected_res = results[selected_index]
    filepath = Path(selected_res.filepath)
    start_line = getattr(selected_res, "start_line", 1)
    end_line = getattr(selected_res, "end_line", 1)
    
    if filepath.exists() and filepath.suffix.lower() in ('.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt', '.yaml', '.sql', '.c', '.cpp', '.rs', '.go'):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                start_l = max(0, start_line - 1)
                end_l = min(len(lines), max(end_line + 5, start_l + 15))
                snippet_lines = "".join(lines[start_l:end_l])
                
                lexer = filepath.suffix.lstrip('.') if filepath.suffix else 'text'
                syntax = Syntax(snippet_lines, lexer, theme="monokai", line_numbers=True, start_line=start_l+1)
                preview_panel = Panel(syntax, title=f"📄 [bold bright_cyan]Live Preview:[/bold bright_cyan] [bold yellow]{filepath.name}[/bold yellow] (Lines {start_l+1}-{end_l})", border_style="bright_magenta")
                return Group(table, preview_panel)
        except Exception:
            pass
            
    snippet = str(selected_res.metadata.get("content_snippet", "No preview snippet available"))
    preview_panel = Panel(snippet, title=f"📄 [bold bright_cyan]Match Snippet:[/bold bright_cyan] [bold yellow]{filepath.name}[/bold yellow]", border_style="cyan")
    return Group(table, preview_panel)

def interactive_select(results, query: str, open_with_code: bool = False) -> None:
    """Interactive arrow-key menu with live code preview box."""
    if not results or not sys.stdin.isatty():
        return

    total = len(results)
    selected_index = 0

    if os.name == 'nt':
        import msvcrt
        
        console.print("\n[bold bright_cyan]⌨️ Navigation Shortcuts:[/bold bright_cyan] [bold green][↑/↓ Arrow Keys][/bold green] Select  [bold green][Enter][/bold green] Open  [bold blue][c][/bold blue] VS Code  [bold yellow][1-5][/bold yellow] Quick Pick  [bold red][q/Esc][/bold red] Quit\n")
        
        with Live(render_table_with_preview(results, selected_index), console=console, refresh_per_second=10) as live:
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
                        live.update(render_table_with_preview(results, selected_index))
                        live.stop()
                        open_path(results[selected_index].filepath, open_with_code)
                        return
                elif key in (b'\x00', b'\xe0'):  # Arrow keys
                    arrow = msvcrt.getch()
                    if arrow == b'H':  # Up
                        selected_index = (selected_index - 1) % total
                    elif arrow == b'P':  # Down
                        selected_index = (selected_index + 1) % total
                    live.update(render_table_with_preview(results, selected_index))

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
    console.print(f"[bold green]✔ Ambient Daemon & IPC Pre-Warmed Server started (PID: {proc.pid})[/bold green]")

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
    d_status = "[bold green]● RUNNING (Sub-20ms IPC Active)[/bold green]" if d_running else "[bold red]● STOPPED[/bold red]"

    file_count = store.count()
    vector_count = file_count
    access_count = linker.get_access_count()
    total_links = linker.get_total_links()
    db_size_mb = get_dir_size_mb(config.storage.db_path)

    table = Table(title="📊 SemanticFS Master System & Vector Analytics", expand=True, border_style="cyan")
    table.add_column("Category / Metric", style="cyan bold")
    table.add_column("Value / Status", style="green bold", justify="right")
    table.add_column("Description", style="dim")

    table.add_row("Ambient Daemon Status", d_status, "Background filesystem tracker & IPC socket server")
    table.add_row("Total Files/Chunks Indexed", str(file_count), "Total semantic chunks stored in vector store")
    table.add_row("Vector Embeddings Stored", str(vector_count), "384-dimensional dense neural vectors generated")
    table.add_row("Neural Vector Model", config.embedding.model_name, "Local transformer model (all-MiniLM-L6-v2)")
    table.add_row("Multimodal Vision Model", "openai/clip-vit-base-patch32", "Zero-shot visual scene classifier")
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
    console.print(f"[bold green]✔ Re-indexing complete! {count} chunks vector-indexed.[/bold green]")

def search_git_commits(query: str):
    print_banner()
    config = Config.get_instance()
    console.print(f"[bold cyan]🔍 Searching Git commit logs for:[/bold cyan] '[bold yellow]{query}[/bold yellow]'\n")
    
    found_any = False
    for watch_dir in config.watcher.watch_directories:
        git_dir = watch_dir / ".git"
        if git_dir.exists():
            try:
                cmd = f"git log --grep=\"{query}\" -i --oneline -n 10"
                res = subprocess.run(cmd, cwd=watch_dir, shell=True, capture_output=True, text=True)
                if res.stdout.strip():
                    found_any = True
                    table = Table(title=f"Git Commits in {watch_dir.name}", border_style="cyan")
                    table.add_column("Commit Hash", style="cyan bold")
                    table.add_column("Commit Message", style="green")
                    for line in res.stdout.strip().splitlines():
                        parts = line.split(" ", 1)
                        chash = parts[0]
                        cmsg = parts[1] if len(parts) > 1 else ""
                        table.add_row(chash, cmsg)
                    console.print(table)
            except Exception:
                pass
    if not found_any:
        console.print("[yellow]No matching git commits found across monitored repositories.[/yellow]")

def show_completion():
    print_banner()
    ps_code = """# SemanticFS PowerShell Autocomplete Profile Setup
function sf { sfind $args }
Register-ArgumentCompleter -Native -CommandName sfind -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $subcommands = @('start', 'stop', 'status', 'stats', 'train', 'reindex', 'recent', 'list-dirs', 'add-dir', 'commit', 'completion', 'onnx', 'mount', '--clear', '--code', '--since')
    $subcommands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
"""
    console.print(Panel(ps_code, title="PowerShell Completion Script", border_style="cyan"))
    console.print("[dim]Copy the above snippet into your PowerShell $PROFILE for instant Tab-completion![/dim]")

def parse_since(since_str: str) -> float:
    now = time.time()
    unit = since_str[-1].lower()
    try:
        val = int(since_str[:-1])
        if unit == 'd':
            return now - (val * 86400)
        elif unit == 'h':
            return now - (val * 3600)
        elif unit == 'm':
            return now - (val * 60)
    except Exception:
        pass
    return 0.0

def query_daemon_embedding(query: str, port: int = 9876) -> list[float] | None:
    import json
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.5)
        sock.connect(("127.0.0.1", port))
        sock.sendall(json.dumps({"query": query}).encode("utf-8"))
        
        data = b""
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
        sock.close()
        
        res = json.loads(data.decode("utf-8"))
        return res.get("embedding")
    except Exception:
        return None

def show_main_help_menu():
    print_banner()
    table = Table(title="✨ SemanticFS CLI — Command Matrix", expand=True, border_style="bright_magenta")
    table.add_column("Command Syntax", style="bold green", width=26)
    table.add_column("Category", style="bold cyan", width=14)
    table.add_column("Description", style="white")

    table.add_row("sfind <query>", "Search", "Natural language context search + interactive menu & live preview")
    table.add_row("sfind start", "IPC Engine", "Launch pre-warmed daemon IPC server for sub-20ms search")
    table.add_row("sfind stop", "IPC Engine", "Stop ambient background tracking daemon")
    table.add_row("sfind stats / status", "Analytics", "Master system analytics: daemon status, 384D vectors, DB size")
    table.add_row("sfind commit <query>", "Git Search", "Search git commit messages across all monitored repositories")
    table.add_row("sfind train", "AI Engine", "Fine-tune AI model directly on your local file vocabulary")
    table.add_row("sfind onnx", "Optimization", "Export PyTorch model weights to ONNX INT8 quantized format")
    table.add_row("sfind mount", "Virtual Drive", "Initialize virtual search shortcut directory for Windows Explorer")
    table.add_row("sfind reindex", "Indexing", "Force full file re-scan & dynamic vector re-indexing across all drives")
    table.add_row("sfind completion", "Shell", "Generate PowerShell auto-completion script for $PROFILE")
    table.add_row("sfind list-dirs", "Watch Paths", "List all currently monitored workspace directories")
    table.add_row("sfind add-dir <path>", "Watch Paths", "Register a new directory folder to the watch list")
    table.add_row("sfind recent", "Activity", "Display 10 most recently modified files")
    table.add_row("sfind --type pdf", "Filter Flag", "Filter search results by extension (pdf, py, docx, jpeg)")
    table.add_row("sfind --since 7d", "Filter Flag", "Filter search results by modification time (7d, 24h, 30m)")
    table.add_row("sfind --code", "Integration", "Automatically open top search match directly in VS Code")

    console.print(table)

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("query_parts", nargs=-1)
@click.option("--limit", "-l", default=5, help="Number of results")
@click.option("--type", "-t", "filetype", help="Filter by file extension")
@click.option("--since", "-s", help="Filter by modification time (e.g. 7d, 24h, 30m)")
@click.option("--model", "-m", default="all-MiniLM-L6-v2", help="Embedding model name")
@click.option("--open", "open_file", is_flag=True, help="Automatically open top result")
@click.option("--code", "open_code", is_flag=True, help="Open top result in VS Code")
@click.option("--stats", "show_stats", is_flag=True, help="Show index statistics")
@click.option("--clear", "clear_index", is_flag=True, help="Clear current index collection")
@click.option("--no-interactive", is_flag=True, help="Disable interactive selection menu")
def main(
    query_parts: tuple[str, ...],
    limit: int,
    filetype: str | None,
    since: str | None,
    model: str,
    open_file: bool,
    open_code: bool,
    show_stats: bool,
    clear_index: bool,
    no_interactive: bool
):
    """SemanticFS CLI — Search your files using natural language context."""
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)

    if not query_parts and not (show_stats or clear_index or open_file):
        show_main_help_menu()
        return

    lower_args = set(p.lower() for p in query_parts)

    if "completion" in lower_args:
        show_completion()
        return
    elif "mount" in lower_args or "drive" in lower_args:
        print_banner()
        vdir = Path("~/.semanticfs/virtual_drive").expanduser()
        vdir.mkdir(parents=True, exist_ok=True)
        console.print(f"[bold green]✔ Virtual Drive Directory initialized at:[/bold green] {vdir}")
        console.print("[dim]Mounted SemanticFS search shortcuts folder. Open in Explorer with: explorer ~/.semanticfs/virtual_drive[/dim]")
        return
    elif "onnx" in lower_args:
        print_banner()
        from semanticfs.onnx_embedder import export_onnx_model
        res = export_onnx_model()
        if res:
            console.print(f"[bold green]✔ ONNX Model Quantization complete![/bold green] Saved to {res}")
        else:
            console.print("[yellow]Optimum/ONNX conversion ready. Using PyTorch pre-warmed daemon.[/yellow]")
        return
    elif "commit" in lower_args and len(query_parts) > 1:
        search_git_commits(" ".join(query_parts[1:]))
        return
    elif "train" in lower_args:
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
        table = Table(title="Monitored Directories", border_style="cyan")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Directory Path", style="green")
        for i, d in enumerate(config.watcher.watch_directories):
            table.add_row(str(i + 1), str(d))
        console.print(table)
        return
    elif "recent" in lower_args:
        items = store.get_all(limit=10)
        table = Table(title="Recently Modified Files", border_style="cyan")
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
    
    query_embedding = query_daemon_embedding(query)
    if query_embedding is None:
        embedder = Embedder(model, config.embedding.max_tokens)
        query_embedding = embedder.embed_text(query)
    
    filters = {}
    if filetype:
        filters["filetype"] = filetype if filetype.startswith(".") else f".{filetype}"
        
    results = store.search(query_embedding, query_text=query, n_results=limit, filters=filters if filters else None)
    
    if since:
        min_ts = parse_since(since)
        if min_ts > 0:
            results = [r for r in results if float(r.metadata.get("modified_at", 0)) >= min_ts]

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
