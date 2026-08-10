# Phase 2 — Scope split: core product vs. roadmap

**Objective:** Split the ~30-command feature surface into a small, reliable "core" product and a clearly labeled "experimental/roadmap" tier, without deleting any code.

Task hints:
- **Core tier** (what ships and is benchmarked): natural-language + operator search (`sfind <query>`), `jump`, `tag`, `collection create/list`, `duplicates`, daemon `start/stop/status`, `reindex`, `recent`, `list-dirs`/`add-dir`, the interactive terminal UI and its action keys.
- **Experimental/roadmap tier** (present but clearly flagged, not benchmarked yet): CLIP vision scene search, OCR pipeline, git commit search, `sfind train` (local fine-tuning), `sfind onnx` export, `sfind model` (the ASCII visualizer), virtual drive mount.
- Implement this as **optional install extras** so it's structurally enforced, not just a README note. `pyproject.toml` already has a `train` extra (`datasets`, `accelerate`) — extend the same pattern: add `vision = ["transformers", "torch", "pillow"]` and `ocr = ["pytesseract", "easyocr", "pillow"]` and `onnx = ["optimum[onnxruntime]", "transformers"]` groups. These are real, confirmed-missing dependencies — `vision.py` and `ocr.py` are genuinely wired into `embedder.py`'s indexing path today, so right now a clean `pip install -e .` leaves those code paths unable to import their libraries. `pip install -e .` should stay core-only; `pip install -e ".[vision,ocr,onnx,train]"` pulls in everything.
- While in `onnx_embedder.py`: it defaults to exporting `all-MiniLM-L6-v2`, while the rest of the system (embedder, docs, architecture diagram) is built around `bge-small-en-v1.5`. Either make this intentional and documented (e.g. "we export a smaller distilled model for the ONNX path because X") or make it consistent with the primary model.
- Restructure the README: "Core Features" section (accurate, benchmarked, stable) then a separate "Roadmap / Experimental" section for the rest — same content, honest framing. Move the ASCII visualizer to a "fun extras" callout, not the main feature list.
- Group the CLI surface into subcommand families where it makes sense (you already do this for `collection` — extend the pattern, e.g. `sfind daemon start/stop/status` instead of three bare top-level verbs) to keep `sfind --help` readable as the surface grows.

**Acceptance criteria:**
- `pip install -e .` (no extras) installs and runs full core search with no Tesseract/CLIP/torch dependency errors.
- README clearly separates "works today, benchmarked" from "in progress."
- `sfind --help` groups related commands instead of listing 30 flat verbs.

---
