// ==============================================================================
// File: Infrastructure/Telemetry/OtelSetup.cs
// Purpose: Optional OTLP traces + metrics. Histogram name rpc.server.duration
//          (unit ms) becomes opn_rpc_server_duration_milliseconds_* after the
//          collector Prometheus exporter (namespace opn).
// SOLID: SRP — bootstrap only. Gated by OTEL_EXPORTER_OTLP_ENDPOINT.
// ==============================================================================

using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Telemetry;

/// <summary>Composition-root helper. No-op unless the collector endpoint is set.</summary>
public static class OtelSetup
{
    public const string MeterName = "grpc-csharp";
    public const string DurationInstrument = "rpc.server.duration";

    /// <summary>Strip http(s):// so the OTLP gRPC exporter gets host:port.</summary>
    public static string? Endpoint()
    {
        var raw = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT");
        if (string.IsNullOrWhiteSpace(raw)) return null;
        return raw.Replace("https://", "", StringComparison.OrdinalIgnoreCase)
                  .Replace("http://", "", StringComparison.OrdinalIgnoreCase)
                  .Trim();
    }

    public static void AddIfConfigured(IServiceCollection services)
    {
        var endpoint = Endpoint();
        if (endpoint is null)
        {
            Console.WriteLine("[OTEL] disabled (OTEL_EXPORTER_OTLP_ENDPOINT unset).");
            return;
        }

        services.AddOpenTelemetry()
            .ConfigureResource(r => r.AddService("grpc-csharp"))
            .WithTracing(t => t
                .AddAspNetCoreInstrumentation()
                .AddOtlpExporter(o =>
                {
                    o.Endpoint = new Uri($"http://{endpoint}");
                }))
            .WithMetrics(m => m
                .AddMeter(MeterName)
                .AddAspNetCoreInstrumentation()
                .AddOtlpExporter(o =>
                {
                    o.Endpoint = new Uri($"http://{endpoint}");
                }));

        Console.WriteLine($"[OTEL] traces+metrics -> {endpoint}");
    }
}
