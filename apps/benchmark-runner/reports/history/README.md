# reports/history

Append-only. Header-only CSVs are committed; JSONL files start empty.

| File | Writer |
|------|--------|
| `manual_results.csv` / `.jsonl` | `Invoke-ManualTest.ps1` |
| `automated_results.csv` / `.jsonl` | `Invoke-AutomatedTests.ps1` |
| `performance_results.csv` / `.jsonl` | k6 wrappers + `test_type` performance or security |

Never truncate these files to “clean” a demo. Use a new managerial `run_<timestamp>` folder instead.
