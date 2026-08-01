# Version Evolution & Release History

SemanticFS has evolved across 5 major development milestones. Each phase is preserved in a dedicated git branch for auditing and testing:

| Milestone Branch | Major Features Introduced | Test Suite | Benchmark Top-1 Acc. | Code Quality | Status |
|---|---|---|---|---|---|
| [`v1.0-core-retrieval`](https://github.com/Rioeio/SemanticFS/tree/v1.0-core-retrieval) | BAAI/bge-small-en-v1.5 embeddings, AST code chunker | Manual CLI | 60.00% (10 queries) | Baseline | Initial Milestone |
| [`v2.0-virtual-collections-visualizer`](https://github.com/Rioeio/SemanticFS/tree/v2.0-virtual-collections-visualizer) | Virtual Smart Collections (`sfind collection`), 3D ASCII visualizer | Manual CLI | 70.00% (10 queries) | Feature additions | Visual Milestone |
| [`v3.0-benchmarks-storage-security`](https://github.com/Rioeio/SemanticFS/tree/v3.0-benchmarks-storage-security) | Portable eval suite (`run_benchmarks.py`), `sfind purge`, 0% network egress | Manual CLI | 80.00% (10 queries) | Security hardening | Security Milestone |
| [`v4.0-testing-ci-docs`](https://github.com/Rioeio/SemanticFS/tree/v4.0-testing-ci-docs) | PyTest unit test suite (`tests/`), GitHub Actions CI, architecture docs | 7/7 PyTest | 100.00% (10 queries) | `--exit-zero` CI | Testing Milestone |
| [`v5.0-production-release`](https://github.com/Rioeio/SemanticFS/tree/v5.0-production-release) (`main`) | Phase 9 audit fixes, 40-query eval set, terminal `demo.svg`, zero SQLite file leaks, cross-platform CI | 9/9 Passed (100%) | 95.00% (38/40 queries) | Clean (0 errors) | Current Release |

> [!NOTE]
> **Current Release**: `main` (`v5.0-production-release`) is the active release of SemanticFS. It includes 100% clean type safety, zero Windows file-handle leaks, 40-query benchmark evaluation, and GitHub Actions CI integration.
