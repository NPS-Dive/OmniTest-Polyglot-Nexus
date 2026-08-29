# MASTER IMPLEMENTATION PROMPT — OmniTest-Polyglot-Nexus

> **Format note:** Markdown is the format this agent should consume. Headings, lists, and fenced code stay parseable. Do not convert this file to `.txt`.
>
> **How to use:** Attach or `@`-mention this file in a new Cursor Agent (Agent mode, not Plan mode) and say: **Implement this prompt against the current repository. Start at Phase A and continue through Phase F.**
>
> **Workspace:** `e:\Shah\Mine\omni\OmniTest-Polyglot-Nexus-main`

---

## ROLE

You are implementing, fixing, and extending the **existing** OmniTest-Polyglot-Nexus monorepo. This is not a greenfield rewrite. Read every file you will change before editing it. Preserve working seed data and existing embeddings.

Your job is to turn the current partial scaffold into a showcase of **clean architecture, SOLID, polyglot gRPC, QA/QC (manual + automated), performance comparison, observability, and a hybrid AI agent**.

---

## THREE NON-NEGOTIABLE RULES (every file, every language)

1. **Clean code structure** — presentation → domain → infrastructure. Composition root only in `main` / `Program` / `index`.
2. **SOLID** — one reason to change per type; repository interfaces in domain; Postgres implementations in infrastructure; no gRPC handler talking to SQL/ORM directly; extend via new implementations (OCP), not by editing core switch statements.
3. **Comments and docs** — file header (purpose, SOLID role, dependencies); comment every type, method, and non-obvious block. Comments explain *why* and *contract*, not syntax. Every app/service/data/shared folder gets a README. Root README must match the real tree and ports.

When you update a file, write the **complete file** with full comments (not a fragment). Do not commit unless the user asks.

---

## MISSION

Implement the remaining platform so a hiring manager can:

1. Start Postgres + observability with Docker Compose.
2. Run six language gRPC services against **isolated tables** in one database.
3. Use the Blazor dashboard to probe services and trigger tests.
4. Run manual and automated tests from PowerShell (single test and run-all).
5. Run k6 load / stress / spike / concurrency / security tests.
6. See live results in Grafana and CLI.
7. Have append-only CSV + JSONL history and ISTQB-aligned bug + managerial QAQC comparison reports.
8. Ask the **OpenClaw + Hermes Agent hybrid** (MCP tools + LangGraph QA skills) about tests, failures, and RAG docs.

---

## LOCKED PRODUCT DECISIONS (do not reopen)

- **Database isolation:** ONE PostgreSQL database `opn_db`. **Table per language**, not database per language.
- Tables (identical schema, identical ~1,000,000 rows): `persons_csharp`, `persons_python`, `persons_java`, `persons_node`, `persons_cpp`, **`persons_golang` (new)**.
- **Do not wipe** the existing Docker volume / embeddings unless a migration copies data first. The 1M embedding backfill is already done for at least one table; skip rows that already have vectors.
- **Include Blazor WebAssembly** dashboard in this wave.
- **C++ gRPC** must be initiated and completed (it is currently a stub).
- **Golang gRPC** must be created from scratch.
- Python stays **gRPC** (not a FastAPI replacement of the Person API). FastAPI is only for `ai-gateway`.
- **Semantic Kernel is skipped in v1** (it would duplicate LangGraph). Document it as a future C# option only.
- **AI hybrid is OpenClaw + Hermes Agent (Nous Research), not “Hermes = an LLM”.** See Phase F. Do not flatten Hermes Agent into a model name.

---

## CURRENT GROUND TRUTH (do not regress)

### What exists on disk today

