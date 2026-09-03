/**
 * @file infrastructure/telemetry/otel.ts
 * @description Optional OTLP traces + metrics for grpc-node.
 * Histogram rpc.server.duration (ms) → opn_rpc_server_duration_milliseconds_* .
 * SOLID: SRP — bootstrap only. Gated by OTEL_EXPORTER_OTLP_ENDPOINT.
 */

import { metrics, trace } from '@opentelemetry/api';

let enabled = false;

function strip(endpoint: string): string {
    return endpoint.replace(/^https?:\/\//i, '').trim();
}

export async function setupTelemetry(serviceName = 'grpc-node'): Promise<void> {
    const raw = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
    if (!raw) {
        console.log('[OTEL] disabled (OTEL_EXPORTER_OTLP_ENDPOINT unset).');
        return;
    }
    try {
        const [{ Resource }, { NodeTracerProvider, BatchSpanProcessor }, { OTLPTraceExporter }] = await Promise.all([
            import('@opentelemetry/resources'),
            import('@opentelemetry/sdk-trace-node'),
            import('@opentelemetry/exporter-trace-otlp-grpc')
        ]);
        const { MeterProvider, PeriodicExportingMetricReader } = await import('@opentelemetry/sdk-metrics');
        const { OTLPMetricExporter } = await import('@opentelemetry/exporter-metrics-otlp-grpc');
        const { SemanticResourceAttributes } = await import('@opentelemetry/semantic-conventions');

        const endpoint = strip(raw);
        const resource = new Resource({ [SemanticResourceAttributes.SERVICE_NAME]: serviceName });

        const tracerProvider = new NodeTracerProvider({ resource });
        tracerProvider.addSpanProcessor(new BatchSpanProcessor(new OTLPTraceExporter({ url: endpoint })));
        tracerProvider.register();

        const meterProvider = new MeterProvider({
            resource,
            readers: [
                new PeriodicExportingMetricReader({
                    exporter: new OTLPMetricExporter({ url: endpoint }),
                    exportIntervalMillis: 15000
                })
            ]
        });
        metrics.setGlobalMeterProvider(meterProvider);
        enabled = true;
        console.log(`[OTEL] traces+metrics -> ${endpoint}`);
        void trace;
    } catch (error) {
        console.warn('[OTEL] setup skipped', error);
    }
}

export function recordRpc(durationMs: number, statusCode = '0'): void {
    if (!enabled) return;
    const histogram = metrics.getMeter('grpc-node').createHistogram('rpc.server.duration', { unit: 'ms' });
    histogram.record(durationMs, { 'rpc.grpc.status_code': statusCode, 'service.name': 'grpc-node' });
}
