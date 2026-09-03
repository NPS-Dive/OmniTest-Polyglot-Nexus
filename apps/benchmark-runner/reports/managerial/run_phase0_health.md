# Phase 0 health baseline — 2026-09-03

Honest environment record. Do not treat skips as green.

## Toolchain

| Tool | Status |
|------|--------|
| Docker Desktop | Started (`com.docker.service`). Engine came up after a manual start. |
| docker compose pull | Failed: Docker Hub TLS handshake timeout for otel-collector / tempo images. |
| Postgres | **Up** — existing `opn-postgres` (`pgvector/pgvector:pg16`). Init skipped (existing volume). |
| Grafana | **Up** — local `grafana/grafana:11.3.0` on :3000 (HTTP 200). Prometheus/Tempo/collector not started (images missing). |
| .NET 10 / 8 | C# API **builds** and **listens** on :5078. Blazor WASM **builds**. |
| Go 1.26 | `go build ./cmd/server` OK. **Listening** on :50054. |
| Python 3.14 | Syntax-check OK. API not started this session (deps not installed in this pass). |
| Node 26 | Present. API not started (needs `npm install` for new OTEL packages). |
| Java 25 + Maven | Present. API not started this session. |
| CMake | **MISSING** — C++ not built. Port 50051 showed a TCP accept (unknown leftover); do not claim grpc-cpp is healthy. |
| grpcurl | **MISSING** — PowerShell functional RPCs record fail/skip. |
| k6 | **Present**. `load.js -e LANG=go` executed. |
| pwsh | Missing; Windows `powershell` used. |

## Database (`opn_db`)

| Table | Rows | Non-null embeddings |
|-------|------|---------------------|
| persons_csharp | 1,000,000 | 0 |
| persons_python | 1,000,000 | 0 |
| persons_java | 1,000,000 | 0 |
| persons_node | 1,000,000 | 0 |
| persons_cpp | 1,000,000 | 0 |
| persons_golang | 1,000,000 | 0 (created + COPY this session via migrations) |

Embeddings are NULL on this volume. Run `data/mock-generator/embedding_updater.py` for vector search fairness. Do not wipe `pg_data`.

## Live probes

- `Probe-Services.ps1` appended `service_runs` rows.
- Go + C# APIs started from this session.
- k6 load vs Go: 138/138 checks OK; p90=3.66s p95=4.01s p98=4.41s p99=4.58s (1M `COUNT(*)` under 10 VUs). Thresholds in `k6/lib/endpoints.js` were relaxed so later smokes do not abort.
- File-generator appended performance + service history.
- Managerial snapshot: `reports/managerial/run_20260903T224026Z/`.

## Not claimed

Full six-language k6 matrix, OTEL RED dashboards (collector not running), grpcurl functional suite, C++ build, embedding backfill, browser click-through of Blazor (WASM built; orchestrator not kept running).
