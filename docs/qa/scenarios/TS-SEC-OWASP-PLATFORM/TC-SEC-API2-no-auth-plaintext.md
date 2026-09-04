# TC-SEC-API2-no-auth-plaintext — Broken authentication (residual)

<!-- OWASP API2:2023. Demo stack intentionally has no auth. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API2-NO-AUTH-PLAINTEXT |
| Title | Person RPCs succeed without credentials over plaintext |
| Objective | Document residual risk: no authentication, plaintext gRPC (h2c) |
| Priority | High (awareness) |
| Type / level | Security / System (checklist) |
| Technique | OWASP API2:2023 |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Procedure | `Invoke-OwaspPlatformChecklist.ps1` item API2 |
| Mode | Residual risk — **not a product fail** for v1 demo |

## Steps

1. Call `ReadAllPersons` limit=1 with **no** authorization metadata.
2. Confirm plaintext port from `services.json` (no TLS required).

## Expected results (v1)

- RPC succeeds without credentials → record **residual risk: Broken Authentication / plaintext**.
- Pass criteria for checklist: residual documented in history (`pass=true` means checklist completed, not “secure”).

## Production note

Require TLS and authentication before any public exposure.
