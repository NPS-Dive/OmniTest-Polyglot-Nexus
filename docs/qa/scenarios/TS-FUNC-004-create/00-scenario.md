# TS-FUNC-004 — CreatePerson

| Field | Value |
|-------|--------|
| Identifier | TS-FUNC-004 |
| Title | CreatePerson inserts one row and returns inserted_id |
| Test basis | `CreatePersonRequest` / `CreatePersonResponse` |
| Priority | High |
| OWASP links | API1 (id tamper), API3 (mass assignment), API6 (flow abuse) |
| Realizing cases | `TC-FUNC-004.md`, `TC-SEC-API1-create-id-tamper.md`, `TC-SEC-API3-create-mass-assignment.md`, `TC-SEC-API6-create-burst.md` |
| BDD | `docs/gherkin/person-readall.feature` (create) |
