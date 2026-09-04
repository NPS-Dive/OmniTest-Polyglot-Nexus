# TC-FUNC-001 — ReadAllPersons default page

<!-- ISTQB CTFL 4.0.1 test-design work product. Technique: equivalence partitioning (valid pagination). -->

| Field | Value |
|-------|--------|
| Identifier | TC-FUNC-001 |
| Title | ReadAllPersons returns at most the requested page and a full-table total_count |
| Objective | Verify pagination and fair `COUNT(*)` on the language-owned table |
| Priority | High |
| Type / level | Functional / System (gRPC) |
| Technique | Equivalence partitioning — valid `limit` in (1..500) |
| Test basis | `ReadAllPersonsRequest.limit/offset`; `PersonListResponse` |
| Scenario | TS-FUNC-001 |
| Coverage item | `limit=5`, `offset=0` |
| Test object | `omnitest.polyglot.nexus.PersonService` on the selected language port |
| Gherkin | `docs/gherkin/person-readall.feature` — Default page |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language <lang>` |
| Log name | `TC-FUNC-001-<lang>` |

## Preconditions

1. Postgres `opn_db` reachable; target `persons_*` table exists.
2. Target language gRPC process listening (`docs/qa` port table in root README).
3. `grpcurl` on PATH (else result = blocked, not fail).

## Test data

```json
{"limit": 5, "offset": 0}
```

## Steps

1. Select language L and confirm TCP on its port.
2. Invoke `ReadAllPersons` with the JSON above (plaintext).
3. Record TTL and gRPC status in history.

## Expected results

- Status `OK`.
- `persons` length ≤ 5.
- `total_count` ≥ page size and equals table `COUNT(*)` (not `len(page)`).
- No rows from another language’s table.

## Postconditions

Read-only. No new rows.

## Actual / evidence

Fill after a run: status, `total_count`, history `timestamp_utc`. On contract fail → `BUG-NNN`.
