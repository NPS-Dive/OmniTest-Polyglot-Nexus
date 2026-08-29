# grpc-csharp

ASP.NET Core gRPC Person service on **Kestrel 5078**, table **`persons_csharp` only**.

The folder is `grpc-csharp`. The .NET assembly/namespace stays `OmniTest.Polyglot.Nexus.Api.CSharp` so existing project files do not need a C# rename.

## Layers

- `Domain/` — `Person`, `PersonFilter`, `IPersonRepository`
- `Infrastructure/Data/` — EF `AppDbContext` + `PostgresPersonRepository` (L2)
- `Mappers/PersonMapper.cs` — proto `first_name` / `inserted_id` / `top_k`
- `Services/PersonGrpcService.cs` — no SQL
- `Program.cs` — composition root

```powershell
cd services/grpc-csharp
dotnet run
```

Env: `POSTGRES_*`, `OTEL_EXPORTER_OTLP_ENDPOINT`.
