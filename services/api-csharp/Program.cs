using Microsoft.EntityFrameworkCore;
using OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Data;
using OmniTest.Polyglot.Nexus.Api.CSharp.Services;

var builder = WebApplication.CreateBuilder(args);

// 1. Add gRPC services to the container.
builder.Services.AddGrpc();

// 2. Add gRPC Reflection for Postman testing (Option A for our UI/Testing)
builder.Services.AddGrpcReflection();

// 3. Configure PostgreSQL with pgvector support
// We pull the connection string from appsettings.json
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString, o => o.UseVector()));

var app = builder.Build();

// 4. Map the gRPC Service implementation
app.MapGrpcService<PersonGrpcService>();

// 5. Enable Reflection in Development mode so Postman can read the .proto contract dynamically
if (app.Environment.IsDevelopment())
{
    app.MapGrpcReflectionService();
}

// 6. Root endpoint fallback for standard HTTP GET requests
app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client like Postman.");

app.Run();