| Area | Path / fact |
|------|-------------|
| Shared proto | `shared/proto/person_service.proto` — package `omnitest.polyglot.nexus`. RPCs: `CreatePerson`, `ReadAllPersons`, `SearchByFilter`, `SearchByVector`. |
| Compose | `shared/infrastructure/docker-compose.yml` — **only** `pgvector/pgvector:pg16`, DB `opn_db`, user `opn_admin`, password `opn_secret`, port `5432`. |
| Schema | `data/vector-store/02_create_tables.sql` — five tables. **No `persons_golang`.** |
| Seed | `data/master_seed.csv` (~1M rows). Columns: `id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code`. |
| Embeddings | `data/mock-generator/embedding_updater.py` — model `all-MiniLM-L6-v2`, 384-dim, currently hardcoded to `persons_csharp`. |
| Node API | `services/api-node` — port **5079**, 4 RPCs, cleanest layers, proto field drift (`name`/`family`). |
| C# API | `services/api-csharp` — Kestrel **5078**, 4 RPCs, no repository interface, empty `CreatePersonResponse`, old proto names. |
| Python API | `services/api-python` — port **50052**, flat files, stale `person_service_pb2.py`, no interface, no `requirements.txt`. |
| Java API | `services/api-java` — gRPC **50053**, REST 8083, only 2 RPCs wired, schema mismatch, dual JDBC + unused Spring Data, `ddl-auto: update`. |
| C++ API | `services/api-cpp` — port **50051**, stub `main.cpp`, layered files **not linked in CMake**, wrong proto namespace `person::v1`, wrong table `persons`. |
| Go API | **Does not exist.** |
| Mock generator | `data/mock-generator/` — SOLID reference (`models`, `rules`, `factory`, `exporters`, `main`). |
| Root README | Out of date (flat `api-node/` tree, claims database-per-language). |

### Confirmed missing (you must create)

- `apps/blazor-ui`
- `apps/benchmark-runner` (k6, PowerShell, orchestrator, reports)
- `docs/` and `docs/gherkin/`
- `data/knowledge-base/`
- `services/api-go`
- `services/ai-gateway`
- `services/ai-agents`
- OTEL collector, Prometheus, Grafana, Tempo configs
- Per-service READMEs
- Test result history CSV/JSONL
- ISTQB bug templates and managerial reports

---

## SOLVED-ISSUE CATALOG (fix in Phase A / B before new features)

These block fair language comparison. Fix them; do not paper over them.

1. **Proto vs implementations.** Live proto uses `first_name`, `last_name`, `inserted_id`, `top_k`, `gender`, `job_category`, `embedding_vector`. Several services still use `name`/`family`, `id` instead of `inserted_id`, `limit` instead of `top_k`.
2. **Proto vs SQL.** SQL columns: `sex`, `occupation`, `embedding` (VARCHAR categoricals). Proto uses enums plus `birth_date` and `has_passport`. Java INSERT uses `gender`, `birth_date`, `job_category`, `has_passport`, `embedding_vector` and will fail against init SQL.
3. **C++ wiring.** CMake compiles only `main.cpp`. Headers must use package `omnitest.polyglot.nexus` and table `persons_cpp`.
4. **C# DIP.** `PersonGrpcService` uses `AppDbContext` directly. Add `IPersonRepository`. Populate `CreatePersonResponse`. Fix filter field names.
5. **Python layout.** Reshape to `domain/` / `infrastructure/` / `presentation/`. Add repository interface and `requirements.txt`. Regenerate protobuf stubs from the live proto.
6. **Node types.** Replace `any`. Env-based DB config. Implement full `FilterSearchRequest` (`min_age`, `max_age`, `gender`).
7. **Java persistence.** One path only (JDBC **or** Spring Data, not both). Implement all 4 RPCs. Entity = SQL schema. Set `ddl-auto: none`.
8. **Docker seed.** `03_seed_data.sql` uses `\copy ... FROM '../master_seed.csv'` but compose mounts `/master_seed.csv`. `\copy` is unreliable in `docker-entrypoint-initdb.d`. Fix so all language tables receive the same 1M rows.
9. **Index filename.** Rename `4_create_indexes.sql` → `04_create_indexes.sql`.
10. **README truth.** Rewrite root README to the real `services/` + `shared/` + `apps/` + `data/` + `docs/` tree and **table-per-language**.

---

## CANONICAL DATA CONTRACT (all 6 languages map the same way)

### Postgres `persons_*` columns (stored truth)

