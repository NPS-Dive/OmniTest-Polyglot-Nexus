// ==============================================================================
// File: Infrastructure/Telemetry/RpcMetricsInterceptor.cs
// Purpose: Time every unary RPC as rpc.server.duration (ms) for Grafana RED.
// SOLID: SRP — interceptor only. Meter is a no-op unless OTEL SDK is registered.
// ==============================================================================

using Grpc.Core;
using Grpc.Core.Interceptors;
using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Telemetry;

/// <summary>Records rpc.server.duration for each inbound gRPC call.</summary>
public sealed class RpcMetricsInterceptor : Interceptor
{
    private static readonly Meter Meter = new(OtelSetup.MeterName);
    private static readonly Histogram<double> Duration = Meter.CreateHistogram<double>(
        OtelSetup.DurationInstrument, unit: "ms");

    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request,
        ServerCallContext context,
        UnaryServerMethod<TRequest, TResponse> continuation)
    {
        var sw = Stopwatch.StartNew();
        try
        {
            return await continuation(request, context);
        }
        finally
        {
            var code = context.Status.StatusCode == StatusCode.OK ? "0" : ((int)context.Status.StatusCode).ToString();
            Duration.Record(sw.Elapsed.TotalMilliseconds, new TagList
            {
                { "rpc.grpc.status_code", code },
                { "service.name", "grpc-csharp" }
            });
        }
    }
}
