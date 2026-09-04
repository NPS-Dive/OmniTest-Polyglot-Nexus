# TC-SEC-API6-create-burst — Unrestricted access to create flow

<!-- OWASP API6:2023 Unrestricted Access to Sensitive Business Flows. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API6-CREATE-BURST |
| Title | Rapid repeated CreatePerson does not crash the service |
| Objective | Document lack of rate limiting as residual risk; verify no crash under small burst |
| Priority | Medium |
| Type / level | Security / System |
| Technique | OWASP API6:2023 |
| Scenario | TS-FUNC-004 |
| Procedure | Loop 20× `Invoke-ManualTest.ps1 -TestId TC-FUNC-004 -Language <lang>` or scripted burst |
| Log name | `TC-SEC-API6-CREATE-BURST-<lang>` |
| Gherkin | `person-security.feature` `@owasp @api6` |

## Preconditions

API + DB. Use a **dev** database only (inserts ~20 rows).

## Steps

1. Issue 20 consecutive `CreatePerson` calls with unique national codes.
2. Confirm the process still serves `ReadAllPersons` limit=1.
3. Record in history that rate limiting is **not** implemented (residual risk for production).

## Expected results

- No crash / `Unavailable`.
- Soft expect: most creates succeed; document residual: no throttling in v1.
- Fail: process death or DB connection exhaustion without recovery.

## Postconditions

~20 rows added to `persons_<lang>`. Note when comparing COUNT(*) fairness after many bursts.
