# TC-SEC-API4-vector-topk — Resource consumption (Vector top_k)

<!-- OWASP API4:2023 for SearchByVector. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API4-VECTOR-TOPK |
| Title | Extreme or invalid top_k / vector length is clamped or rejected |
| Objective | Prevent unbounded kNN work; validate dimension contract |
| Priority | High |
| Type / level | Security / System |
| Technique | BVA; OWASP API4:2023 |
| Scenario | TS-FUNC-003 |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API4-VECTOR-TOPK -Language <lang>` |
| Log name | `TC-SEC-API4-VECTOR-TOPK-<lang>` |
| Gherkin | `person-security.feature` `@owasp @api4` |

## Preconditions

API + DB + grpcurl. Empty embeddings → OK empty page is environment, not fail.

## Test data

```json
{"vector": [<384 floats 0.0>], "top_k": 999999}
```

(Catalog payload kind `vector_topk_huge`.)

## Steps

1. Call `SearchByVector` with `top_k=999999` and 384-dim zeros.
2. Optionally retry with wrong dimension (e.g. 8 floats) — expect InvalidArgument.

## Expected results

- Process up.
- If OK: at most 100 neighbours (`top_k` max).
- Or `InvalidArgument` / `OutOfRange`.
- Fail: crash or unbounded huge result set.

## Postconditions

Read-only.
