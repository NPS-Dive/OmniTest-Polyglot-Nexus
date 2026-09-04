# TC-PERF-001 — Steady load ReadAll

<!-- ISTQB non-functional case. Folder: TS-PERF-001-load -->

| Field | Value |
|-------|--------|
| Identifier | TC-PERF-001 |
| Title | Steady load ReadAll |
| Objective | Same ReadAllPersons under 10 VUs / 30s; record p90/p95/p98/p99 |
| Priority | High |
| Type / level | Performance / System |
| Scenario | TS-PERF-001 |
| Script | `apps/benchmark-runner/k6/load.js` |
| Procedure | `k6 run -e LANG=<lang> .\load.js` or `Invoke-AllLanguagePerf.ps1` |

## Preconditions

k6 installed; target API up; proto via `k6/lib/endpoints.js`.

## Expected results

Process up; `performance_results` row with p50/p90/p95/p98/p99/avg/max/ttl; gRPC check rate documented. Compare languages only for the same TC-PERF id.

## Phase 0 note

Go / TC-PERF-001: 138/138 OK; p90=3660 ms; p95=4010 ms; p98=4410 ms; p99=4580 ms.
