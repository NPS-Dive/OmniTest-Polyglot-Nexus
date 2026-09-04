# TC-FUNC-004 — CreatePerson minimal bench row

<!-- ISTQB: EP valid create; checks inserted_id and seed-label persistence. -->

| Field | Value |
|-------|--------|
| Identifier | TC-FUNC-004 |
| Title | CreatePerson returns success and inserted_id |
| Objective | Verify write path, proto→SQL mapping, seed labels |
| Priority | High |
| Type / level | Functional / System |
| Technique | Equivalence partitioning — valid Person |
| Scenario | TS-FUNC-004 |
| Gherkin | `docs/gherkin/person-readall.feature` (create then list) |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-FUNC-004 -Language <lang>` |
| Log name | `TC-FUNC-004-<lang>` |

## Preconditions

API + DB up. Create is allowed on the language table.

## Test data

Generated UUID `id`, random 10-digit `national_code`, `first_name=Bench`, `last_name=Runner`, `age=30`, `gender=SEX_MALE`, `job_category=OCCUPATION_FULL_TIME` (see `Invoke-FunctionalRpc.ps1` `create_minimal`).

## Steps

1. Call `CreatePerson` with the generated payload.
2. Read `success`, `message`, `inserted_id`.
3. Optional: ReadAll or filter by national_code to confirm the row.

## Expected results

- Status `OK`, `success=true`, non-empty UUID `inserted_id`.
- Stored `sex` is seed label `male` (not `MALE` / `SEX_MALE`).
- Stored `occupation` is `full-time`.
- Row exists only in that language’s table.

## Postconditions

One extra row in `persons_<lang>`. Acceptable for demo; note it when comparing COUNT(*) across languages after many creates.
