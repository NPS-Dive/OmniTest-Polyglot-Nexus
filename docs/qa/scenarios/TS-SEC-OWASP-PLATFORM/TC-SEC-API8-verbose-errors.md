# TC-SEC-API8-verbose-errors — Information disclosure in errors

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API8-VERBOSE-ERRORS |
| Title | Invalid payloads do not leak stack traces or SQL |
| Objective | Misconfiguration / info disclosure under API8 |
| Priority | High |
| Type / level | Security / System |
| Technique | OWASP API8:2023 |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API8-VERBOSE-ERRORS -Language <lang>` |
| Log name | `TC-SEC-API8-VERBOSE-ERRORS-<lang>` |

## Test data

Invalid enum / bad vector length — payload kind `vector_bad_dims` (8 floats, `top_k=5`).

## Steps

1. Call `SearchByVector` with wrong dimension count.
2. Inspect error message text.

## Expected results

- `InvalidArgument` (or similar) without SQL text, file paths, or stack frames.
- Fail: message contains `SELECT`, stack traces, or connection strings.
