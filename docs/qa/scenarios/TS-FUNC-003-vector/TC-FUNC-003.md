# TC-FUNC-003 — SearchByVector dummy embedding

<!-- ISTQB: EP valid 384-dim input; environment risk if embeddings are NULL. -->

| Field | Value |
|-------|--------|
| Identifier | TC-FUNC-003 |
| Title | SearchByVector accepts a 384-float query and returns at most top_k rows |
| Objective | Verify L2 path, `top_k` clamp, and proto `embedding_vector` mapping |
| Priority | High |
| Type / level | Functional / System |
| Technique | Equivalence partitioning — valid vector length |
| Scenario | TS-FUNC-003 |
| Test data | 384 × `0.01`, `top_k=5` |
| Gherkin | `docs/gherkin/person-vector.feature` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-FUNC-003 -Language <lang>` |
| Log name | `TC-FUNC-003-<lang>` |

## Preconditions

TC-FUNC-001 preconditions. Prefer non-null `embedding` on the language table. If all embeddings are NULL, **expected** is OK + empty list (environment), not INTERNAL.

## Steps

1. Invoke `SearchByVector` with 384 floats and `top_k=5`.
2. Confirm status and `persons.length <= 5`.
3. `total_count` equals returned neighbour count (documented kNN contract).

## Expected results

- Status `OK` or documented empty page.
- No crash. Dimension mismatch (if tester alters length) → `InvalidArgument`.

## Postconditions

Read-only.
