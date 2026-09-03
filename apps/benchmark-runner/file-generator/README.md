# file-generator

Append-only writer for `apps/benchmark-runner/reports/history`. Twin of `powershell/ReportWriter.ps1` for callers that prefer Python (orchestrator, CI, notebooks).

**SOLID:** `models.py` owns row shapes, `writers.py` owns append I/O (never overwrite), `main.py` is the CLI composition root.

No third-party packages — see `requirements.txt`.

## Files

| Path | Role |
|------|------|
| `models.py` | `ResultRow` (p90–p99 + TTL) and `ServiceRunRow` |
| `writers.py` | `append_csv`, `append_jsonl`, `append_history` |
| `main.py` | `--kind service\|manual\|automated\|performance` |

## Usage

```powershell
cd apps\benchmark-runner\file-generator
python main.py --kind performance --language go --test-name K6-load-go --p90-ms 8 --p95-ms 10 --p98-ms 12 --p99-ms 14 --pass
python main.py --kind manual --language python --test-name TC-FUNC-001-python --ttl-ms 40 --pass
python main.py --kind service --language go --port 50054 --up --latency-ms 3
```

`--kind service` writes `service_runs.csv` / `.jsonl`. Other kinds write the matching `*_results` pair (`p99_ms` sits after `p98_ms`).