```
id              UUID PRIMARY KEY
first_name      VARCHAR(100) NOT NULL
last_name       VARCHAR(100) NOT NULL
age             INT NOT NULL CHECK (age >= 0)
sex             VARCHAR(20) NOT NULL      -- proto Sex without prefix, e.g. MALE
marital_status  VARCHAR(20) NOT NULL
children_count  INT NOT NULL CHECK (children_count >= 0)
living_place    VARCHAR(50) NOT NULL
occupation      VARCHAR(50) NOT NULL      -- proto Occupation / job_category
national_code   VARCHAR(10) NOT NULL
embedding       vector(384)
has_passport    BOOLEAN DEFAULT FALSE     -- add via 05_align_optional_columns.sql
```

### Proto mapping

| Proto field | Storage |
|-------------|---------|
| `gender` | column `sex` |
| `job_category` | column `occupation` |
| `embedding_vector` | column `embedding` |
| `birth_date` | derive approximate ISO date from `age` on read (do not re-seed 1M rows) |
| `has_passport` | column `has_passport`; default `false` on existing rows |

Vector search metric: **L2** operator `<->` to match existing HNSW `vector_l2_ops`.

Pagination defaults: `limit` default 50, max 500. `top_k` default 10, max 100.

Codegen: C# / Java / C++ / Go from `shared/proto/person_service.proto` only. Regenerate Python `*_pb2.py` / `*_pb2_grpc.py` from that same file.

---

## TARGET ARCHITECTURE

```
Clients:     Blazor WASM (5080) | PowerShell CLI | k6 | OpenClaw channels (CLI / optional chat)
                |
                v
Optional:    benchmark-runner orchestrator HTTP API (for Blazor to trigger tests)
                |
                v
gRPC:        C++ :50051 | Python :50052 | Java :50053 | Go :50054 | C# :5078 | Node :5079
                |
                v
Postgres:    opn_db → persons_{csharp,python,java,node,cpp,golang}
                |
OTEL:        each API + k6 → otel-collector :4317/:4318 → Prometheus :9090, Tempo :3200 → Grafana :3000
AI hybrid:   User → OpenClaw gateway (entry, light Q&A, session)
                → Hermes Agent (heavy QA, memory, sandbox, subagents)
                → MCP OmniTest tools + LangGraph skills
             ai-gateway FastAPI: /rag/query, /agent/run (also callable by Hermes)
```

### Required layering for every gRPC service

```
src/ (or language equivalent)
  domain/                 # Person entity + IPersonRepository   (DIP / SRP)
  application/            # optional use-cases if mapping is heavy
  infrastructure/
    db/                   # Postgres*Repository
    telemetry/            # OTEL setup
  presentation/grpc/      # proto <-> domain only; no SQL
  main / Program / index  # composition root only
```

---

## PHASE A — Contract and data

Do this first.

1. Lock mapping comments in proto + SQL (do not silently rename proto fields).
2. Fix seed so init and existing volumes can load `/master_seed.csv` into **all six** tables.
3. Add `persons_golang` to `02_create_tables.sql` and indexes.
4. Add `data/vector-store/migrate_add_golang.sql` for databases that already have a volume (init scripts will not re-run).
5. Add `05_align_optional_columns.sql` (`has_passport` on all six tables).
6. Rename `4_create_indexes.sql` → `04_create_indexes.sql`.
7. Extend `embedding_updater.py`: table list argument, skip non-null embeddings, then embed `persons_golang` (and any remaining NULLs). VACUUM ANALYZE after large updates.
8. Update `data/mock-generator/requirements.txt` (`faker`, `psycopg2-binary`, `sentence-transformers`, `numpy`).
9. README in `data/vector-store/` and `data/mock-generator/`.

---

## PHASE B — Finish and create APIs

### Align existing

- **Python:** reshape folders; interface + SQLAlchemy repo on `persons_python`; regenerate stubs; `requirements.txt`; OTEL hook; README.
- **C#:** `IPersonRepository` + EF impl; mapper uses current proto; fill `CreatePersonResponse`; OTEL; README.
- **Node:** env config; typed `Person`; full filter; OTEL; README.
- **Java:** one persistence path; all 4 RPCs; entity = SQL; `ddl-auto: none`; OTEL; README. Delete unused competing repository.

