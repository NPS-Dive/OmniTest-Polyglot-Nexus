# grpc-java — Person gRPC service

Java Spring Boot implementation of `omnitest.polyglot.nexus.PersonService`. It talks **only** to `persons_java` on the shared `opn_db` database.

| Item | Value |
|------|--------|
| Module | `com.omnitest:grpc-java` |
| Listen | `0.0.0.0:50053` (`PORT` overrides) |
| Table | `persons_java` |
| Proto | `shared/proto/person_service.proto` (`com.omnitest.polyglot.nexus.shared.proto`) |
| Vector | L2 `<->` on `embedding vector(384)` |
| Pagination | `limit` default 50 max 500; `top_k` default 10 max 100 |
| Persistence | JDBC only (`JdbcTemplate`). No JPA / Hibernate. |

## Layout (clean architecture)

```
src/main/java/com/omnitest/apijava/
  ApiJavaApplication.java                      composition root
  domain/model/Person.java                     string categoricals + List<Float> embedding
  domain/PersonFilter.java                     SearchByFilter criteria
  domain/repository/PersonRepository.java      save, findAll, findByFilter, searchByVector
  infrastructure/db/PostgresPersonRepositoryImpl.java   SQL only
  infrastructure/telemetry/OtelConfig.java     OTEL (no-op unless endpoint set)
  presentation/grpc/PersonGrpcService.java     4 RPCs, no SQL
  presentation/grpc/PersonMapper.java          proto ↔ domain
src/main/resources/application.yml             env-friendly datasource, gRPC 50053
```

Presentation never imports JDBC. The repository never imports proto types.

## Proto ↔ SQL mapping

| Proto field | Storage |
|-------------|---------|
| `gender` | column `sex` |
| `job_category` | column `occupation` |
| `embedding_vector` | column `embedding` |
| `has_passport` | column `has_passport` |
| `birth_date` | **not stored** — `(current year − age)-01-01` on read |

Canonical columns on `persons_java`: `id UUID`, `first_name`, `last_name`, `age`, `sex VARCHAR`, `marital_status VARCHAR`, `children_count`, `living_place VARCHAR`, `occupation VARCHAR`, `national_code`, `embedding vector(384)`, `has_passport BOOLEAN`.

Not in DB: `birth_date`, `gender` int, `job_category`, `embedding_vector`.

Seed CSV labels are lowercase (`male`, `female`, `bigender`, `agender`, `not specified`, `single parent`, `job seeker`, `full-time`). The API maps those (and `SEX_MALE` / `OCCUPATION_JOB_SEEKER` style names) to proto enums by uppercasing conceptually and turning spaces/hyphens into underscores. New inserts write seed-style labels so they match the existing million rows.

## Environment

| Variable | Default |
|----------|---------|
| `PORT` | `50053` |
| `HTTP_PORT` | `8083` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` / `POSTGRES_DATABASE` | `opn_db` |
| `POSTGRES_USER` | `opn_admin` |
| `POSTGRES_PASSWORD` | `opn_secret` |
| `POSTGRES_SSLMODE` | `disable` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset → **no-op** telemetry |
| `OTEL_SERVICE_NAME` | `grpc-java` |

Start Postgres first (`shared/infrastructure/docker-compose.yml`). Schema is created by `data/vector-store` SQL — Spring does **not** run DDL (`ddl-auto` is not configured).

## Run

From this directory (Java 17+, Maven wrapper included):

```powershell
cd services\grpc-java
.\mvnw.cmd spring-boot:run
```

Or:

```bash
cd services/grpc-java
./mvnw spring-boot:run
```

gRPC reflection is enabled. Example with [grpcurl](https://github.com/fullstorydev/grpcurl):

```powershell
grpcurl -plaintext localhost:50053 list
grpcurl -plaintext localhost:50053 list omnitest.polyglot.nexus.PersonService
grpcurl -plaintext -d "{\"limit\": 5, \"offset\": 0}" localhost:50053 omnitest.polyglot.nexus.PersonService/ReadAllPersons
```

## Generate protobuf stubs

Stubs are generated at build time from `../../shared/proto` into `target/generated-sources/protobuf`. The Maven protobuf plugin runs `compile` and `compile-custom` (grpc-java).

```powershell
cd services\grpc-java
.\mvnw.cmd compile
```

## RPCs

| RPC | Behavior |
|-----|----------|
| `CreatePerson` | Insert into `persons_java`; returns `inserted_id` |
| `ReadAllPersons` | Page + `total_count` (full table) |
| `SearchByFilter` | Optional `first_name`, `last_name`, `min_age`, `max_age`, `gender`, `national_code` |
| `SearchByVector` | L2 `<->`, `top_k` clamped 1–100 (0 → 10) |

## OTEL

Leave `OTEL_EXPORTER_OTLP_ENDPOINT` unset for a silent no-op. When set (for example `localhost:4317`), the process exports traces and metrics over OTLP/gRPC.
