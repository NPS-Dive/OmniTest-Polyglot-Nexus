# powershell

Test procedures for cases under `docs/qa/scenarios/TS-*/`. Catalog IDs must stay aligned with [docs/qa/catalog.md](../../../docs/qa/catalog.md).

Windows-first runners. Functional and executable OWASP coverage is **parameterized**: `Invoke-FunctionalRpc.ps1` plus loops in `Invoke-All*.ps1`.

| Script | Role |
|--------|------|
| `Common.ps1` | Repo paths + `services.json` |
| `ReportWriter.ps1` | Append-only CSV + JSONL |
| `Invoke-FunctionalRpc.ps1` | One RPC / one language via grpcurl |
| `Invoke-ManualTest.ps1` | `-TestId` `-Language` (FUNC/EDGE/SEC) |
| `Invoke-AllManualTests.ps1` | Catalog × 6 langs (incl. executable OWASP) |
| `Invoke-OwaspPlatformChecklist.ps1` | API2/5/7/8/9/10 residual checklist → history |
| `Invoke-AutomatedTests.ps1` | Same catalog → automated history (+ optional k6 smoke) |
| `Invoke-AllAutomatedTests.ps1` | Loop all langs |
| `New-ManagerialReport.ps1` | `reports/managerial/run_<ts>/` |

If `grpcurl` is missing, the runner **does not** invent a pass. It appends `pass=false` and the install hint. Platform N/A cases use the checklist runner (`pass` = residual risk logged), not fake exploit automation.
