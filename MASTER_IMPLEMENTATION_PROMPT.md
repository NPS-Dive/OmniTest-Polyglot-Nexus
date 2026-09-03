# MASTER IMPLEMENTATION PROMPT — OmniTest-Polyglot-Nexus (Ground Truth)

> **How to use:** Agent mode. Start at Phase 0. Workspace: this repo root.
>
> Folders are `services/grpc-*`, **not** `api-*`. Do not re-implement solved Phase A/B issues from the 2025 scaffold prompt.

## Locked decisions

- One database `opn_db`. Table per language: `persons_{csharp,python,java,node,cpp,golang}`.
- Proto: `shared/proto/person_service.proto`, package `omnitest.polyglot.nexus`.
- Ports: C++ 50051, Python 50052, Java 50053, Go 50054, C# 5078, Node 5079, Blazor 5080, orchestrator 5081, ai-gateway 5082.
- History percentiles: p50, p90, p95, p98, **p99**, avg, max, ttl.
- AI: OpenClaw gateway + Hermes Agent worker + MCP + LangGraph skills. Semantic Kernel skipped in v1.
- Security tests: safe payloads only.

## Already done (do not regress)

Six gRPC APIs with all 4 RPCs, DIP repositories, SQL 01–05 + golang migrations, compose (Postgres + OTEL + Prometheus + Tempo + Grafana), Blazor, PowerShell runners, k6 profiles (load/stress/spike/concurrency/endurance/scalability/compare/security), file-generator, Gherkin, knowledge-base, AI scaffold.

## Remaining / keep honest

- Docker Desktop must be running before compose.
- CMake and grpcurl are optional on Windows; record skips, do not invent metrics.
- C++ OTEL is a host `/metrics` fallback on :15051 (Prometheus scrapes `host.docker.internal`).
- Embeddings: run `data/mock-generator/embedding_updater.py` after a fresh seed (skips non-null).

## Fairness contract

`ReadAllPersons` / `SearchByFilter` `total_count` = `COUNT(*)`. Vector search `total_count` = returned neighbours. Categorical writes use seed labels (`male`, `full-time`, `job seeker`).

## Phase order

0. Health: compose, table counts, toolchain, Probe-Services.ps1.
1. Fairness leftovers (total_count, C++ seed labels, Python DIP, Node types).
2. OTEL `rpc.server.duration` (ms) → collector namespace `opn` → Grafana RED.
3. k6 + file-generator + p99 history + managerial + characteristics table.
4. Blazor Compare includes p99; orchestrator `/reports/latest`.
5. MCP `grpc_call` via grpcurl (`CreatePerson` needs `confirm=true`); LangGraph deterministic graphs.
6. README / comment audit.

See root [README.md](README.md) and [docs/benchmark-characteristics.md](docs/benchmark-characteristics.md).
