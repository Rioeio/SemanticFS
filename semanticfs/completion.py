from __future__ import annotations

from rich.console import Console

console = Console()

POWERSHELL_COMPLETION = """
# SemanticFS PowerShell Completion Script
Register-ArgumentCompleter -Native -CommandName sfind -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $commands = @(
        "search", "start", "stop", "status", "reindex", "purge", "doctor",
        "collection", "mount", "train", "onnx", "commit", "ui", "completion"
    )
    $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
"""

BASH_COMPLETION = """
# SemanticFS Bash Completion Script
_sfind_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmds="search start stop status reindex purge doctor collection mount train onnx commit ui completion"
    COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
}
complete -F _sfind_completion sfind
"""

ZSH_COMPLETION = """
#compdef sfind
_sfind() {
    local -a commands
    commands=(
        'search:Search files using natural language'
        'start:Start ambient background daemon'
        'stop:Stop ambient background daemon'
        'status:Show vector index status and analytics'
        'reindex:Clear and rebuild full vector index'
        'purge:Delete all vector database storage'
        'doctor:Run environment diagnostic check'
        'collection:Manage virtual smart collections'
        'mount:Mount virtual drive search shortcuts'
        'train:Fine-tune local neural embedding model'
        'onnx:Export PyTorch model to ONNX format'
        'commit:Search git commit logs'
        'ui:Launch Web Node Graph Dashboard'
        'completion:Generate shell auto-completion script'
    )
    _describe -t commands 'sfind commands' commands
}
_sfind "$@"
"""

def generate_completion(shell: str = "powershell") -> None:
    """Generate shell completion script."""
    sh = shell.lower()
    if sh in ("powershell", "ps", "pwsh"):
        console.print(POWERSHELL_COMPLETION.strip())
    elif sh == "bash":
        console.print(BASH_COMPLETION.strip())
    elif sh == "zsh":
        console.print(ZSH_COMPLETION.strip())
    else:
        console.print(f"[yellow]Unknown shell:[/yellow] '{shell}'. Supported: powershell, bash, zsh.")
