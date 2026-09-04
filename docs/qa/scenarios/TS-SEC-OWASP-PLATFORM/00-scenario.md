# TS-SEC-OWASP-PLATFORM — Cross-cutting OWASP API Security Top 10:2023

| Field | Value |
|-------|--------|
| Identifier | TS-SEC-OWASP-PLATFORM |
| Title | Stack-wide OWASP API:2023 controls for OmniTest gRPC Person APIs |
| Test basis | [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) + [gRPC Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/gRPC_Security_Cheat_Sheet.html) + `person_service.proto` |
| Priority | High |
| Scope | All six languages / ports; not tied to a single RPC happy-path |
| Safe only | No exploit kits; residual risks documented as N/A where product has no auth/roles/URL fetch |

## Related cases in this folder

| Case | OWASP | Executable? |
|------|-------|-------------|
| [TC-SEC-API2-no-auth-plaintext.md](TC-SEC-API2-no-auth-plaintext.md) | API2 | Checklist (residual risk) |
| [TC-SEC-API5-bfla-na.md](TC-SEC-API5-bfla-na.md) | API5 | Doc N/A |
| [TC-SEC-API7-ssrf-na.md](TC-SEC-API7-ssrf-na.md) | API7 | Doc N/A |
| [TC-SEC-API8-reflection-misconfig.md](TC-SEC-API8-reflection-misconfig.md) | API8 | Checklist / grpcurl list |
| [TC-SEC-API8-verbose-errors.md](TC-SEC-API8-verbose-errors.md) | API8 | Manual + history |
| [TC-SEC-API9-service-inventory.md](TC-SEC-API9-service-inventory.md) | API9 | Checklist vs services.json |
| [TC-SEC-API10-outbound-na.md](TC-SEC-API10-outbound-na.md) | API10 | Doc N/A |

Endpoint-specific OWASP cases live under `TS-FUNC-*` (and dedicated `TS-EDGE-002` for huge ReadAll limit).

## Runner

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-OwaspPlatformChecklist.ps1
```
