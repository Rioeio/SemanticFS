# Phase 0 — Credibility fixes (do this first, ~1 session)

**Objective:** Fix all factual contradictions and unsupported claims in the README so every number and claim in the document is either accurate, sourced, or removed.

Task hints for the agent:
- Reconcile the "Sub-5ms Query Latency" claim against the benchmark section's 18.97ms/query figure. Either (a) clarify these measure different things (e.g. warm-cache single-file lookup vs. cold large-scale stress test) and label each number with what it actually measures, or (b) pick one honest number and use it everywhere.
- Remove or soften "#1 MTEB Benchmark embedding model" for bge-small-en-v1.5 — it's a small/fast-tier model, not the top of the leaderboard. Replace with an accurate, dated description (e.g. "a compact, high-throughput embedding model suited to local/offline use") or link the actual MTEB leaderboard entry with a retrieval date.
- Find or remove the "+35% higher semantic retrieval accuracy for code and technical terms" claim. If there's no benchmark backing it, delete it. If you want to keep a number like this, it must point to a script in `/benchmarks` (see Phase 1).
- Replace the hardcoded `C:\Users\Manoj` path with `%USERPROFILE%` (Windows) or a generic placeholder.
- **Fix the Native Rust Core claim.** `native_core/` currently returns placeholder zero-vectors and is never called from Python. Pick one: (a) actually wire it in via PyO3 bindings and have it do real work, or (b) move the "Native Rust Core Crate" section out of the main feature list into a clearly labeled "Experimental / Not Yet Integrated" note, drop or annotate the Rust badge, and remove it from the architecture diagram until it's real. Do not leave it presented as a working component — this is the top-priority item in this phase.
- **Fill in the GitHub repo's About metadata** (description + topics) — currently empty. Takes a minute, shows up everywhere the repo link is shared.
- Add a one-line "Project status" indicator near the top of the README (alpha / beta / actively developed) — this alone materially improves how technical readers trust the rest of the document.
- Consider scrubbing or generalizing the personal name/coursework references committed in `tests/test_suite_100.py` (e.g. full name + course codes) before the repo gets wider visibility — your call, but worth a conscious decision rather than an oversight.

**Acceptance criteria:**
- No two numbers in the README contradict each other.
- Every performance or ranking claim either links to a script/source in the repo or is removed.
- No personal file paths appear anywhere in tracked files.
- The Native Rust Core is either functionally real or clearly labeled as not-yet-integrated — never presented as working when it isn't.
- GitHub repo About panel has a real description and at least a few topics set.

---