### Initiate C++ (pending → done)

- CMake must compile domain + `PostgresPersonRepository` + `PersonGrpcService` + generated `person_service*.pb.cc`.
- `main.cpp` is composition root only: env → pqxx → repo → service → `0.0.0.0:50051`.
- All 4 RPCs against `persons_cpp`.
- README: Windows-friendly build (vcpkg) and Linux deps (`grpc`, `protobuf`, `libpqxx`).

### Create Golang

- New `services/api-go`: `cmd/server`, `internal/domain`, `internal/infrastructure/db`, `internal/presentation/grpc`.
- Stack: `google.golang.org/grpc`, `pgx`, pgvector, OTEL.
- Table `persons_golang`, port **50054**, all 4 RPCs, README.

After Phase B, each language uses **only its own table**.

---

## PHASE C — OpenTelemetry and Grafana

Extend `shared/infrastructure/docker-compose.yml` (keep Postgres):

- `otel-collector`
- `prometheus`
- `grafana`
- `tempo` (or Jaeger if Tempo is painful on Windows)

Provision:

- Datasources (Prometheus, Tempo).
- Dashboard 1: live gRPC RED (rate, errors, duration) per language.
- Dashboard 2: test-run comparison (p90/p95/p98 side-by-side).

Instrument all 6 APIs: RPC latency histogram, DB query duration, error counts.

k6 must export to Prometheus remote-write or OTLP so a test run appears on Grafana.

README in `shared/infrastructure/`: how to start the stack, Grafana URL, which dashboard to open during k6.

---

## PHASE D — Test suite, history, QAQC reports

Windows-first (PowerShell). Root of tests: `apps/benchmark-runner/`.

### Functional / manual

- One script per case: `powershell/manual/TC-FUNC-001-ReadAll-Python.ps1` (and siblings).
- `Invoke-ManualTest.ps1 -TestId TC-FUNC-001`
- `Invoke-AllManualTests.ps1`
- Coverage: 4 RPCs × 6 languages + edges (empty filter, bad UUID, `top_k=0`, huge `limit`).

### Automated

- `Invoke-AutomatedTests.ps1`
- `Invoke-AllAutomatedTests.ps1`
- Wraps functional cases + k6 smoke.
- CLI table: test name, language, pass/fail, duration, p90, p95, p98, TTL.

### Gherkin / BDD

- `docs/gherkin/*.feature` aligned 1:1 with scenarios/cases.
- Tags: `@functional` `@performance` `@security`.
- Step defs: PowerShell Pester or a small Cucumber runner. Document the mapping in `docs/README.md`.

### k6 (gRPC)

`apps/benchmark-runner/k6/`:

- `load.js`, `stress.js`, `spike.js`, `concurrency.js`, soak if cheap.
- Shared lib: service URL map, thresholds, custom metrics.
- Parameter: `-e LANG=python` (and csharp, java, node, cpp, go).
- Wrapper to run all languages for comparison.

### Security (against this stack only)

Safe payloads: oversized strings, SQL-looking text in name/national_code, long repeated patterns (ReDoS-ish), invalid enums, missing fields, extreme `limit` / `top_k` / `offset`.

Document **expected rejection or safe handling**. Do not write real exploit kits.

### Result storage (append-only)

| File | Purpose |
|------|---------|
| `reports/history/manual_results.csv` + `.jsonl` | each manual run = one new row |
| `reports/history/automated_results.csv` + `.jsonl` | each automated run = one new row |
| `reports/history/performance_results.csv` + `.jsonl` | each k6/perf run = one new row |

**Never overwrite prior runs.**

Required columns: `timestamp_utc`, `test_name`, `test_type` (manual|automated|performance|security), `language`, `p90_ms`, `p95_ms`, `p98_ms`, `ttl_ms`, plus `p50_ms`, `avg_ms`, `max_ms`, `iterations`, `vus`, `fail_rate`, `pass`, `error_message`.

### After every run

