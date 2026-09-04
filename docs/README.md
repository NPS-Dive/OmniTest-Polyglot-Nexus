# docs

QA documentation for OmniTest-Polyglot-Nexus.

**ISTQB / ASTQB work products** live in **[qa/](qa/)** — one folder per scenario under [qa/scenarios/](qa/scenarios/), catalog at [qa/catalog.md](qa/catalog.md).  
Gherkin in `gherkin/` is the BDD view (`@owasp @apiN` on security cases). Runners: `apps/benchmark-runner/powershell/`.

## Feature → script map

| Feature | Tags | Catalog / script |
|---------|------|------------------|
| `gherkin/person-readall.feature` | `@functional` `@owasp` `@api4` `@performance` | `TC-FUNC-001`, `TC-FUNC-004`, `TC-SEC-API4-READALL-RESOURCE`, `k6/load.js` |
| `gherkin/person-filter.feature` | `@functional` `@security` `@owasp` `@api3` | `TC-FUNC-002`, `TC-EDGE-001/004`, `TC-SEC-API3-FILTER-INJECTION` |
| `gherkin/person-vector.feature` | `@functional` `@owasp` `@api4` `@performance` | `TC-FUNC-003`, `TC-EDGE-003`, `TC-SEC-API4-VECTOR-TOPK` |
| `gherkin/person-security.feature` | `@security` `@owasp` `@api1`…`@api10` | OWASP SEC IDs, `k6/security.js`, `Invoke-OwaspPlatformChecklist.ps1` |
| `gherkin/person-performance.feature` | `@performance` | `k6/*.js` via `Invoke-AllLanguagePerf.ps1` |

## How steps are executed (Windows)

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
.\Invoke-ManualTest.ps1 -TestId TC-SEC-API3-FILTER-INJECTION -Language csharp
```

`Invoke-AllManualTests.ps1` loops languages × TestIds (functional, edge, and executable OWASP SEC cases).

## History and bugs

- Results: `apps/benchmark-runner/reports/history/*.csv` + `*.jsonl`
- Defects: `apps/benchmark-runner/reports/bugs/TEMPLATE.md`
- Managerial snapshot: `.\New-ManagerialReport.ps1`
