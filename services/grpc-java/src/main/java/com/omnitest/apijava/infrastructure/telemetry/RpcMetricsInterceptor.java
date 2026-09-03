// ============================================================================
// File: infrastructure/telemetry/RpcMetricsInterceptor.java
// Purpose: Time every unary RPC as rpc.server.duration (ms) for Grafana RED.
//          Collector namespace opn → opn_rpc_server_duration_milliseconds_*.
// SOLID: SRP — interceptor only. No-op when OpenTelemetry is noop.
// ============================================================================

package com.omnitest.apijava.infrastructure.telemetry;

import io.grpc.ForwardingServerCall;
import io.grpc.Metadata;
import io.grpc.ServerCall;
import io.grpc.ServerCallHandler;
import io.grpc.ServerInterceptor;
import io.grpc.Status;
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.DoubleHistogram;
import net.devh.boot.grpc.server.interceptor.GrpcGlobalServerInterceptor;
import org.springframework.stereotype.Component;

/**
 * Global gRPC interceptor. Records duration even when the SDK is no-op (then discarded).
 */
@Component
@GrpcGlobalServerInterceptor
public class RpcMetricsInterceptor implements ServerInterceptor {

    private static final AttributeKey<String> STATUS = AttributeKey.stringKey("rpc.grpc.status_code");
    private static final AttributeKey<String> SERVICE = AttributeKey.stringKey("service.name");

    private final DoubleHistogram duration = GlobalOpenTelemetry.getMeter("grpc-java")
            .histogramBuilder("rpc.server.duration")
            .setUnit("ms")
            .build();

    @Override
    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
            ServerCall<ReqT, RespT> call,
            Metadata headers,
            ServerCallHandler<ReqT, RespT> next) {
        long started = System.nanoTime();
        ServerCall<ReqT, RespT> wrapping = new ForwardingServerCall.SimpleForwardingServerCall<>(call) {
            @Override
            public void close(Status status, Metadata trailers) {
                double ms = (System.nanoTime() - started) / 1_000_000.0;
                String code = status == null ? "2" : String.valueOf(status.getCode().value());
                duration.record(ms, Attributes.of(STATUS, code, SERVICE, "grpc-java"));
                super.close(status, trailers);
            }
        };
        return next.startCall(wrapping, headers);
    }
}
