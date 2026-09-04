# TC-SEC-API9-service-inventory — Improper inventory management

| Field | Value |
|-------|--------|
| Identifier | TC-SEC-API9-SERVICE-INVENTORY |
| Title | Documented ports and RPCs match the running inventory |
| Objective | OWASP API9:2023 — no shadow endpoints vs `services.json` / proto |
| Priority | Medium |
| Type / level | Security / System (checklist) |
| Scenario | TS-SEC-OWASP-PLATFORM |
| Procedure | `Invoke-OwaspPlatformChecklist.ps1` item API9 |

## Steps

1. Read `apps/benchmark-runner/config/services.json` (six languages, ports, tables).
2. Confirm root README ports match.
3. Confirm `person_service.proto` lists exactly: CreatePerson, ReadAllPersons, SearchByFilter, SearchByVector.
4. TCP-probe each port (`Probe-Services.ps1`); note up/down without inventing services.

## Expected results

- Inventory table written to checklist history.
- Fail only if README/services.json/proto disagree on ports or RPC names.
