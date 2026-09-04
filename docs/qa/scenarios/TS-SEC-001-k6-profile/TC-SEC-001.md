# TC-SEC-001 — k6 safe security profile

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-001 |
| Title | Oversized, SQL-looking, and extreme pagination payloads are handled safely |
| Objective | No crash and no SQL execution; expected rejection or clamp |
| Priority | High |
| Type / level | Security (negative) / System |
| Technique | Error guessing; checklist of safe payloads |
| Scenario | TS-SEC-001 |
| Script | `apps/benchmark-runner/k6/security.js` |
| Gherkin | `docs/gherkin/person-security.feature` |
| Log type | `security` (stored with performance history files) |

## Preconditions

API up; k6 installed. **Do not** add real exploit payloads.

## Steps

```powershell
cd apps\benchmark-runner\k6
k6 run -e LANG=csharp .\security.js
```

The script sends: `limit=999999`; SQL-looking name/national_code; 20k-char names.

## Expected results

- Safe gRPC codes: OK, InvalidArgument, OutOfRange, FailedPrecondition.
- Fail: Unavailable after panic, or dropped tables.
- Checks rate threshold in the script (`rate>0.70`).

## Postconditions

Schema unchanged. History row `test_type=security`.
