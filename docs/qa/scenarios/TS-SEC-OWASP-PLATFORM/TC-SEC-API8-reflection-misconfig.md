# TC-SEC-API8-reflection-misconfig — gRPC reflection exposure

<!-- OWASP API8:2023 + OWASP gRPC Security Cheat Sheet. -->

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API8-REFLECTION-MISCONFIG |
| Title | Server reflection availability is inventoried per language |
| Objective | Record which APIs expose `grpc.reflection` (misconfig risk in production) |
| Priority | Medium |
| Type / level | Security / System (checklist) |
| Technique | OWASP API8:2023; gRPC cheat sheet |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Procedure | `Invoke-OwaspPlatformChecklist.ps1` item API8-reflection |

## Steps

1. For each language port in `services.json`, run `grpcurl -plaintext <host:port> list` (or document grpcurl missing).
2. Note whether `grpc.reflection.v1alpha.ServerReflection` / service list appears.
3. Record residual: reflection OK for **local demo**; disable in production.

## Expected results

- Checklist completed with a per-language yes/no table.
- Not a v1 product fail if reflection is on (dev convenience).
