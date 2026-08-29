# powershell

Windows-first runners. All functional coverage is **parameterized**: `Invoke-FunctionalRpc.ps1` plus loops in `Invoke-All*.ps1`. `manual/` holds thin TC-FUNC / TC-EDGE wrappers only.

| Script | Role |
|--------|------|
| `Common.ps1` | Repo paths + `services.json` |
| `ReportWriter.ps1` | Append-only CSV + JSONL |
| `Invoke-FunctionalRpc.ps1` | One RPC / one language via grpcurl |
| `Invoke-ManualTest.ps1` | `-TestId` `-Language` |
| `Invoke-AllManualTests.ps1` | 4 RPCs × 6 langs + edges |
| `Invoke-AutomatedTests.ps1` | Same catalog → automated history (+ optional k6 smoke) |
| `Invoke-AllAutomatedTests.ps1` | Loop all langs |
| `New-ManagerialReport.ps1` | `reports/managerial/run_<ts>/` |

If `grpcurl` is missing, the runner **does not** invent a pass. It appends `pass=false` and the install hint. That is the mock-safe skip.
