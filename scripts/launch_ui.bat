@echo off
title SemanticFS Web UI
echo ==========================================
echo        SemanticFS Web Dashboard           
echo ==========================================

echo Starting SemanticFS Web UI on http://127.0.0.1:8000...
start http://127.0.0.1:8000
python -m uvicorn semanticfs.api:app --host 127.0.0.1 --port 8000
pause
