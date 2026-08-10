# Phase 8 — Perception & positioning (portfolio polish)

**Objective:** Add the things that don't fix correctness but materially change how a reviewer perceives the project's quality and maturity.

Task hints:
- **Visual proof.** Record a short terminal session (asciinema, or a `.gif` via `vhs`/`terminalizer`) showing `sfind <query>` with the interactive arrow menu and live code preview actually working, and embed it near the top of the README. This is worth more than any paragraph of feature description — reviewers trust what they can see.
- **Positioning section.** Add a short "Why not just use Recoll / Everything / Spotlight / VS Code search?" section. State honestly what those tools do well and where SemanticFS's semantic/contextual approach adds something they don't (and where it doesn't — e.g. Everything is faster for exact filename lookup, SemanticFS is for "I don't remember the name" cases). Comparative honesty reads as domain expertise, not weakness.
- **Code quality tooling.** Add `ruff` (lint), `mypy` (type checking), and `black` or `ruff format` (formatting), wired into a pre-commit hook and into the Phase 5 CI workflow. Small effort, standard signal that the codebase is maintained to a bar, not just functional.
- **Versioning & release path.** Adopt semantic versioning, tag releases in git, and add a note on the eventual plan to publish to PyPI (even if not done yet — "installable via `pip install -e .` today; PyPI release planned" is an honest, forward-looking statement). Add a `CHANGELOG.md` entry per tagged version if not already covered in Phase 6.
- **IPC security note.** Document that the daemon listens on `127.0.0.1:9876` (localhost-only, not exposed to the network) and add one sentence on what that does and doesn't protect against (any other local process/user on the same machine could in principle connect — state this plainly rather than leaving it implicit). If there's no auth/token on the socket, either add a simple shared-secret handshake or explicitly note it's trusted-local-machine-only by design.

**Acceptance criteria:**
- README has an embedded demo GIF/recording above the fold.
- A "vs. alternatives" section exists and doesn't overstate SemanticFS's advantages.
- `ruff`/`mypy` run clean in CI.
- IPC trust model is stated explicitly, not left implicit.
