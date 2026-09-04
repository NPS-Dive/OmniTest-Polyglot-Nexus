# TC-PERF-002 — Stress ramp

<!-- ISTQB non-functional case. Folder: TS-PERF-002-stress -->

| Field | Value |
|-------|--------|
| Identifier | TC-PERF-002 |
| Title | Stress ramp |
| Objective | Same ReadAllPersons under 0→25→50→0; record p90/p95/p98/p99 |
| Priority | High |
| Type / level | Performance / System |
| Scenario | TS-PERF-002 |
| Script | `apps/benchmark-runner/k6/stress.js` |
| Procedure | `k6 run -e LANG=<lang> .\stress.js` or `Invoke-AllLanguagePerf.ps1` |

## Preconditions

k6 installed; target API up; proto via `k6/lib/endpoints.js`.

## Expected results

Process up; `performance_results` row with p50/p90/p95/p98/p99/avg/max/ttl; gRPC check rate documented. Compare languages only for the same TC-PERF id.

## Phase 0 note

Go / TC-PERF-001: 138/138 OK; p90=3660 ms; p95=4010 ms; p98=4410 ms; p99=4580 ms.
