// ==============================================================================
// File: apps/blazor-ui/Models/Dtos.cs
// Purpose: JSON DTOs matching the orchestrator FastAPI responses.
// SOLID: SRP — data shapes only. HTTP lives in OrchestratorApi.
// ==============================================================================

using System.Text.Json.Serialization;

namespace OmniTest.BlazorUi.Models;

/// <summary>One language row from GET /services/status.</summary>
public sealed class ServiceStatusItem
{
    public string Language { get; set; } = "";
    public string Host { get; set; } = "";
    public int Port { get; set; }
    public string? Table { get; set; }
    public bool Up { get; set; }
}

/// <summary>GET /services/status envelope.</summary>
public sealed class ServiceStatusResponse
{
    public List<ServiceStatusItem> Services { get; set; } = new();
}

/// <summary>GET /reports/latest — last JSONL objects per bucket.</summary>
public sealed class LatestReportsResponse
{
    public List<Dictionary<string, object?>> Manual { get; set; } = new();
    public List<Dictionary<string, object?>> Automated { get; set; } = new();
    public List<Dictionary<string, object?>> Performance { get; set; } = new();
}

/// <summary>POST /tests/run body (camelCase for FastAPI alias testId).</summary>
public sealed class RunTestRequest
{
    [JsonPropertyName("testId")]
    public string TestId { get; set; } = "TC-FUNC-001";

    [JsonPropertyName("language")]
    public string Language { get; set; } = "go";
}

/// <summary>POST /probe body.</summary>
public sealed class ProbeRequest
{
    public string Language { get; set; } = "go";
    public string Rpc { get; set; } = "ReadAllPersons";
}
