# k6

gRPC performance and security scripts. Shared addressing lives in `lib/endpoints.js` (`resolveEndpoint`, `personService`, proto path, `defaultThresholds` with p90/p95/p98/p99 on `grpc_req_duration`). **These files have not been executed** as part of scaffolding.

| Script | Profile | Executor (default) |
|--------|---------|--------------------|
| `load.js` | Steady load | constant-vus 10 / 30s |
| `stress.js` | Rising pressure | ramping-vus → 50 |
| `spike.js` | Sudden burst | ramping-vus spike |
| `concurrency.js` | Connection / pool pressure | constant-vus 30 / 20s |
| `endurance.js` | Soak | constant-vus 5 / 2m |
| `scalability.js` | Capacity curve | ramping-vus 0→5→10→20→0 |
| `compare.js` | All six langs per VU | constant-vus 3 / 30s |
| `security.js` | Safe negative payloads | per-vu-iterations |

```powershell
# Install k6, start an API, then:
cd apps\benchmark-runner\k6
k6 run -e LANG=go .\load.js
k6 run -e LANG=python .\stress.js
k6 run -e LANG=java .\spike.js
k6 run -e LANG=node .\concurrency.js
k6 run -e LANG=go .\endurance.js
k6 run -e LANG=go .\scalability.js
k6 run .\compare.js
k6 run -e LANG=csharp .\security.js
```

Optional Prometheus remote-write (compose enables the receiver on Prometheus `:9090`):

```powershell
$env:K6_PROMETHEUS_RW_SERVER_URL = "http://localhost:9090/api/v1/write"
k6 run -e LANG=go --out experimental-prometheus-rw .\load.js
```

Suite wrapper (writes `performance_results` / security rows, including p99):

```powershell
cd apps\benchmark-runner\powershell
.\Invoke-AllLanguagePerf.ps1
.\Invoke-AllLanguagePerf.ps1 -Smoke
```

`LANG` must be one of: `cpp`, `python`, `java`, `go`, `csharp`, `node`. Unset `LANG` defaults to `go` via `lib/endpoints.js`.
