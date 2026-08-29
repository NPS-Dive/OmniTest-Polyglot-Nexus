// ==============================================================================
// File: apps/blazor-ui/Services/OrchestratorApi.cs
// Purpose: Typed HTTP client for the :5081 orchestrator (WASM cannot spawn PS).
// SOLID: SRP — transport only. Pages decide what to render.
// ==============================================================================

using System.Net.Http.Json;
using OmniTest.BlazorUi.Models;

namespace OmniTest.BlazorUi.Services;

/// <summary>Calls the benchmark orchestrator. BaseAddress is set in Program.cs.</summary>
public sealed class OrchestratorApi
{
    private readonly HttpClient _http;

    public OrchestratorApi(HttpClient http)
    {
        _http = http;
    }

    /// <summary>TCP status of the six gRPC ports.</summary>
    public Task<ServiceStatusResponse?> GetStatusAsync() =>
        _http.GetFromJsonAsync<ServiceStatusResponse>("services/status");

    /// <summary>Tail of history JSONL files (may be empty arrays).</summary>
    public Task<LatestReportsResponse?> GetLatestReportsAsync() =>
        _http.GetFromJsonAsync<LatestReportsResponse>("reports/latest");

    /// <summary>Run one catalogued test (Invoke-ManualTest.ps1).</summary>
    public async Task<string> RunTestAsync(string testId, string language)
    {
        var res = await _http.PostAsJsonAsync("tests/run", new RunTestRequest
        {
            TestId = testId,
            Language = language
        });
        return await res.Content.ReadAsStringAsync();
    }

    /// <summary>Run the full manual loop.</summary>
    public async Task<string> RunAllAsync()
    {
        var res = await _http.PostAsync("tests/run-all", null);
        return await res.Content.ReadAsStringAsync();
    }

    /// <summary>Probe one RPC through the orchestrator.</summary>
    public async Task<string> ProbeAsync(string language, string rpc)
    {
        var res = await _http.PostAsJsonAsync("probe", new ProbeRequest
        {
            Language = language,
            Rpc = rpc
        });
        return await res.Content.ReadAsStringAsync();
    }
}
