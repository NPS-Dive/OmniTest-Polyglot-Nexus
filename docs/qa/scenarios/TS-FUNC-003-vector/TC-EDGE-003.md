# TC-EDGE-003 — SearchByVector top_k=0 (BVA below min)

| Field | Value |
|-------|--------|
| Identifier | TC-EDGE-003 |
| Title | top_k=0 uses default 10 and does not crash |
| Objective | Clamp contract: default 10, max 100 |
| Priority | Medium |
| Technique | Boundary value analysis — below minimum |
| Scenario | TS-FUNC-003 |
| Test data | 384 × `0.0`, `top_k=0` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-EDGE-003 -Language <lang>` |
| Log name | `TC-EDGE-003-<lang>` |

## Expected results

- `OK` with at most 10 neighbours, **or** `InvalidArgument` if the service treats 0 as illegal.
- Not `INTERNAL` / crash.

## Postconditions

Read-only.
