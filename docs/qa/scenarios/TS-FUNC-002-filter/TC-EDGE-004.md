# TC-EDGE-004 — SQL-looking first_name (safe security)

| Field | Value |
|-------|--------|
| Identifier | TC-EDGE-004 |
| Title | SQL-looking filter text is not executed |
| Objective | Confirm parameterized SQL / no string concat of user text |
| Priority | High |
| Technique | Error guessing (experience-based); safe payload only |
| Scenario | TS-FUNC-002 |
| Test data | `{"first_name":"Robert'); DROP TABLE persons_python;--"}` |
| Gherkin | `docs/gherkin/person-security.feature` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-EDGE-004 -Language <lang>` |
| Log name | `TC-EDGE-004-<lang>` |

## Preconditions

API + DB. Note the table name in the payload is **python** even when testing other languages — the point is the string must not run as SQL anywhere.

## Steps

1. Call `SearchByFilter` with the payload.
2. After the call, confirm `persons_python` (and the target table) still exist (`\dt` or `SELECT 1`).

## Expected results

- `OK` (typically 0 matches) or `InvalidArgument`.
- All six `persons_*` tables still present.
- Fail: table missing, syntax error leaking SQL, or crash.

## Postconditions

No schema change. Included in `Invoke-AllManualTests.ps1`.
