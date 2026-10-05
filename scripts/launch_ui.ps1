# SemanticFS Web UI Launcher
# Usage: ./scripts/launch_ui.ps1 [-Dev]
param (
    [switch]$Dev
)

$Host.UI.RawUI.WindowTitle = "SemanticFS Web UI"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       SemanticFS Web Dashboard           " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check if background ambient daemon is running on port 9876
$daemonRunning = $false
try {
    $tcp = Get-NetTCPConnection -LocalPort 9876 -State Listen -ErrorAction SilentlyContinue
    if ($tcp) { $daemonRunning = $true }
} catch {}

if (-not $daemonRunning) {
    Write-Host "[!] Ambient daemon offline. Launching daemon in background..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "-m semanticfs.daemon" -WindowStyle Hidden
    Start-Sleep -Seconds 2
} else {
    Write-Host "[✔] Background daemon active on port 9876." -ForegroundColor Green
}

if ($Dev) {
    Write-Host "[✔] Starting Frontend in Live Development Mode (Vite HMR on http://localhost:5173)..." -ForegroundColor Green
    Set-Location -Path "$PSScriptRoot/../frontend"
    pnpm dev --port 5173
} else {
    Write-Host "[✔] Starting Unified Web UI & API Server on http://127.0.0.1:8000..." -ForegroundColor Green
    Start-Process "http://127.0.0.1:8000"
    python -m uvicorn semanticfs.api:app --host 127.0.0.1 --port 8000
}
