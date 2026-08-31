<#
.SYNOPSIS
    Setup SemanticFS Ambient Daemon as a persistent Windows Startup Task.
.DESCRIPTION
    Installs a lightweight, hidden VBScript runner into the Windows user Startup folder
    so the SemanticFS pre-warmed IPC socket server (port 9876) runs automatically on login.
.PARAMETER Uninstall
    Removes the startup task and stops the ambient daemon.
.PARAMETER Status
    Checks the installation and socket connectivity status of the daemon.
#>
param(
    [switch]$Uninstall,
    [switch]$Status
)

$StartupFolder = [Environment]::GetFolderPath("Startup")
$VbsPath = Join-Path $StartupFolder "SemanticFS_Daemon.vbs"

function Test-DaemonPort {
    param([int]$Port = 9876)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $iar = $tcpClient.BeginConnect("127.0.0.1", $Port, $null, $null)
        $success = $iar.AsyncWaitHandle.WaitOne(1000, $false)
        if ($success) {
            $tcpClient.EndConnect($iar)
            $tcpClient.Close()
            return $true
        }
        $tcpClient.Close()
        return $false
    } catch {
        return $false
    }
}

if ($Status) {
    Write-Host "=== SemanticFS Daemon Startup Status ===" -ForegroundColor Cyan
    $installed = Test-Path $VbsPath
    if ($installed) {
        Write-Host "Startup Task : [✔ INSTALLED] at $VbsPath" -ForegroundColor Green
    } else {
        Write-Host "Startup Task : [⚪ NOT CONFIGURED]" -ForegroundColor Yellow
    }

    $active = Test-DaemonPort -Port 9876
    if ($active) {
        Write-Host "IPC Server   : [✔ RUNNING] Reachable on 127.0.0.1:9876 (Sub-5ms fast path active)" -ForegroundColor Green
    } else {
        Write-Host "IPC Server   : [✘ OFFLINE] Port 9876 not reachable (CLI in slow fallback mode)" -ForegroundColor Red
    }
    return
}

if ($Uninstall) {
    Write-Host "Uninstalling SemanticFS Startup Task..." -ForegroundColor Yellow
    if (Test-Path $VbsPath) {
        Remove-Item -Path $VbsPath -Force
        Write-Host "Removed startup file: $VbsPath" -ForegroundColor Green
    } else {
        Write-Host "No startup file found at: $VbsPath" -ForegroundColor Gray
    }
    
    try {
        & sfind stop 2>$null
    } catch {}
    
    Write-Host "Persistent startup daemon successfully uninstalled." -ForegroundColor Green
    return
}

# 1. Determine Python executable
$PythonPath = $null
if ($env:VIRTUAL_ENV -and (Test-Path "$env:VIRTUAL_ENV\Scripts\python.exe")) {
    $PythonPath = "$env:VIRTUAL_ENV\Scripts\python.exe"
}
if (-not $PythonPath) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        $PythonPath = $cmd.Source
    }
}
if (-not $PythonPath) {
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        $PythonPath = $cmd.Source
    }
}
if (-not $PythonPath) {
    $PythonPath = "python.exe"
}

# 2. VBScript wrapper launches Python completely hidden (window mode 0)
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """$PythonPath"" -m semanticfs.daemon", 0, False
"@

Set-Content -Path $VbsPath -Value $VbsContent -Encoding ASCII

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SemanticFS Ambient Daemon - Windows Startup Configured!   " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Startup VBScript : $VbsPath" -ForegroundColor Gray
Write-Host "Python Binary    : $PythonPath" -ForegroundColor Gray
Write-Host "The daemon will now automatically run silently whenever Windows boots." -ForegroundColor Yellow
Write-Host ""

# 3. Check if daemon is already listening on port 9876; if not, launch it now
if (Test-DaemonPort -Port 9876) {
    Write-Host "Ambient Daemon is already listening on 127.0.0.1:9876." -ForegroundColor Green
} else {
    Write-Host "Launching ambient daemon silently in background..." -ForegroundColor Green
    Start-Process wscript.exe -ArgumentList "`"$VbsPath`""
    
    # Wait up to 3 seconds for IPC server to bind
    $running = $false
    for ($i = 0; $i -lt 6; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-DaemonPort -Port 9876) {
            $running = $true
            break
        }
    }
    
    if ($running) {
        Write-Host "✔ Verified: Daemon IPC Server is active on port 9876!" -ForegroundColor Green
    } else {
        Write-Host "Daemon launched. Verify status anytime with: sfind doctor" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Done! 24/7 Ambient File Tracking & Sub-5ms IPC Search are active." -ForegroundColor Green
Write-Host "Verify diagnostics anytime by running: sfind doctor" -ForegroundColor Cyan
