// ==============================================================================
// File: Program.cs
// Purpose: Composition root — DI, gRPC, reflection, EF + IPersonRepository.
// SOLID: no business logic. OTEL is a no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set.
// ==============================================================================

using Microsoft.EntityFrameworkCore;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain;
using OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Data;
using OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Telemetry;
using OmniTest.Polyglot.Nexus.Api.CSharp.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddGrpc(options => options.Interceptors.Add<RpcMetricsInterceptor>());
builder.Services.AddSingleton<RpcMetricsInterceptor>();
builder.Services.AddGrpcReflection();
OtelSetup.AddIfConfigured(builder.Services);

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Host=localhost;Port=5432;Database=opn_db;Username=opn_admin;Password=opn_secret";

// Env overrides keep compose/k8s portable without rewriting appsettings.
var host = Environment.GetEnvironmentVariable("POSTGRES_HOST");
if (!string.IsNullOrWhiteSpace(host))
{
    connectionString =
        $"Host={host};Port={Environment.GetEnvironmentVariable("POSTGRES_PORT") ?? "5432"};" +
        $"Database={Environment.GetEnvironmentVariable("POSTGRES_DB") ?? "opn_db"};" +
        $"Username={Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "opn_admin"};" +
        $"Password={Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "opn_secret"}";
}

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString, o => o.UseVector()));
builder.Services.AddScoped<IPersonRepository, PostgresPersonRepository>();

var app = builder.Build();
app.MapGrpcService<PersonGrpcService>();
if (app.Environment.IsDevelopment())
    app.MapGrpcReflectionService();
app.MapGet("/", () => "grpc-csharp gRPC on this host. Use a gRPC client.");
app.Run();
