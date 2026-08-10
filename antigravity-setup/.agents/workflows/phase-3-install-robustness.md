# Phase 3 — Installation & environment robustness

**Objective:** Make installation fail loudly and helpfully instead of silently, and document real system requirements.

Task hints:
- Add a **System Requirements** section: approximate RAM/disk needed to index N files, model download sizes (bge-small, CLIP if the `vision` extra is installed), supported OS (be honest if it's currently Windows-only given the Explorer/Clipboard integration — don't imply cross-platform if it isn't).
- Tesseract is a system-level binary, not a pip package — `pip install -e ".[ocr]"` will succeed while OCR silently fails without it. Add a startup check that detects a missing Tesseract binary and prints a clear install instruction (with OS-specific commands) instead of a stack trace.
- Same treatment for any other non-pip system dependency (Rust toolchain for `native_core`, if that's required for the core install or only for an optional native-acceleration path — clarify which).
- Add a `sfind doctor` (or similar) command that checks all dependencies and reports what's missing/misconfigured — genuinely useful and a nice portfolio signal (shows you thought about real-world failure modes, not just the happy path).

**Acceptance criteria:**
- A missing system dependency produces a one-line actionable error, not a Python traceback.
- README's install section lists every non-pip dependency explicitly.

---
