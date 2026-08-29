// ==============================================================================
// File: apps/blazor-ui/Program.cs
// Purpose: WASM composition root — HttpClient + OrchestratorApi only.
// SOLID: DIP — pages depend on OrchestratorApi, not raw URLs.
// Dependencies: Microsoft.AspNetCore.Components.WebAssembly
// ==============================================================================

using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using OmniTest.BlazorUi;
using OmniTest.BlazorUi.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

var orchestrator = builder.Configuration["OrchestratorBaseUrl"] ?? "http://127.0.0.1:5081";
builder.Services.AddScoped(_ => new HttpClient { BaseAddress = new Uri(orchestrator) });
builder.Services.AddScoped<OrchestratorApi>();

await builder.Build().RunAsync();
