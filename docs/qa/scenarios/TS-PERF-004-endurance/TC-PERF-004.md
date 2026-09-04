# TC-PERF-004 — Endurance / soak

<!-- ISTQB non-functional case. Folder: TS-PERF-004-endurance -->

| Field | Value |
|-------|--------|
| Identifier | TC-PERF-004 |
| Title | Endurance / soak |
| Objective | Same ReadAllPersons under 5 VUs / 2m; record p90/p95/p98/p99 |
| Priority | Medium |
| Type / level | Performance / System |
| Scenario | TS-PERF-004 |
| Script | `apps/benchmark-runner/k6/endurance.js` |
| Procedure | `k6 run -e LANG=<lang> .\endurance.js` or `Invoke-AllLanguagePerf.ps1` |

## Preconditions

k6 installed; target API up; proto via `k6/lib/endpoints.js`.

## Expected results

Process up; `performance_results` row with p50/p90/p95/p98/p99/avg/max/ttl; gRPC check rate documented. Compare languages only for the same TC-PERF id.

## Phase 0 note

Go / TC-PERF-001: 138/138 OK; p90=3660 ms; p95=4010 ms; p98=4410 ms; p99=4580 ms.