1. Human-readable CLI summary.
2. Managerial markdown + HTML: `reports/managerial/run_<timestamp>/` — scenarios, cases, BDD refs, pass/fail, **cross-language comparison**, bugs.
3. On failure: `reports/bugs/BUG-<id>.md` ISTQB content:
   - identifier, title
   - severity: Blocker / Critical / Major / Minor / Trivial
   - priority, environment, module/language
   - precondition, steps to reproduce
   - expected vs actual
   - evidence (log / CSV snippet)
   - isolation (which languages fail)
   - suggestion

QAQC comparison report must rank languages per RPC and per test type (publication-quality, showcase artifact).

---

## PHASE E — Blazor WASM + test orchestrator

`apps/blazor-ui` (host on port **5080**):

- Service status (health or `ReadAllPersons` limit=1 per language).
- Manual actions: Create / ReadAll / Filter / Vector search; language selectable.
- Test control: run one / run all via `apps/benchmark-runner/orchestrator` HTTP API (WASM cannot spawn PowerShell).
- Comparison view: latest p90/p95/p98/TTL per language from report files.
- Link to Grafana.
- Clean C# structure (pages / application services / gRPC or HTTP clients). XML docs + section comments. README.

Verify UI in the browser if tools are available; otherwise say what was verified via CLI.

---

## PHASE F — AI hybrid: OpenClaw + Hermes Agent + MCP + LangGraph

