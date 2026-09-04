# TS-FUNC-002 — SearchByFilter

| Field | Value |
|-------|--------|
| Identifier | TS-FUNC-002 |
| Title | SearchByFilter AND-combines optional proto fields |
| Test basis | `FilterSearchRequest` |
| Priority | High |
| Technique hint | Decision table: field set vs unset; empty filter (EP); SQL-looking (API3) |
| OWASP links | API3 (injection / property abuse) via `TC-SEC-API3-filter-injection` + `TC-EDGE-004` |
| Realizing cases | `TC-FUNC-002.md`, `TC-EDGE-001.md`, `TC-EDGE-004.md`, `TC-SEC-API3-filter-injection.md` |
| BDD | `docs/gherkin/person-filter.feature`, `person-security.feature` |

**Condition:** Optional filter fields AND-combine. Empty body is a valid read. SQL-looking text is data, not SQL.
