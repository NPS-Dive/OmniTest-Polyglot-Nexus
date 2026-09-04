# TC-EDGE-002 — ReadAllPersons huge limit (BVA above max)

| Field | Value |
|-------|--------|
| Identifier | TC-EDGE-002 |
| Title | limit=999999 is clamped to 500 or rejected |
| Objective | Protect process and fair paging; also a safe security probe |
| Priority | High |
| Technique | Boundary value analysis — above max 500 |
| Scenario | TS-EDGE-002 |
| Test data | `{"limit":999999,"offset":0}` |
| Gherkin | `docs/gherkin/person-security.feature` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-EDGE-002 -Language <lang>` |
| Log name | `TC-EDGE-002-<lang>` |

## Preconditions

API + DB + grpcurl.

## Steps

1. Call `ReadAllPersons` with limit 999999.
2. If OK, count returned persons.

## Expected results

- Process stays up.
- If OK: `persons.length <= 500`.
- Or `InvalidArgument` / `OutOfRange`.
- Fail: crash, `Unavailable`, or unbounded 1M-row payload.

## Postconditions

Read-only.
