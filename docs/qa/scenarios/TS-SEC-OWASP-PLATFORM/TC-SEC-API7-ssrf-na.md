# TC-SEC-API7-ssrf-na — Server-side request forgery (N/A)

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API7-SSRF-NA |
| Title | SSRF not applicable — no user-supplied URI fetch |
| Objective | Document N/A for OWASP API7:2023 |
| Priority | Low |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Mode | Documentation only |

## Rationale

Proto fields are scalars/enums/embeddings only. No URL, webhook, or callback field. Person APIs do not fetch remote resources based on client input.

## Expected results

Checklist row: **N/A — no SSRF surface**.
