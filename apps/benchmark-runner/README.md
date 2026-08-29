# benchmark-runner

Windows-first test harness for the six Person gRPC APIs. History is **append-only**. k6 scripts are present but **have not been executed** unless you run them locally.

## Layout

```
apps/benchmark-runner/
├── config/services.json          # lang → host:port
├── powershell/                   # manual + automated + reports
├── powershell/manual/            # thin TC-FUNC / TC-EDGE wrappers
├── k6/                           # load, stress, spike, concurrency, security
├── orchestrator/                 # FastAPI :5081 (Phase E)
└── reports/                      # history, bugs, managerial
```

## Ports (from services.json)

| Language | Host port | Table |
|----------|-----------|--------|
| cpp | 50051 | persons_cpp |
| python | 50052 | persons_python |
| java | 50053 | persons_java |
| go | 50054 | persons_golang |
| csharp | 5078 | persons_csharp |
| node | 5079 | persons_node |

## Manual (PowerShell)

Requires [grpcurl](https://github.com/fullstorydev/grpcurl/releases) on PATH for a live call. Without it, the runner records a **fail** and a mock-safe skip message (no RPC is sent).

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
.\Invoke-AllManualTests.ps1
.\manual\TC-FUNC-001-ReadAll-Python.ps1
.\New-ManagerialReport.ps1
```

## Automated

```powershell
.\Invoke-AutomatedTests.ps1 -TestId TC-FUNC-001 -Language go
.\Invoke-AllAutomatedTests.ps1
# optional k6 smoke (fails the extra row if k6 is missing):
.\Invoke-AllAutomatedTests.ps1 -SmokeK6
```

## k6

See `k6/README.md`. Example after you install k6 and start `api-go`:

```powershell
cd apps\benchmark-runner\k6
k6 run -e LANG=go .\load.js
```

## Orchestrator (Blazor)

```powershell
cd apps\benchmark-runner\orchestrator
pip install -r requirements.txt
python main.py
```

Listens on `http://127.0.0.1:5081`.
