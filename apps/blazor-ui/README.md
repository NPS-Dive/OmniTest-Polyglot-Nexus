# blazor-ui

Blazor WebAssembly dashboard on **http://localhost:5080**. It talks only to the orchestrator on **http://127.0.0.1:5081** (CORS is enabled there).

| Page | Route | Behavior |
|------|-------|----------|
| Home | `/` | Service TCP status |
| Probe | `/probe` | Create / ReadAll / Filter / Vector + language dropdown |
| Tests | `/tests` | Run one / run all |
| Compare | `/compare` | Latest report JSON + Grafana comparison link |
| Grafana | external | [http://localhost:3000](http://localhost:3000) |

## Run

```powershell
cd apps\blazor-ui
dotnet run
```

Start the orchestrator first (`apps/benchmark-runner/orchestrator`). Without it, Home shows a connection error.

Requires .NET 8 SDK. This project is a complete WASM host (`csproj`, `Program.cs`, `App.razor`, pages, `wwwroot/index.html`).
