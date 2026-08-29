# shared

Cross-language assets. Person services under `services/grpc-*` all consume these.

| Path | Role |
|------|------|
| [proto/](proto/README.md) | Single `person_service.proto` contract |
| [infrastructure/](infrastructure/README.md) | Docker Compose: Postgres, OTEL, Prometheus, Grafana, Tempo |

Do not fork the proto per language. Table names (`persons_*`) are not defined here — they live in `data/vector-store`.
