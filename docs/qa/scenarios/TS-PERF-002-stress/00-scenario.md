# TS-PERF-002 — Stress past saturation

| Field | Value |
|-------|--------|
| Identifier | TS-PERF-002 |
| Title | Stress past saturation |
| Priority | High |
| Type | Performance (CTFL non-functional) |
| Script | `k6/stress.js` |
| Metrics | p50, p90, p95, p98, p99, avg, max, TTL |
| OWASP note | Sustained load also stresses API4 resource limits |
| Realizing cases | `TC-PERF-002.md` |
