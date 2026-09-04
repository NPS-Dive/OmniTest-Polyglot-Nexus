# QA work products (ISTQB CTFL 4.0.1 / ASTQB)

This folder is the **test analysis and test design** documentation for OmniTest-Polyglot-Nexus.

**Syllabus:** [ISTQB Certified Tester Foundation Level v4.0.1](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/) (errata 15 Sep 2024).  
**ASTQB** is the US ISTQB member board. It examines the same CTFL 4.0.1 syllabus; there is no separate ASTQB defect form.

**Security basis:** [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) mapped to this gRPC Person surface (safe payloads only).

## Vocabulary used in this repo

| ISTQB term (CTFL 4.0) | What we write | Location |
|-----------------------|---------------|----------|
| Test basis | Proto, SQL schema, language READMEs, OWASP API Top 10 | `shared/proto/`, `data/vector-store/` |
| Test condition (“what to test?”) | **Test scenario** `TS-*` → `00-scenario.md` | [scenarios/TS-*/](scenarios/) |
| Test case (“how to test?”) | **Test case** `TC-*.md` in the same folder | [scenarios/TS-*/](scenarios/) |
| Test procedure / script | PowerShell + k6 | `apps/benchmark-runner/` |
| Test log | History CSV/JSONL | `apps/benchmark-runner/reports/history/` |
| Defect report | `BUG-NNN.md` | [bugs](../../apps/benchmark-runner/reports/bugs/) |

A **scenario folder** holds `00-scenario.md` first (sortable), then related `TC-*.md` files. Gherkin in `docs/gherkin/` is the BDD view (`@owasp @apiN` tags for security).

## Layout

```text
docs/qa/
  README.md
  catalog.md
  scenarios/
    README.md
    TS-FUNC-001-readall/     # TC-FUNC-001 + TC-SEC-API4-…
    TS-FUNC-002-filter/      # TC-FUNC-002 + TC-EDGE-001/004 + TC-SEC-API3-…
    TS-FUNC-003-vector/      # TC-FUNC-003 + TC-EDGE-003 + TC-SEC-API4-…
    TS-FUNC-004-create/      # TC-FUNC-004 + TC-SEC-API1/3/6-…
    TS-EDGE-002-huge-limit/  # dedicated BVA/API4 only
    TS-PERF-001-load/ … TS-PERF-007-compare/
    TS-SEC-001-k6-profile/
    TS-SEC-OWASP-PLATFORM/   # API2/5/7/8/9/10 checklist + N/A
```

Filter/Vector boundary cases live **inside** those RPC folders. Only extreme ReadAll `limit` keeps a dedicated `TS-EDGE-002` folder.
## Traceability

```
Requirement / proto RPC / OWASP API:2023
    → TS folder (00-scenario.md)
        → TC-*.md
            → Gherkin (@owasp @apiN)
                → Invoke-ManualTest.ps1 / k6 / Invoke-OwaspPlatformChecklist.ps1
                    → history row
                        → BUG-NNN if product failure
```

Master matrix: [catalog.md](catalog.md).

## OWASP mapping (summary)

| OWASP API:2023 | Where |
|----------------|--------|
| API1–4, API6 | Endpoint TCs inside `TS-FUNC-*` / `TS-EDGE-*` |
| API2, API5, API7–10 | [TS-SEC-OWASP-PLATFORM](scenarios/TS-SEC-OWASP-PLATFORM/) (checklist / N/A residual) |

## How to run

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language go
.\Invoke-ManualTest.ps1 -TestId TC-SEC-API4-READALL-RESOURCE -Language csharp
.\Invoke-AllManualTests.ps1
.\Invoke-OwaspPlatformChecklist.ps1 -Language csharp -SkipInteractive
.\Invoke-AllLanguagePerf.ps1 -Smoke
```

Missing `grpcurl` is an **environment block**, not a product defect.

## Related

- Scenario index: [scenarios/README.md](scenarios/README.md)
- BDD map: [docs/README.md](../README.md)
- Defect process: [apps/benchmark-runner/reports/bugs/README.md](../../apps/benchmark-runner/reports/bugs/README.md)
- RAG copy: [data/knowledge-base/istqb-defect-process.md](../../data/knowledge-base/istqb-defect-process.md)
