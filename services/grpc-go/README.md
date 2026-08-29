# api-go — Person gRPC service

Go implementation of `omnitest.polyglot.nexus.PersonService`. It talks **only** to `persons_golang` on the shared `opn_db` database.

| Item | Value |
|------|--------|
| Module | `github.com/omnitest/api-go` |
| Listen | `0.0.0.0:50054` (`PORT` overrides) |
| Table | `persons_golang` |
| Proto | `shared/proto/person_service.proto` |
| Vector | L2 `<->` on `embedding vector(384)` |
| Pagination | `limit` default 50 max 500; `top_k` default 10 max 100 |

## Layout (clean architecture)

```
cmd/server/main.go                         composition root
internal/domain/                           Person, PersonFilter, PersonRepository
internal/infrastructure/db/                pgx adapter (SQL only)
internal/infrastructure/telemetry/         OTEL (no-op unless endpoint set)
internal/presentation/grpc/                proto mapping + 4 RPCs
internal/gen/                              generated personpb stubs
internal/config/                           env → Config
```

Presentation never imports pgx. The repository never imports proto types.

## Proto ↔ SQL mapping

| Proto field | Storage |
|-------------|---------|
| `gender` | column `sex` |
| `job_category` | column `occupation` |
| `embedding_vector` | column `embedding` |
| `has_passport` | column `has_passport` |
| `birth_date` | **not stored** — `(current year − age)-01-01` on read |

Seed CSV labels are lowercase (`male`, `job seeker`, `full-time`, `single parent`). The API maps those (and `SEX_MALE` / `OCCUPATION_JOB_SEEKER` style names) to proto enums. New inserts write seed-style labels so they match the existing million rows.

## Environment

| Variable | Default |
|----------|---------|
| `PORT` | `50054` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` / `POSTGRES_DATABASE` | `opn_db` |
| `POSTGRES_USER` | `opn_admin` |
| `POSTGRES_PASSWORD` | `opn_secret` |
| `POSTGRES_SSLMODE` | `disable` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset → **no-op** telemetry |
| `OTEL_SERVICE_NAME` | `api-go` |

Start Postgres first (`shared/infrastructure/docker-compose.yml`). Existing volumes need `data/vector-store/migrations/migrate_add_golang.sql` if `persons_golang` is missing.

## Run

From this directory (Go 1.22+). If both 32-bit and 64-bit Go are installed, prefer the 64-bit `go` on PATH.

```powershell
cd services\api-go
go run ./cmd/server
```

Or:

```powershell
make run
```

gRPC reflection is enabled. Example with [grpcurl](https://github.com/fullstorydev/grpcurl):

```powershell
grpcurl -plaintext localhost:50054 list
grpcurl -plaintext localhost:50054 list omnitest.polyglot.nexus.PersonService
grpcurl -plaintext -d "{\"limit\": 5, \"offset\": 0}" localhost:50054 omnitest.polyglot.nexus.PersonService/ReadAllPersons
```

## Generate protobuf stubs

Stubs under `internal/gen/` are **committed** so the server builds without `protoc`. Regenerate after proto changes.

### Prerequisites

1. [`protoc`](https://github.com/protocolbuffers/protobuf/releases) on PATH (tested with 29.3).
2. Plugins:

```powershell
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.5
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1
```

Add `$(go env GOPATH)\bin` to PATH.

### Windows

```powershell
cd services\api-go
.\scripts\generate.ps1
```

Or:

```powershell
go generate -tags generate ./...
```

### Linux / macOS / Make

```bash
cd services/api-go
make generate
```

### Exact `protoc` command

Run from `services/api-go`:

```bash
protoc -I ../../shared/proto \
  --go_out=internal/gen --go_opt=paths=source_relative \
  --go_opt=Mperson_service.proto=github.com/omnitest/api-go/internal/gen \
  --go-grpc_out=internal/gen --go-grpc_opt=paths=source_relative \
  --go-grpc_opt=Mperson_service.proto=github.com/omnitest/api-go/internal/gen \
  person_service.proto
```

The shared proto also has `option go_package = "github.com/omnitest/api-go/internal/gen;personpb"`.

If `protoc` is not installed, keep the committed `internal/gen/*.pb.go` files and use the script above when you can install the compiler.

## RPCs

| RPC | Behavior |
|-----|----------|
| `CreatePerson` | Insert into `persons_golang`; returns `inserted_id` |
| `ReadAllPersons` | Page + `total_count` (full table) |
| `SearchByFilter` | Optional `first_name`, `last_name`, `min_age`, `max_age`, `gender`, `national_code` |
| `SearchByVector` | L2 `<->`, `top_k` clamped 1–100 (0 → 10) |

## OTEL

Leave `OTEL_EXPORTER_OTLP_ENDPOINT` unset for a silent no-op. When set (for example `localhost:4317`), the process exports traces and metrics over OTLP/gRPC and attaches the otelgrpc server stats handler.
