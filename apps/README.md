# apps

Client-facing apps. They do **not** own Person data — that stays in `services/api-*` and `opn_db`.

| App | Port | Role |
|-----|------|------|
| `benchmark-runner` | orchestrator `5081` | PowerShell + k6 + report history + HTTP trigger API |
| `blazor-ui` | `5080` | WASM dashboard: status, probe, tests, compare, Grafana link |
