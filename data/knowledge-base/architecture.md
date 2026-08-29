<!--
File: data/knowledge-base/architecture.md
Purpose: RAG-ready description of the real OmniTest-Polyglot-Nexus architecture.
SOLID: documentation only — no runtime coupling.
-->

# Architecture

OmniTest-Polyglot-Nexus is a **monorepo** that compares six implementations of the same gRPC `PersonService` (`omnitest.polyglot.nexus`) against **one PostgreSQL database** (`opn_db`) with **one table per language**. Isolation is not database-per-language.

## Tables

| Language | Process | Port | Table |
|----------|---------|------|--------|
| C++ | `services/api-cpp` | 50051 | `persons_cpp` |
| Python | `services/api-python` | 50052 | `persons_python` |
| Java | `services/api-java` | 50053 | `persons_java` |
| Go | `services/api-go` | 50054 | `persons_golang` |
| C# | `services/api-csharp` | 5078 | `persons_csharp` |
| Node | `services/api-node` | 5079 | `persons_node` |

Schema is shared: `id`, `first_name`, `last_name`, `age`, `sex`, `marital_status`, `children_count`, `living_place`, `occupation`, `national_code`, `embedding vector(384)`, `has_passport`. Proto field `gender` maps to `sex`; `job_category` maps to `occupation`; `embedding_vector` maps to `embedding`. `birth_date` is derived on read.

RPCs: `CreatePerson`, `ReadAllPersons` (limit default 50, max 500), `SearchByFilter`, `SearchByVector` (L2 `<->`, `top_k` default 10, max 100).

## Layers (every API)

Presentation (gRPC) maps proto ↔ domain. Domain owns `Person` and `IPersonRepository`. Infrastructure owns Postgres and optional OTEL. `main` / `Program` / `index` is the composition root only.

## Compose (Phase C)

`shared/infrastructure/docker-compose.yml` starts Postgres plus otel-collector (4317/4318), Prometheus (9090), Tempo (3200), Grafana (3000). APIs stay on the host and export to `localhost:4317`.

## Clients

- Blazor WASM `apps/blazor-ui` :5080
- Orchestrator `apps/benchmark-runner/orchestrator` :5081
- PowerShell + k6 under `apps/benchmark-runner`
- AI: OpenClaw (entry) → Hermes (heavy) → MCP + LangGraph + `services/ai-gateway`
