# TC-EDGE-001 — Empty FilterSearchRequest

| Field | Value |
|-------|--------|
| Identifier | TC-EDGE-001 |
| Title | Empty filter does not error |
| Objective | Invalid/empty partition of optional filters is still a valid RPC |
| Priority | Medium |
| Technique | Equivalence partitioning — no filters set |
| Scenario | TS-FUNC-002 |
| Test data | `{}` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-EDGE-001 -Language <lang>` |
| Log name | `TC-EDGE-001-<lang>` |

## Preconditions

API + DB + grpcurl.

## Steps

1. Call `SearchByFilter` with an empty object.
2. Observe status and payload.

## Expected results

- `OK`. A page of persons (default limit behaviour) or empty list.
- Not `INTERNAL`. `total_count` is the unconstrained match count (table size) if the implementation applies no extra default filter.

## Postconditions

Read-only.
