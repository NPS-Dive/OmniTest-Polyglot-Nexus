# TS-SEC-001 — k6 safe security profile

| Field | Value |
|-------|--------|
| Identifier | TS-SEC-001 |
| Title | Abusive but non-weaponized payloads are handled without process death |
| Priority | High |
| Payloads | 20k-char strings; SQL-looking names; extreme limit/top_k |
| Expected class | OK, InvalidArgument, OutOfRange, FailedPrecondition |
| Fail class | Unavailable / crash / SQL execution |
| OWASP | API3, API4 |
| Realizing cases | `TC-SEC-001.md` |
| BDD | `docs/gherkin/person-security.feature` |
