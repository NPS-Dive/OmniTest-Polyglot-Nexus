# TC-SEC-API3-filter-injection — Property / injection abuse (Filter)

<!-- OWASP API3:2023 + injection as data. Safe payloads only. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API3-FILTER-INJECTION |
| Title | SQL-looking and oversized filter fields are not executed |
| Objective | Confirm user strings are bound as data (API3 property abuse / injection surface) |
| Priority | High |
| Type / level | Security / System |
| Technique | Error guessing; OWASP API3:2023 |
| Test basis | [OWASP API3:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) + `FilterSearchRequest` |
| Scenario | TS-FUNC-002 |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API3-FILTER-INJECTION -Language <lang>` |
| Log name | `TC-SEC-API3-FILTER-INJECTION-<lang>` |
| Related | TC-EDGE-004 |
| Gherkin | `person-security.feature` `@owasp @api3` |

## Preconditions

API + DB. After the call, tables must still exist.

## Test data

Primary (catalog): SQL-looking `first_name` (same as `filter_sql_name`).  
Also acceptable: 20k-char `first_name` via `filter_oversized` if running the extended payload.

## Steps

1. Call `SearchByFilter` with SQL-looking `first_name`.
2. Optionally call with oversized `first_name`.
3. `SELECT 1 FROM persons_python LIMIT 1` (or `\dt`) to confirm schema intact.

## Expected results

- `OK` (often 0 matches) or `InvalidArgument`.
- All `persons_*` tables still present.
- Fail: table drop, SQL syntax leak, crash.

## Postconditions

No schema change.
