# TC-SEC-API3-create-mass-assignment — Extra properties on Create

<!-- OWASP API3:2023 Broken Object Property Level Authorization / mass assignment. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API3-CREATE-MASS-ASSIGNMENT |
| Title | Unknown extra fields on CreatePerson are ignored or rejected |
| Objective | Ensure only proto-mapped properties persist (seed labels, no privilege flags) |
| Priority | High |
| Type / level | Security / System |
| Technique | OWASP API3:2023 mass assignment |
| Scenario | TS-FUNC-004 |
| Procedure | `Invoke-ManualTest.ps1 -TestId TC-SEC-API3-CREATE-MASS-ASSIGNMENT -Language <lang>` |
| Log name | `TC-SEC-API3-CREATE-MASS-ASSIGNMENT-<lang>` |
| Gherkin | `person-security.feature` `@owasp @api3` |

## Preconditions

API + DB + grpcurl.

## Test data

`create_extra_fields`: valid CreatePerson JSON plus unknown keys such as `"is_admin":true,"role":"root"` at the person object level (proto-loader / JSON may strip unknown fields — that is an acceptable pass).

## Steps

1. Call `CreatePerson` with extra fields.
2. If success, inspect stored row (filter by national_code): only schema columns exist; categoricals are seed labels.

## Expected results

- Success with extras ignored, **or** InvalidArgument.
- No elevation fields stored (schema has no `is_admin`).
- Fail: crash or unexpected column population.

## Postconditions

At most one extra bench row in the target table.
