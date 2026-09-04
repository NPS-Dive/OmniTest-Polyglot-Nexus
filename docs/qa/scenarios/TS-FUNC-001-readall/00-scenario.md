# TS-FUNC-001 — Paginated ReadAllPersons

| Field | Value |
|-------|--------|
| Identifier | TS-FUNC-001 |
| Title | Paginated ReadAllPersons returns a page plus full-table count |
| Test basis | RPC `ReadAllPersons`; SQL `LIMIT/OFFSET` + `COUNT(*)` |
| Priority | High |
| Test level | System (gRPC API) |
| Coverage items | Default/clamped `limit`, `offset >= 0`, `total_count` is not page length |
| OWASP links | API4 (resource consumption) via related `TC-SEC-API4-readall-resource` |
| Realizing cases | `TC-FUNC-001.md`, `TC-SEC-API4-readall-resource.md` |
| BDD | `docs/gherkin/person-readall.feature` |

**Condition:** A client can page the language-owned table. `total_count` equals matching rows in **that** table only.
