# grafana (provisioning)

File-mounted Grafana assets used by `docker-compose.yml`.

| Path | Role |
|------|------|
| `provisioning/datasources/datasources.yml` | Prometheus + Tempo |
| `provisioning/dashboards/dashboards.yml` | File provider → `/var/lib/grafana/dashboards` |
| `dashboards/grpc-red.json` | Live RED per language |
| `dashboards/test-comparison.json` | k6 p90/p95/p98 |

Do not edit dashboards only inside the Grafana UI if you want them to survive `docker compose down -v`. Edit the JSON here.
