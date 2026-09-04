# QA catalog — scenarios and test cases

Single traceability matrix. **Canonical location:** each case lives under `docs/qa/scenarios/TS-*/` (`00-scenario.md` first, then `TC-*.md`).

IDs are stable. Language instances append `-{lang}` in the test log (`TC-FUNC-001-go`).

Boundary cases for Filter/Vector live **inside** those RPC folders (`TC-EDGE-001/004` under filter; `TC-EDGE-003` under vector). Dedicated BVA folder kept only for huge ReadAll limit: [TS-EDGE-002-huge-limit](scenarios/TS-EDGE-002-huge-limit/).

## Functional / edge / executable security (PowerShell)

| Case | Scenario folder | Type | OWASP | PayloadKind | Procedure |
|------|-----------------|------|-------|-------------|-----------|
| TC-FUNC-001 | [TS-FUNC-001-readall](scenarios/TS-FUNC-001-readall/) | Functional | — | `readall_default` | `Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language <lang>` |
| TC-SEC-API4-readall-resource | TS-FUNC-001-readall | Security | API4 | `readall_huge_limit` | `-TestId TC-SEC-API4-READALL-RESOURCE` |
| TC-FUNC-002 | [TS-FUNC-002-filter](scenarios/TS-FUNC-002-filter/) | Functional | — | `filter_name` | `-TestId TC-FUNC-002` |
| TC-EDGE-001 | TS-FUNC-002-filter | Boundary | — | `filter_empty` | `-TestId TC-EDGE-001` |
| TC-EDGE-004 | TS-FUNC-002-filter | Security | API3 | `filter_sql_name` | `-TestId TC-EDGE-004` |
| TC-SEC-API3-filter-injection | TS-FUNC-002-filter | Security | API3 | `filter_sql_name` / `filter_oversized` | `-TestId TC-SEC-API3-FILTER-INJECTION` |
| TC-FUNC-003 | [TS-FUNC-003-vector](scenarios/TS-FUNC-003-vector/) | Functional | — | `vector_dummy` | `-TestId TC-FUNC-003` |
| TC-EDGE-003 | TS-FUNC-003-vector | Boundary | API4 | `vector_topk_zero` | `-TestId TC-EDGE-003` |
| TC-SEC-API4-vector-topk | TS-FUNC-003-vector | Security | API4 | `vector_topk_huge` | `-TestId TC-SEC-API4-VECTOR-TOPK` |
| TC-FUNC-004 | [TS-FUNC-004-create](scenarios/TS-FUNC-004-create/) | Functional | — | `create_minimal` | `-TestId TC-FUNC-004` |
| TC-SEC-API1-create-id-tamper | TS-FUNC-004-create | Security | API1 | `create_bad_uuid` | `-TestId TC-SEC-API1-CREATE-ID-TAMPER` |
| TC-SEC-API3-create-mass-assignment | TS-FUNC-004-create | Security | API3 | `create_extra_fields` | `-TestId TC-SEC-API3-CREATE-MASS-ASSIGNMENT` |
| TC-SEC-API6-create-burst | TS-FUNC-004-create | Security | API6 | `create_minimal` × N | Checklist / scripted burst |
| TC-EDGE-002 | [TS-EDGE-002-huge-limit](scenarios/TS-EDGE-002-huge-limit/) | BVA | API4 | `readall_huge_limit` | `-TestId TC-EDGE-002` |

Languages: `cpp` `python` `java` `go` `csharp` `node`. Suite: `Invoke-AllManualTests.ps1`.

## Performance (k6)

| Case | Scenario folder | Script |
|------|-----------------|--------|
| TC-PERF-001 … 007 | [TS-PERF-001-load](scenarios/TS-PERF-001-load/) … [TS-PERF-007-compare](scenarios/TS-PERF-007-compare/) | `k6/*.js` via `Invoke-AllLanguagePerf.ps1` |

## Platform OWASP (checklist / residual)

| Case | Scenario folder | OWASP | Mode |
|------|-----------------|-------|------|
| TC-SEC-001 | [TS-SEC-001-k6-profile](scenarios/TS-SEC-001-k6-profile/) | API3/API4 aggregate | `k6/security.js` |
| TC-SEC-API2-no-auth-plaintext | [TS-SEC-OWASP-PLATFORM](scenarios/TS-SEC-OWASP-PLATFORM/) | API2 | Checklist residual |
| TC-SEC-API5-bfla-na | TS-SEC-OWASP-PLATFORM | API5 | Doc N/A |
| TC-SEC-API7-ssrf-na | TS-SEC-OWASP-PLATFORM | API7 | Doc N/A |
| TC-SEC-API8-reflection-misconfig | TS-SEC-OWASP-PLATFORM | API8 | Checklist |
| TC-SEC-API8-verbose-errors | TS-SEC-OWASP-PLATFORM | API8 | Manual + `-TestId TC-SEC-API8-VERBOSE-ERRORS` |
| TC-SEC-API9-service-inventory | TS-SEC-OWASP-PLATFORM | API9 | Checklist |
| TC-SEC-API10-outbound-na | TS-SEC-OWASP-PLATFORM | API10 | Doc N/A |

Platform checklist: `Invoke-OwaspPlatformChecklist.ps1`.

## Coverage vs proto RPCs

| RPC | Happy path | Boundary | Security (OWASP) | Performance |
|-----|------------|----------|------------------|-------------|
| CreatePerson | TC-FUNC-004 | — | API1, API3, API6 | — |
| ReadAllPersons | TC-FUNC-001 | TC-EDGE-002 | API4 | TC-PERF-001…007 |
| SearchByFilter | TC-FUNC-002 | TC-EDGE-001 | API3 (EDGE-004 + SEC) | — |
| SearchByVector | TC-FUNC-003 | TC-EDGE-003 | API4 | — |
