# Test scenarios (ISTQB test conditions)

**Purpose:** Answer CTFL’s test-analysis question: *what to test?*  
**Layout:** one folder per `TS-*`. Inside each folder, `00-scenario.md` is always first; realizing cases are sibling `TC-*.md` files.

**Catalog:** [../catalog.md](../catalog.md)

## Rules

1. One folder = one scenario (`TS-<TYPE>-NNN-<slug>/`), except Filter/Vector **boundary cases** that live inside the parent RPC folder (see below).
2. `00-scenario.md` states priority, technique, OWASP link (if any), and realizing cases.
3. Cases do not live in a separate flat tree — they stay with their scenario.
4. Six-language coverage is a condition on every Person RPC scenario.

## Index

| Folder | Title | Priority | Type | Cases |
|--------|-------|----------|------|-------|
| [TS-FUNC-001-readall](TS-FUNC-001-readall/) | Paginated ReadAllPersons | High | Functional + API4 | TC-FUNC-001, TC-SEC-API4-readall-resource |
| [TS-FUNC-002-filter](TS-FUNC-002-filter/) | SearchByFilter (+ empty / SQL-looking edges) | High | Functional + API3 | TC-FUNC-002, TC-EDGE-001, TC-EDGE-004, TC-SEC-API3-filter-injection |
| [TS-FUNC-003-vector](TS-FUNC-003-vector/) | SearchByVector (+ top_k=0 edge) | High | Functional + API4 | TC-FUNC-003, TC-EDGE-003, TC-SEC-API4-vector-topk |
| [TS-FUNC-004-create](TS-FUNC-004-create/) | CreatePerson | High | Functional + API1/3/6 | TC-FUNC-004, TC-SEC-API1/3/6-* |
| [TS-EDGE-002-huge-limit](TS-EDGE-002-huge-limit/) | Extreme ReadAll `limit` | High | BVA / API4 | TC-EDGE-002 |
| [TS-PERF-001-load](TS-PERF-001-load/) | Steady load | High | Performance | TC-PERF-001 |
| [TS-PERF-002-stress](TS-PERF-002-stress/) | Stress | High | Performance | TC-PERF-002 |
| [TS-PERF-003-spike](TS-PERF-003-spike/) | Spike | High | Performance | TC-PERF-003 |
| [TS-PERF-004-endurance](TS-PERF-004-endurance/) | Endurance / soak | Medium | Performance | TC-PERF-004 |
| [TS-PERF-005-scalability](TS-PERF-005-scalability/) | Scalability | High | Performance | TC-PERF-005 |
| [TS-PERF-006-concurrency](TS-PERF-006-concurrency/) | Concurrency | High | Performance | TC-PERF-006 |
| [TS-PERF-007-compare](TS-PERF-007-compare/) | Cross-language compare | High | Performance | TC-PERF-007 |
| [TS-SEC-001-k6-profile](TS-SEC-001-k6-profile/) | k6 security profile | High | Security | TC-SEC-001 |
| [TS-SEC-OWASP-PLATFORM](TS-SEC-OWASP-PLATFORM/) | Cross-cutting OWASP API2/5/7–10 | High | Security | TC-SEC-API2/5/7/8/9/10-* |
