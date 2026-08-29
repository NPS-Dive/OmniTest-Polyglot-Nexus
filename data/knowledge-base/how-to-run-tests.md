<!--
File: data/knowledge-base/how-to-run-tests.md
Purpose: RAG-ready operator guide for manual, automated, and k6 tests.
-->

# How to run tests

Windows PowerShell first. History is append-only under `apps/benchmark-runner/reports/history/`.

## Prerequisites

1. `docker compose up -d` from `shared/infrastructure` (Postgres at least).
2. Start the language API you intend to hit.
3. Install [grpcurl](https://github.com/fullstorydev/grpcurl/releases) for functional tests. If it is missing, runners **skip the RPC** and record `pass=false` with an install hint (mock-safe skip).
4. Install [k6](https://k6.io/docs/get-started/installation/) only if you want performance scripts. Scaffolding does **not** mean k6 already ran.

## One test

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
```

Catalog: `TC-FUNC-001` ReadAll, `TC-FUNC-002` Filter, `TC-FUNC-003` Vector, `TC-FUNC-004` Create, `TC-EDGE-001` empty filter, `TC-EDGE-002` huge limit, `TC-EDGE-003` top_k=0, `TC-EDGE-004` SQL-looking name.

Languages: `cpp`, `python`, `java`, `go`, `csharp`, `node`.

## All functional (loops, not 24 copies)

```powershell
.\Invoke-AllManualTests.ps1
.\Invoke-AllAutomatedTests.ps1
.\New-ManagerialReport.ps1
```

Thin wrappers: `powershell/manual/TC-FUNC-001-ReadAll-Python.ps1` and siblings.

## k6 (you must run these yourself)

```powershell
cd apps\benchmark-runner\k6
k6 run -e LANG=go .\load.js
k6 run -e LANG=go --out experimental-prometheus-rw .\load.js
```

Set `K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write` when using remote-write. Grafana: http://localhost:3000 dashboard **Test-run comparison**.

## UI

1. `python apps/benchmark-runner/orchestrator/main.py` → :5081
2. `dotnet run --project apps/blazor-ui` → :5080
3. Home = status, Probe = RPCs, Tests = run one/all, Compare = latest JSONL
