# ai-gateway

FastAPI helper for Hermes (and optionally Blazor). **Not** a user-facing chat. Default bind **5082** when run as `__main__` so it does not collide with orchestrator 5081.

| Method | Path | Role |
|--------|------|------|
| GET | `/health` | Liveness + knowledge-base path |
| POST | `/rag/query` | `{ question, top_k }` over `data/knowledge-base/*.md` |
| POST | `/agent/run` | `{ task, payload }` → LangGraph stubs |

```powershell
cd services\ai-gateway
pip install -r requirements.txt
$env:PYTHONPATH = "..\ai-agents\langgraph"
python main.py
```

CreatePerson is never implied here. Writes go through the MCP `grpc_call` tool with explicit confirmation (Hermes skill).
