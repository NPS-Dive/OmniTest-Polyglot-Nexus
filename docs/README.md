# docs

QA documentation for OmniTest-Polyglot-Nexus. Features live in `gherkin/`. Runners live in `apps/benchmark-runner/powershell/`.

## Feature → script map

| Feature | Tags | Catalog / script |
|---------|------|------------------|
| `gherkin/person-readall.feature` | `@functional` `@performance` | `TC-FUNC-001` (all langs via `-Language`), `TC-FUNC-004` Create, thin `manual/TC-FUNC-001`…`006`, `k6/load.js` |
| `gherkin/person-filter.feature` | `@functional` `@security` | `TC-FUNC-002`, `TC-EDGE-001`, `TC-EDGE-004`, `manual/TC-FUNC-007`, `TC-FUNC-010`, `TC-EDGE-001` |
| `gherkin/person-vector.feature` | `@functional` `@performance` | `TC-FUNC-003`, `TC-EDGE-003`, `manual/TC-FUNC-008`, `TC-EDGE-003` |
| `gherkin/person-security.feature` | `@security` | `TC-EDGE-002`, `k6/security.js` |

## How steps are executed (Windows)

There is no Cucumber runtime in-repo. Treat each Scenario Outline example as:

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
```

`Invoke-AllManualTests.ps1` loops languages × TestIds (4 RPCs × 6 langs + edges). Pester can wrap the same scripts later; do not duplicate the payload builders.

## History and bugs

- Results: `apps/benchmark-runner/reports/history/*.csv` + `*.jsonl`
- Defects: `apps/benchmark-runner/reports/bugs/TEMPLATE.md`
- Managerial snapshot: `.\New-ManagerialReport.ps1`
