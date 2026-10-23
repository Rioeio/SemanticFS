@echo off
title SemanticFS Web UI
echo ==========================================
echo        SemanticFS Web Dashboard           
echo ==========================================

python -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Missing required dependency 'uvicorn'.
    echo pip install -e ".[ui]"
    exit /b 1
)

if not exist "%~dp0..\frontend\dist\index.html" (
    echo [!] frontend/dist missing. Building frontend with pnpm...
    pnpm --dir "%~dp0..\frontend" build
    if %ERRORLEVEL% neq 0 (
        echo [!] Failed to build frontend.
        exit /b 1
    )
)

echo Starting SemanticFS Web UI on http://127.0.0.1:8000...
start http://127.0.0.1:8000
python -m uvicorn semanticfs.api:app --host 127.0.0.1 --port 8000
pause
