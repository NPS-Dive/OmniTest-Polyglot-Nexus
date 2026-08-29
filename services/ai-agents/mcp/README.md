# mcp

OmniTest tools for Hermes (and the OpenClaw → Hermes path). Run `python server.py --demo` for `list_services`. stdio: one JSON line `{"tool":"read_last_report","args":{"limit":5}}` per request.

`query_persons_sql_readonly` rejects non-SELECT. `grpc_call` is a **stub** (no live exploit or silent CreatePerson).
