# grpc-python

gRPC Person service on **port 50052**, table **`persons_python` only**.

## Layers

| Path | Role |
|------|------|
| `domain/` | `Person`, `PersonFilter`, `IPersonRepository` |
| `infrastructure/db/` | SQLAlchemy + `persons_python` + L2 `<->` |
| `infrastructure/telemetry/` | OTEL if `OTEL_EXPORTER_OTLP_ENDPOINT` is set |
| `presentation/grpc/` | proto mapping (`first_name`, `inserted_id`, `top_k`) |
| `main.py` | Composition root |

## Run

```powershell
cd services/grpc-python
pip install -r requirements.txt
python generate_proto.py
python main.py
```

Env: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `PORT`.
