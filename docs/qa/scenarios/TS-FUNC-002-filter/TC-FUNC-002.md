# TC-FUNC-002 — SearchByFilter by first_name

<!-- ISTQB: decision table — first_name set, other optionals unset. -->

| Field | Value |
|-------|--------|
| Identifier | TC-FUNC-002 |
| Title | SearchByFilter with first_name only returns an AND-constrained page |
| Objective | Verify optional proto fields and gender/sex mapping are not required for a name filter |
| Priority | High |
| Type / level | Functional / System |
| Technique | Decision table (one optional field present) |
| Scenario | TS-FUNC-002 |
| Test data | `{"first_name":"A"}` |
| Gherkin | `docs/gherkin/person-filter.feature` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-FUNC-002 -Language <lang>` |
| Log name | `TC-FUNC-002-<lang>` |

## Preconditions

Same as TC-FUNC-001 (DB + API + grpcurl).

## Steps

1. Call `SearchByFilter` with `first_name=A` only.
2. Inspect `persons` and `total_count`.

## Expected results

- Status `OK`.
- Every returned `first_name` contains `A` (case-insensitive).
- `total_count` is the matching COUNT(*), not merely the page length.
- Unset filters (`gender`, ages, national_code) are ignored.

## Postconditions

Read-only.