**Do not flatten [Hermes Agent](https://hermes-agent.nousresearch.com/) into “an LLM”.** Hermes Agent (Nous Research) is a full product: persistent memory, self-generated skills, scheduled jobs, isolated subagents, sandbox backends, multi-channel presence.

**Do not treat OpenClaw as an optional thin shell.** OpenClaw is the **gateway**: channels, sessions, routing, light Q&A, Skills marketplace.

They are complementary, not alternatives ([OpenClaw + Hermes dual-stack](https://open-claw.me/blog/openclaw-hermes-dual-stack-deployment)): breadth (OpenClaw) + depth (Hermes). Mix them as one pipeline with **one user entry** and **one long-term memory owner**.

### Split of responsibility (locked)

```
User (CLI, optional Telegram/Discord, Blazor "Ask agent")
        |
        v
[OpenClaw Gateway]          ← ONLY public entry. Channels, short session, routing.
        |
        +-- light: ports, "how do I run TC-FUNC-001?", "open Grafana"
        |
        +-- heavy: compare languages, explain a fail, draft ISTQB bug, RAG+run tests
                |
                v
[Hermes Agent]              ← execution teammate. Memory, sandbox, subagents, skills.
        |
        +-- MCP OmniTest tools (this repo)
        +-- LangGraph skills (deterministic QA graphs)
        +-- ai-gateway /rag/query when docs/vectors are needed
```

| Piece | Role in THIS repo |
|-------|-------------------|
| **OpenClaw** | Gateway only. Owns channel credentials and short-term session (`historyLimit` small). Routes light tasks locally. Forwards heavy QA to Hermes. Relays Hermes results back to the user. Does **not** store long-term test history or duplicate Hermes memory. |
| **Hermes Agent** | Deep worker ([product](https://hermes-agent.nousresearch.com/)). Owns **long-term memory** (past runs, which language was slow, prior bugs). Sandbox for running delegated test/report jobs. Subagents for parallel language checks. Skills that wrap OmniTest MCP + LangGraph. |
| **MCP** | Shared tool bus (not a third chat). Tools: `list_services`, `grpc_call`, `run_test`, `read_last_report`, `query_persons_sql_readonly` (SELECT only), plus `delegate_to_hermes` / `ask_hermes` used by OpenClaw. |
| **LangGraph** | Deterministic QA **skills** inside Hermes, not a user-facing brain. Graphs: `run_comparison`, `explain_failure`, `draft_istqb_bug`, `rag_ask`. OpenClaw never calls LangGraph directly. |
| **Semantic Kernel** | Skip v1. |
| **ai-gateway** | FastAPI: `/rag/query`, `/agent/run`, health. Called by Hermes (and Blazor), not a second chat UI. |

### Hybrid rules (do not violate)

1. **One entry.** Users talk to OpenClaw (or Blazor → OpenClaw/Hermes via ai-gateway). They do not run a second competing chatbot against Hermes.
2. **One-way heavy path.** OpenClaw → Hermes for comparison/bug/RAG-run. Hermes returns a result; OpenClaw only relays. No dual write of reasoning traces into OpenClaw’s DB.
3. **One memory owner.** Hermes keeps long-term memory. OpenClaw keeps only the last few turns.
4. **MCP is the mix layer.** Check in `services/ai-agents/mcp/` (OmniTest tools) and `services/ai-agents/bridge/` (OpenClaw ↔ Hermes). Prefer a small first-party bridge over depending on an unmaintained community repo; document the same pattern as [mcp-coco](https://glama.ai/mcp/servers/Clew-Code/mcp-coco) / dual-stack guides.
5. **LangGraph is a Hermes skill**, invoked when the task must be repeatable (same comparison, same ISTQB fields). Hermes may still use free-form reasoning around that skill.
6. Forward a **minimal payload** to Hermes: user id + current message + channel context. Do not dump OpenClaw’s full history.

### What to create in-repo

- `services/ai-agents/README.md` — how to install OpenClaw + Hermes Agent on Windows, env vars, which tasks are light vs heavy.
- `services/ai-agents/openclaw/` — gateway config, skills that call MCP / `ask_hermes`.
- `services/ai-agents/hermes/` — Hermes skills wrapping LangGraph + OmniTest MCP; memory notes for QAQC.
- `services/ai-agents/mcp/` — OmniTest tool server.
- `services/ai-agents/langgraph/` — the four graphs.
- `services/ai-gateway/` — FastAPI as above.
- `data/knowledge-base/**/*.md` — real docs (architecture, how to run tests, ISTQB process).

RAG sources: knowledge-base markdown **and** person `embedding` in one demo table.

Agent is **read-mostly**. `CreatePerson` only through the gRPC MCP tool with explicit confirmation (Hermes skill or LangGraph interrupt).

Compose: optional `hermes-gateway` on `127.0.0.1` only (do not publish Hermes’ terminal/sandbox port to the LAN). OpenClaw stays the public-facing process.

---

## TARGET TREE (create what is missing; keep what exists)

```
OmniTest-Polyglot-Nexus/
├── MASTER_IMPLEMENTATION_PROMPT.md      # this file
├── README.md
├── apps/
│   ├── blazor-ui/
│   └── benchmark-runner/
│       ├── k6/
│       ├── powershell/
│       ├── orchestrator/
│       └── reports/
├── services/
│   ├── api-csharp/
│   ├── api-cpp/
│   ├── api-java/
│   ├── api-node/
│   ├── api-python/
│   ├── api-go/                          # NEW
│   ├── ai-gateway/                      # NEW FastAPI RAG / agent HTTP
│   └── ai-agents/                       # NEW OpenClaw + Hermes + MCP + LangGraph
├── shared/
│   ├── proto/person_service.proto
│   └── infrastructure/                  # compose + otel + grafana + prometheus
├── data/
│   ├── master_seed.csv
│   ├── mock-generator/
│   ├── vector-store/
│   └── knowledge-base/                  # NEW
└── docs/
    └── gherkin/
```

---

## IMPLEMENTATION ORDER

Execute **A → B → C → D → E → F**. After each phase:

- Services that already existed still compile.
- Proto field names match implementations.
- Each language still queries only its own `persons_*` table.
- New/changed files have comments + folder README.

Do not claim a phase is done unless the files exist and are wired.

---

## OUTPUT RULES

- Edit in place. Remove orphans (unused Java Spring Data repo, C++ stub service left beside the real one).
- Full file contents with comments when a file is rewritten.
- No git commit unless asked.
- No secrets committed. Env vars with current local defaults as fallbacks (`opn_admin` / `opn_secret` / `opn_db` / `localhost:5432`).
- If a tool is missing (grpcurl, k6, browser), install or document the exact command; do not fake results.

---

## START COMMAND (when this file is attached)

Start at **Phase A**. Read `shared/proto/person_service.proto`, `data/vector-store/*.sql`, `shared/infrastructure/docker-compose.yml`, and each `services/api-*` entry point first. Then implement.
