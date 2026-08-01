# Contributing to SemanticFS

Thank you for your interest in contributing to **SemanticFS**! This document provides guidelines and instructions for setting up your local development environment, running tests, and submitting pull requests.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.11** or higher.
- **Git** version 2.25+.
- **Tesseract OCR** (Optional; required for testing OCR capabilities):
  - **Windows**: `winget install UB-Mannheim.TesseractOCR`
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt install tesseract-ocr`

### 2. Local Environment Setup
Clone the repository and install in editable mode with development and feature extras:

```bash
git clone https://github.com/Rioeio/SemanticFS.git
cd SemanticFS

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install core package with dev and feature extras
pip install -e ".[dev,all]"

# Install pre-commit hooks for automated ruff & mypy checks
pip install pre-commit
pre-commit install
```

---

## 🧪 Running Tests & Diagnostics

### System Diagnostics
Run the automated environment doctor to verify dependencies and paths:
```bash
sfind doctor
```

### PyTest Suite
Run the automated test suite locally:
```bash
pytest
```

### Reproducible Benchmark Suite
Run the portable benchmark runner:
```bash
python benchmarks/run_benchmarks.py
```

---

## 📐 Coding Conventions & Guidelines

1. **Type Annotations**: All python modules must use `from __future__ import annotations` and explicit type hints.
2. **Error Handling**: Non-pip optional dependencies (e.g. `tesseract`, `torch`, `transformers`) must fail gracefully with actionable advice rather than unhandled tracebacks.
3. **No Hardcoded Absolute Paths**: Always use dynamic path resolution (`Path.home()`, `Path(__file__).parent`).

---

## 📬 Submitting a Pull Request

1. Fork the repository and create a feature branch (`git checkout -b feature/amazing-feature`).
2. Ensure all tests (`pytest`) and diagnostics (`sfind doctor`) pass.
3. Commit your changes with clear messages (`git commit -m "Add amazing feature"`).
4. Push to your branch and open a Pull Request against `main`.
