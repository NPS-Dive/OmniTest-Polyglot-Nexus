# k6

gRPC performance and security scripts. **These files have not been executed** as part of scaffolding.

```powershell
# Install k6, start an API, then:
cd apps\benchmark-runner\k6
k6 run -e LANG=go .\load.js
k6 run -e LANG=python .\stress.js
k6 run -e LANG=java .\spike.js
k6 run -e LANG=node .\concurrency.js
k6 run -e LANG=csharp .\security.js
```

Optional Prometheus remote-write (compose enables the receiver):

```powershell
$env:K6_PROMETHEUS_RW_SERVER_URL = "http://localhost:9090/api/v1/write"
k6 run -e LANG=go --out experimental-prometheus-rw .\load.js
```

`LANG` must be one of: `cpp`, `python`, `java`, `go`, `csharp`, `node`.
