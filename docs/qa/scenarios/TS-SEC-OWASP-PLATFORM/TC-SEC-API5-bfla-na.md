# TC-SEC-API5-bfla-na — Broken function level authorization (N/A)

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API5-BFLA-NA |
| Title | BFLA not applicable — no roles or admin RPCs in v1 |
| Objective | Document N/A for OWASP API5:2023 |
| Priority | Low |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Mode | Documentation only |

## Rationale

PersonService exposes the same four RPCs to all clients. There is no admin/user role split, no privileged method, and no function-level ACL. API5 cannot be exercised until roles exist.

## Expected results

Checklist row: **N/A — no BFLA surface**. Residual: add authz before privileged operations.
