// ============================================================================
// File: services/grpc-java/src/main/java/com/omnitest/apijava/infrastructure/telemetry/OtelConfig.java
// Purpose: Optional OpenTelemetry setup. No-op unless OTEL_EXPORTER_OTLP_ENDPOINT
//          is set, so local `mvn spring-boot:run` stays quiet without a collector.
// SOLID: SRP — telemetry bootstrap only. Callers keep using OpenTelemetry.getTracer.
// Dependencies: OTLP gRPC exporters, SDK trace + metric. Gated by env, not YAML.
// ============================================================================

package com.omnitest.apijava.infrastructure.telemetry;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * Installs global TracerProvider + MeterProvider when an OTLP endpoint is configured.
 * Otherwise it leaves {@link OpenTelemetry#noop()} in place so local/dev stays silent.
 */
@Configuration
public class OtelConfig {

    private static final Logger log = LoggerFactory.getLogger(OtelConfig.class);

    private OpenTelemetrySdk sdk;

    /**
     * Why env-gated: the rest of the platform may not have started otel-collector yet.
     */
    public static boolean enabled() {
        String endpoint = System.getenv("OTEL_EXPORTER_OTLP_ENDPOINT");
        return endpoint != null && !endpoint.isBlank();
    }

    /**
     * Collector host:port with any {@code http(s)://} prefix stripped.
     */
    public static String endpoint() {
        String ep = System.getenv("OTEL_EXPORTER_OTLP_ENDPOINT");
        if (ep == null) {
            return "";
        }
        ep = ep.trim();
        if (ep.startsWith("https://")) {
            ep = ep.substring("https://".length());
        } else if (ep.startsWith("http://")) {
            ep = ep.substring("http://".length());
        }
        return ep;
    }

    @Bean
    public OpenTelemetry openTelemetry() {
        if (!enabled()) {
            log.info("OTEL_EXPORTER_OTLP_ENDPOINT unset; using no-op OpenTelemetry");
            return OpenTelemetry.noop();
        }

        String serviceName = envOr("OTEL_SERVICE_NAME", "grpc-java");
        String collector = endpoint();
        String otlpUrl = "http://" + collector;

        Resource resource = Resource.getDefault().merge(
                Resource.create(Attributes.of(AttributeKey.stringKey("service.name"), serviceName))
        );

        OtlpGrpcSpanExporter spanExporter = OtlpGrpcSpanExporter.builder()
                .setEndpoint(otlpUrl)
                .build();
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
                .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
                .setResource(resource)
                .build();

        OtlpGrpcMetricExporter metricExporter = OtlpGrpcMetricExporter.builder()
                .setEndpoint(otlpUrl)
                .build();
        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
                .registerMetricReader(
                        PeriodicMetricReader.builder(metricExporter)
                                .setInterval(Duration.ofSeconds(15))
                                .build())
                .setResource(resource)
                .build();

        sdk = OpenTelemetrySdk.builder()
                .setTracerProvider(tracerProvider)
                .setMeterProvider(meterProvider)
                .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
                .buildAndRegisterGlobal();

        log.info("OTLP exporter configured at {} (service={})", collector, serviceName);
        return sdk;
    }

    @PreDestroy
    public void shutdown() {
        if (sdk != null) {
            sdk.getSdkTracerProvider().shutdown();
            sdk.getSdkMeterProvider().shutdown();
        }
    }

    private static String envOr(String key, String fallback) {
        String value = System.getenv(key);
        return value == null || value.isBlank() ? fallback : value.trim();
    }
}
