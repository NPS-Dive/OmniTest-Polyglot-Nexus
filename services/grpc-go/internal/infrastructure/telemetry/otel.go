// ============================================================================
// File: services/grpc-go/internal/infrastructure/telemetry/otel.go
// Purpose: Optional OpenTelemetry setup. No-op unless OTEL_EXPORTER_OTLP_ENDPOINT
//          is set, so local `go run` stays quiet without a collector.
// SOLID: SRP — telemetry bootstrap only. Callers keep using otel.Tracer/Meter.
// Dependencies: OTLP gRPC exporters, SDK trace + metric. gRPC stats hook is
//               registered in the composition root when Enabled() is true.
// ============================================================================

// Package telemetry installs OTLP exporters when OTEL_EXPORTER_OTLP_ENDPOINT is set.
package telemetry

import (
	"context"
	"os"
	"strings"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

// ShutdownFunc flushes exporters. Always safe to call (may be a no-op).
type ShutdownFunc func(ctx context.Context) error

// Enabled reports whether an OTLP collector endpoint was configured.
// Why env-gated: the rest of the platform may not have started otel-collector yet.
func Enabled() bool {
	return strings.TrimSpace(os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")) != ""
}

// Endpoint returns the collector host:port with any http(s):// prefix stripped.
func Endpoint() string {
	ep := strings.TrimSpace(os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
	ep = strings.TrimPrefix(ep, "https://")
	ep = strings.TrimPrefix(ep, "http://")
	return ep
}

// Init installs global TracerProvider + MeterProvider when Enabled().
// Otherwise it leaves the default no-op providers in place and returns a no-op shutdown.
func Init(ctx context.Context, serviceName string) (ShutdownFunc, error) {
	noop := func(context.Context) error { return nil }
	if !Enabled() {
		return noop, nil
	}
	if serviceName == "" {
		serviceName = "grpc-go"
	}

	res, err := resource.New(ctx,
		resource.WithFromEnv(),
		resource.WithProcess(),
		resource.WithTelemetrySDK(),
		resource.WithAttributes(semconv.ServiceName(serviceName)),
	)
	if err != nil {
		return noop, err
	}

	ep := Endpoint()
	traceExp, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(ep),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		return noop, err
	}

	metricExp, err := otlpmetricgrpc.New(ctx,
		otlpmetricgrpc.WithEndpoint(ep),
		otlpmetricgrpc.WithInsecure(),
	)
	if err != nil {
		_ = traceExp.Shutdown(ctx)
		return noop, err
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExp),
		sdktrace.WithResource(res),
	)
	mp := sdkmetric.NewMeterProvider(
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(metricExp, sdkmetric.WithInterval(15*time.Second))),
		sdkmetric.WithResource(res),
	)

	otel.SetTracerProvider(tp)
	otel.SetMeterProvider(mp)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	return func(ctx context.Context) error {
		var first error
		if err := tp.Shutdown(ctx); err != nil && first == nil {
			first = err
		}
		if err := mp.Shutdown(ctx); err != nil && first == nil {
			first = err
		}
		return first
	}, nil
}
