# Phase 5 — Testing & CI

**Objective:** Add automated tests and a CI pipeline so "it works" is something Antigravity (or anyone) can verify on every change, not just something the README asserts.

Task hints:
- `pytest` suite covering: the AST chunker (function/class boundary correctness on representative Python files), the search operator parser (`ext:`, `+term`, `-term`, `score:`), the recency decay scoring, and the daemon's IPC request/response contract.
- GitHub Actions workflow: run the test suite on push/PR, and ideally run the Phase 1 benchmark script on a fixed small fixture set so latency/accuracy regressions get caught automatically.
- A real CI badge in the README, linked to actual passing runs (replaces one of the fake-looking badges from Phase 0).

**Acceptance criteria:**
- `pytest` runs green locally and in CI.
- CI badge in README links to a real, passing workflow.

---
