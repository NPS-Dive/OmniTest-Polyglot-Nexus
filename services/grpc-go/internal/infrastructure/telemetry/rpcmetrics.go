// ============================================================================
// File: services/grpc-go/internal/infrastructure/telemetry/rpcmetrics.go
// Purpose: rpc.server.duration histogram (ms) for Grafana RED.
//          Collector namespace opn → opn_rpc_server_duration_milliseconds_*.
// SOLID: SRP — metric helper + unary interceptor. No-op when OTEL is disabled.
// ============================================================================

package telemetry

import (
	"context"
	"strconv"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
	"google.golang.org/grpc"
	"google.golang.org/grpc/status"
)

var duration metric.Float64Histogram

func init() {
	meter := otel.Meter("grpc-go")
	h, err := meter.Float64Histogram("rpc.server.duration", metric.WithUnit("ms"))
	if err == nil {
		duration = h
	}
}

// RecordRPC records one unary RPC duration. Safe when providers are no-op.
func RecordRPC(ctx context.Context, elapsed time.Duration, statusCode int) {
	if duration == nil {
		return
	}
	duration.Record(ctx, float64(elapsed.Milliseconds()), metric.WithAttributes(
		attribute.String("rpc.grpc.status_code", strconv.Itoa(statusCode)),
		attribute.String("service.name", "grpc-go"),
	))
}

// UnaryMetricsInterceptor times every unary RPC for the Grafana RED dashboard.
func UnaryMetricsInterceptor() grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req any, _ *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
		started := time.Now()
		resp, err := handler(ctx, req)
		code := 0
		if err != nil {
			code = int(status.Code(err))
		}
		RecordRPC(ctx, time.Since(started), code)
		return resp, err
	}
}
