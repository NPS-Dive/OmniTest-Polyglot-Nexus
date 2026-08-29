# ai-agents — OpenClaw + Hermes Agent hybrid

This folder is **scaffolding**: configs, MCP tools, LangGraph stubs, and a first-party OpenClaw ↔ Hermes bridge. It does not install those products for you.

## Split of responsibility (locked)

```
User → OpenClaw Gateway (only public entry: channels, short session, routing)
         ├─ light: ports, "how do I run TC-FUNC-001?", "open Grafana"
         └─ heavy → Hermes Agent (memory, sandbox, subagents, skills)
                      ├─ MCP OmniTest tools (this repo)
                      ├─ LangGraph QA graphs
                      └─ ai-gateway /rag/query
```

- **One entry.** Do not run a second competing chatbot against Hermes.
- **One memory owner.** Hermes keeps long-term test history. OpenClaw keeps a small `historyLimit`.
- **LangGraph** is a Hermes skill, not a user-facing brain.
- **Semantic Kernel** is skipped in v1.

### Light vs heavy

| Light (OpenClaw locally) | Heavy (forward to Hermes) |
|--------------------------|---------------------------|
| Port map, Grafana URL | Cross-language comparison |
| “How do I run TC-FUNC-001?” | Explain a fail + draft ISTQB bug |
| Which table does Go use? | RAG + run tests via MCP |

## Install on Windows

### OpenClaw (gateway)

1. Node 20+ LTS.
2. Follow current docs: [OpenClaw](https://open-claw.me/) / `npx` or global CLI as published that week (the product name and installer move — check the official site).
3. Copy `openclaw/openclaw.json.example` to a local `openclaw.json` (do not commit secrets). Keep `historyLimit` small.
4. Point a skill at `bridge/ask_hermes.py` for heavy tasks.
5. Bind the gateway to localhost unless you intend to expose chat.

### Hermes Agent (Nous Research)

1. Read [Hermes Agent](https://hermes-agent.nousresearch.com/) for the current Windows install (CLI, Docker, or pip — use what the product documents today).
2. Give Hermes **long-term memory** for past runs and bugs. Do not duplicate that store in OpenClaw.
3. Register MCP server: `python services/ai-agents/mcp/server.py` (stdio or the transport Hermes supports).
4. Skills: see `hermes/skills.md` (wrap LangGraph + MCP).
5. If you use Docker, publish Hermes only on `127.0.0.1` (do not expose sandbox/terminal ports on the LAN).

### Environment (examples — names vary by product)

```
OPENCLAW_GATEWAY_PORT=18789
HERMES_BASE_URL=http://127.0.0.1:8642
OPN_ORCHESTRATOR=http://127.0.0.1:5081
OPN_AI_GATEWAY=http://127.0.0.1:5082
POSTGRES_HOST=localhost
POSTGRES_USER=opn_admin
POSTGRES_PASSWORD=opn_secret
POSTGRES_DB=opn_db
```

Do not commit real channel tokens. Use `.env` (gitignored).

## Layout

```
services/ai-agents/
├── mcp/server.py          # list_services, grpc_call (stub), run_test, …
├── bridge/ask_hermes.py   # OpenClaw → Hermes minimal payload
├── langgraph/graphs.py    # four deterministic stubs
├── openclaw/openclaw.json.example
└── hermes/skills.md
```
