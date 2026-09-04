# TC-SEC-API4-readall-resource — Unrestricted resource consumption (ReadAll)

<!-- OWASP API4:2023. Safe BVA above max limit. Folder: TS-FUNC-001-readall -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API4-READALL-RESOURCE |
| Title | Extreme ReadAllPersons limit does not exhaust the process |
| Objective | Verify clamp (max 500) or InvalidArgument under API4 resource-consumption pressure |
| Priority | High |
| Type / level | Security / System |
| Technique | Boundary value analysis; OWASP API4:2023 |
| Test basis | [OWASP API4:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) + `ReadAllPersonsRequest.limit` |
| Scenario | TS-FUNC-001 |
| Coverage item | `limit=999999` |
| Gherkin | `docs/gherkin/person-security.feature` `@owasp @api4` |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API4-READALL-RESOURCE -Language <lang>` |
| Log name | `TC-SEC-API4-READALL-RESOURCE-<lang>` |
| Related | TC-EDGE-002 (same payload; kept for BVA suite) |

## Preconditions

API + DB + grpcurl. Same as TC-FUNC-001.

## Test data

```json
{"limit": 999999, "offset": 0}
```

## Steps

1. Call `ReadAllPersons` with the payload.
2. If OK, count returned persons.
3. Confirm the process still accepts a follow-up `ReadAllPersons` limit=1.

## Expected results

- Process stays up (not `Unavailable`).
- If OK: `persons.length <= 500`.
- Or `InvalidArgument` / `OutOfRange`.
- Fail: crash, unbounded 1M-row response, or SQL/error dump in message.

## Postconditions

Read-only.
