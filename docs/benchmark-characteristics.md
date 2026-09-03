# ==============================================================================
# File: docs/benchmark-characteristics.md
# Purpose: Fair-comparison sheet — runtime, GC, typing, gRPC stack, persistence,
#          OTEL, port, and table for each Person API. Percentiles are placeholders
#          until Phase 3 k6 suites are actually executed.
# SOLID: SRP — documentation only. Numbers come from reports/history after a run.
# Dependencies: services/grpc-*/README.md, config/services.json, k6/lib/endpoints.js
# ==============================================================================

# Benchmark characteristics (six Person APIs)

Isolation is **table-per-language** on one `opn_db`. Ports match `apps/benchmark-runner/config/services.json` and `k6/lib/endpoints.js`.

Phase 0 live k6 (`load.js`, 10 VUs / 30s, `ReadAllPersons` limit=10) against **Go** on a 1M-row table: p90=3660 ms, p95=4010 ms, p98=4410 ms, p99=4580 ms (138/138 gRPC OK; COUNT(*) dominates). Other languages: not run in this environment.

| Language | Runtime | GC | Typing | gRPC stack | Persistence | OTEL status | Port | Table | Latest p90 | Latest p95 | Latest p98 | Latest p99 |
|----------|---------|----|--------|------------|-------------|-------------|------|-------|------------|------------|------------|------------|
| C++ | Native (CMake / MSVC or g++) | None (RAII / no GC) | Static | grpc++ + protobuf | libpqxx → `persons_cpp` | Host Prometheus `/metrics` on :15051 (`rpc` histogram); OTLP SDK not linked | 50051 | `persons_cpp` | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 |
| Python | CPython 3 | Refcount + cyclic GC | Dynamic (type hints) | grpcio | SQLAlchemy → `persons_python` | OTLP traces+metrics + interceptor when `OTEL_EXPORTER_OTLP_ENDPOINT` is set | 50052 | `persons_python` | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 |
| Java | JVM 17+ (Spring Boot) | HotSpot / G1 (typical) | Static | grpc-spring-boot + protobuf | JDBC `JdbcTemplate` (no JPA) → `persons_java` | OTLP traces+metrics + global interceptor when endpoint is set | 50053 | `persons_java` | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 |
| Go | Go 1.22+ runtime | Concurrent GC | Static | `google.golang.org/grpc` | pgx → `persons_golang` | OTLP traces+metrics + unary interceptor when endpoint is set | 50054 | `persons_golang` | 3660 ms (k6 load 10 VU / 30s) | 4010 ms | 4410 ms | 4580 ms |
| C# | .NET / CLR (Kestrel) | Generational GC | Static | Grpc.AspNetCore | EF Core → `persons_csharp` | OTLP traces+metrics + `RpcMetricsInterceptor` when endpoint is set | 5078 | `persons_csharp` | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 |
| Node | Node.js / V8 | V8 generational GC | TypeScript (compile-time) | `@grpc/grpc-js` + proto-loader | `pg` + pgvector → `persons_node` | OTLP traces+metrics via `@opentelemetry/*` when endpoint is set | 5079 | `persons_node` | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 | not run — see Phase 0 |

k6 profiles: `load.js`, `stress.js`, `spike.js`, `concurrency.js`, `endurance.js`, `scalability.js`, `compare.js` (plus `security.js` for safe negatives). Wrapper: `apps/benchmark-runner/powershell/Invoke-AllLanguagePerf.ps1`.
