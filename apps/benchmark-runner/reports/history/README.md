# reports/history

Append-only. Header-only CSVs are committed; JSONL files start empty.

Result CSVs include **p99_ms** immediately after **p98_ms**.

| File | Writer |
|------|--------|
| `manual_results.csv` / `.jsonl` | `Invoke-ManualTest.ps1` |
| `automated_results.csv` / `.jsonl` | `Invoke-AutomatedTests.ps1` |
| `performance_results.csv` / `.jsonl` | k6 wrappers (`Invoke-AllLanguagePerf.ps1`) + `test_type` performance or security |
| `service_runs.csv` / `.jsonl` | `Write-OpnServiceRun` (liveness / port probe) |

Never truncate these files to “clean” a demo. Use a new managerial `run_<timestamp>` folder instead.
