# SemanticFS Web UI Launcher
# Usage: ./scripts/launch_ui.ps1 [-Dev]
param (
    [switch]$Dev
)

$Host.UI.RawUI.WindowTitle = "SemanticFS Web UI"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       SemanticFS Web Dashboard           " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 0. Check that uvicorn is importable
$null = python -c "import uvicorn" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Missing required dependency 'uvicorn'." -ForegroundColor Red
    Write-Host 'pip install -e ".[ui]"' -ForegroundColor Yellow
    exit 1
}

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

# 2. Check if frontend/dist is missing
$frontendDir = Join-Path $PSScriptRoot "../frontend"
$distIndex = Join-Path $frontendDir "dist/index.html"
if (-not (Test-Path $distIndex)) {
    Write-Host "[!] frontend/dist missing. Building frontend with pnpm..." -ForegroundColor Yellow
    pnpm --dir $frontendDir build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Failed to build frontend." -ForegroundColor Red
        exit 1
    }
}

if ($Dev) {
    Write-Host "[✔] Starting Frontend in Live Development Mode (Vite HMR on http://localhost:5173)..." -ForegroundColor Green
    Set-Location -Path $frontendDir
    pnpm dev --port 5173
} else {
    Write-Host "[✔] Starting Unified Web UI & API Server on http://127.0.0.1:8000..." -ForegroundColor Green
    Start-Process "http://127.0.0.1:8000"
    python -m uvicorn semanticfs.api:app --host 127.0.0.1 --port 8000
}
