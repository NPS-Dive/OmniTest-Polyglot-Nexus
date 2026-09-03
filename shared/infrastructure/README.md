# shared/infrastructure

Local Docker stack for OmniTest-Polyglot-Nexus: one Postgres (`opn_db`, table-per-language) plus the Phase C observability path.

This folder does **not** run the six gRPC APIs. Those stay on the host and talk to `localhost:5432` and optionally `localhost:4317`.

## Services and ports

| Container | Image role | Host ports | Notes |
|-----------|------------|------------|--------|
| `opn-postgres` | PostgreSQL 16 + pgvector | `5432` | DB `opn_db`, user `opn_admin`, password `opn_secret` |
| `opn-otel-collector` | OTLP intake | `4317` (gRPC), `4318` (HTTP), `8889` (Prom scrape) | Set `OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4317` on APIs |
| `opn-prometheus` | Metrics | `9090` | Remote-write receiver on for k6 |
| `opn-tempo` | Traces | `3200` | OTLP is internal; collector forwards |
| `opn-grafana` | Dashboards | `3000` | Anonymous Admin **or** `admin` / `admin` |

## Start

From this directory (PowerShell):

```powershell
cd shared\infrastructure
docker compose up -d
docker compose ps
```

First-time Postgres will run `data/vector-store/01`–`05` and `COPY` `/master_seed.csv` into all six `persons_*` tables. That can take several minutes. Existing `pg_data` volumes **do not** re-run init scripts — use `data/vector-store/migrations/` instead of wiping the volume.

Stop (keep volumes):

```powershell
docker compose down
```

## Grafana

- URL: [http://localhost:3000](http://localhost:3000)
- Auth: anonymous Admin is enabled; login `admin` / `admin` also works.

**Which dashboard during a k6 run**

1. Folder **OmniTest** → **gRPC RED — six languages** (`uid: opn-grpc-red`) while APIs are serving. Six per-language rate panels plus shared rate / error / p95.
2. Folder **OmniTest** → **Test-run comparison — p90 / p95 / p98 / p99** (`uid: opn-test-comparison`) while k6 is remote-writing.

C++ without the OTEL SDK publishes Prometheus text on host `:15051` (`METRICS_PORT`). Compose Prometheus scrapes `host.docker.internal:15051`.

Provisioned datasources: **Prometheus** (`http://prometheus:9090`), **Tempo** (`http://tempo:3200`).

## Point APIs and k6 at the collector

```powershell
$env:OTEL_EXPORTER_OTLP_ENDPOINT = "localhost:4317"
```

k6 → Prometheus (this compose already enables the receiver):

```powershell
$env:K6_PROMETHEUS_RW_SERVER_URL = "http://localhost:9090/api/v1/write"
k6 run -e LANG=go --out experimental-prometheus-rw ..\..\apps\benchmark-runner\k6\load.js
```

Those k6 commands are **not** executed by this README. After you run them, the comparison dashboard should light up.

## Layout

```
shared/infrastructure/
├── docker-compose.yml
├── otel-collector-config.yaml
├── prometheus.yml
├── tempo.yaml
├── grafana/provisioning/datasources/datasources.yml
├── grafana/provisioning/dashboards/dashboards.yml
└── grafana/dashboards/grpc-red.json
    grafana/dashboards/test-comparison.json
```
