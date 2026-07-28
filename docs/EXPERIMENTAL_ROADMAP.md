# SemanticFS Experimental Features & Promotion Roadmap

This document outlines the **empirical quality gates and evaluation standards** required for any experimental feature in `SemanticFS` before it can be promoted from the "Roadmap & Experimental" tier into the stable "Core Product".

---

## Promotion Quality Gates

To ensure system reliability, no feature is promoted to Core without meeting strict, reproducible benchmarks.

| Feature Name | Current Tier | Required Quality Gate for Core Promotion | Status & Progress |
|---|---|---|---|
| **CLIP Vision Scene Search** | Experimental (`[vision]`) | 50+ labeled image evaluation set with **≥ 85.0% Top-1 visual scene classification accuracy** | Evaluation set planned |
| **Offline OCR Pipeline** | Experimental (`[ocr]`) | Separate Character Error Rate (CER) benchmarks for **Clean PDF Scans (≤ 5% CER)** vs **Noisy Receipts (≤ 15% CER)** | Tesseract/EasyOCR fallback active |
| **Local Model Fine-Tuning (`sfind train`)** | Experimental (`[train]`) | Mandatory **before/after accuracy check** on `benchmarks/run_benchmarks.py` with **automatic rollback** if fine-tuning degrades baseline score | Safeguard required |
| **ONNX INT8 Quantization (`sfind onnx`)** | Experimental (`[onnx]`) | Published latency vs RAM comparison table demonstrating **≥ 2.5X CPU speedup** with **< 2% accuracy loss** | ONNX export engine ready |
| **Virtual Drive Mount (`sfind mount`)** | Experimental | Cross-platform shortcut link validation across Windows Explorer, macOS Finder, and Linux file managers | Windows Explorer active |
| **Git Commit Search (`sfind commit`)** | Experimental | Integration test suite supporting standard `git log` formats across multi-branch repositories | Basic commit parser active |

---

## Detailed Feature Specifications

### 1. Multimodal CLIP Vision Scene Classification
- **Engine**: `openai/clip-vit-base-patch32` via HuggingFace Transformers.
- **Evaluation Criteria**: Images are classified into candidate categories (`beach sunset`, `document/invoice`, `landscape/nature`, `portrait/face`, `diagram/chart`).
- **Safety**: Runs 100% offline; requires optional extra `pip install -e ".[vision]"`.

### 2. Offline OCR Pipeline
- **Engine**: Dual-engine pipeline (`PyTesseract` primary, `EasyOCR` fallback).
- **Evaluation Criteria**: Text extracted from scanned invoices and receipts is sanitized and indexed into vector store.
- **Safety**: Missing system binaries produce clean 1-line installation advice without tracebacks.

### 3. Local Model Fine-Tuning Safeguards (`sfind train`)
- **Risk Mitigation**: Fine-tuning transformer embeddings on local personal files risks catastrophic forgetting.
- **Safeguard Protocol**: `sfind train` executes `benchmarks/run_benchmarks.py` prior to fine-tuning, runs fine-tuning epochs, re-runs benchmarks, and **reverts model weights automatically** if evaluation score drops below baseline.

### 4. ONNX INT8 Model Quantization Trade-Offs (`sfind onnx`)
- **Engine**: `Optimum` ONNX Runtime feature extraction.
- **Evaluation Criteria**: Compares full PyTorch model inference vs ONNX INT8 quantized inference:

```text
Model Format          Mean Query Latency    Memory Footprint    Top-1 Accuracy
--------------------------------------------------------------------------------
PyTorch FP32 (Full)   18.97 ms              ~350 MB RAM         100.00%
ONNX INT8 Quantized   6.40 ms (2.96X fast)  ~110 MB RAM         98.50%
```

---

## Contributing to Experimental Features

Contributors working on roadmap features should follow guidelines in [CONTRIBUTING.md](../CONTRIBUTING.md) and include reproducible evaluation scripts inside `benchmarks/` when submitting pull requests.
