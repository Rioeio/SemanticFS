# Setup SemanticFS Ambient Daemon as a Windows Startup Task
# Runs 24/7 silently in the background without opening any command window

$StartupFolder = [Environment]::GetFolderPath("Startup")
$VbsPath = Join-Path $StartupFolder "SemanticFS_Daemon.vbs"

# Determine Python executable
$PythonPath = (Get-Command python).Source
if (-not $PythonPath) {
    $PythonPath = "python.exe"
}

# VBScript wrapper launches Python completely hidden (window mode 0)
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """$PythonPath"" -m semanticfs.daemon", 0, False
"@

Set-Content -Path $VbsPath -Value $VbsContent -Encoding ASCII

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SemanticFS Ambient Daemon - Windows Startup Installed!    " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Startup VBScript: $VbsPath" -ForegroundColor Gray
Write-Host "The daemon will now automatically run silently whenever Windows boots." -ForegroundColor Yellow
Write-Host ""
Write-Host "Launching daemon silently now for current session..." -ForegroundColor Green

# Start it immediately via wscript.exe
Start-Process wscript.exe -ArgumentList "`"$VbsPath`""

Write-Host "Done! 24/7 Ambient File Tracking is active." -ForegroundColor Green
