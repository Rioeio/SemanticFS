# Phase 4 — Storage, privacy & security documentation

**Objective:** Back up the "Privacy & Offline Isolation" claim with concrete, verifiable detail.

Task hints:
- Document exactly where the vector index and any OCR'd text (which can include receipts/invoices — sensitive by nature) are stored on disk (e.g. `~/.semanticfs/`), what format, and whether it's encrypted at rest. If it isn't encrypted, either add optional encryption or state plainly that it isn't and let the user decide — don't leave it unstated.
- Document the daemon's resource footprint (idle RAM/CPU, behavior on a laptop on battery) since it's an always-on background process scanning the full user directory tree.
- Add a `sfind purge` / uninstall path that fully removes the index and daemon registration — right now there's no documented way to undo the "full user space" indexing.
- One paragraph on what data ever leaves the machine (should be "none" given the offline claim — state it explicitly rather than implying it).

**Acceptance criteria:**
- Someone evaluating this for privacy-sensitive use has everything they need without reading source code.
- A clean uninstall/purge path exists and is documented.

---
