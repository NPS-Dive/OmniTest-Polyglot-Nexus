# TC-SEC-API1-create-id-tamper — Object id / UUID tamper (Create)

<!-- OWASP API1:2023 Broken Object Level Authorization — adapted to demo (no multi-tenant auth). -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API1-CREATE-ID-TAMPER |
| Title | Client-supplied invalid or colliding id does not corrupt other tables |
| Objective | Verify create handles bad/client UUID without cross-language writes |
| Priority | High |
| Type / level | Security / System |
| Technique | OWASP API1:2023 (object id control); EP invalid id |
| Scenario | TS-FUNC-004 |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API1-CREATE-ID-TAMPER -Language <lang>` |
| Log name | `TC-SEC-API1-CREATE-ID-TAMPER-<lang>` |
| Gherkin | `person-security.feature` `@owasp @api1` |

## Preconditions

API + DB. Note: this stack has **no auth** — API1 is tested as *object-id integrity*, not BOLA across users (see TS-SEC-OWASP-PLATFORM residual).

## Test data

`create_bad_uuid`: person with `"id":"not-a-uuid"` and otherwise valid fields.

## Steps

1. Call `CreatePerson` with invalid id.
2. Confirm response is InvalidArgument **or** server ignores id and generates a new UUID with `success=true`.
3. Confirm no write occurred to another language’s `persons_*` table.

## Expected results

- InvalidArgument, **or** success with a generated valid UUID (id ignored).
- Fail: crash, insert into wrong table, or success with invalid id stored as PK.

## Postconditions

At most one row in the target language table if the server accepts generated ids.
