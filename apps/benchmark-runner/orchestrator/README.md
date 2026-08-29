# orchestrator

Small FastAPI process on **port 5081**. Blazor WASM calls this instead of spawning PowerShell in the browser.

| Method | Path | Role |
|--------|------|------|
| GET | `/health` | Liveness |
| GET | `/services/status` | TCP up/down per language |
| GET | `/reports/latest` | Tail of history JSONL |
| POST | `/tests/run` | `{ "testId", "language" }` → `Invoke-ManualTest.ps1` |
| POST | `/tests/run-all` | `Invoke-AllManualTests.ps1` |
| POST | `/probe` | `{ language, rpc }` → `Invoke-FunctionalRpc.ps1` |

```powershell
cd apps\benchmark-runner\orchestrator
pip install -r requirements.txt
python main.py
```

CORS allows `http://localhost:5080`. grpcurl must be on PATH for functional calls; otherwise scripts record a mock-safe skip.
