# TC-SEC-API10-outbound-na — Unsafe consumption of APIs (N/A)

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API10-OUTBOUND-NA |
| Title | Outbound API consumption not applicable |
| Objective | Document N/A for OWASP API10:2023 |
| Priority | Low |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Mode | Documentation only |

## Rationale

Person gRPC services talk only to Postgres. They do not call third-party HTTP/gRPC APIs. (ai-gateway / agents are separate processes.)

## Expected results

Checklist row: **N/A — no outbound API consumption in Person services**.
