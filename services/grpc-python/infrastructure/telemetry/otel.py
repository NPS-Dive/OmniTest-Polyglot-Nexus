"""
File: infrastructure/telemetry/otel.py
Purpose: Optional OTLP traces + metrics. Histogram rpc.server.duration (ms)
         becomes opn_rpc_server_duration_milliseconds_* on Prometheus.
SOLID: SRP — telemetry bootstrap only. Gated by OTEL_EXPORTER_OTLP_ENDPOINT.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import grpc

logger = logging.getLogger(__name__)

_histogram: Any = None


def _strip(endpoint: str) -> str:
    """Collector wants host:port; tolerate http(s):// prefixes from compose docs."""
    ep = endpoint.strip()
    for prefix in ("https://", "http://"):
        if ep.startswith(prefix):
            ep = ep[len(prefix) :]
    return ep


def setup_telemetry(service_name: str = "grpc-python") -> None:
    """Attach OTLP gRPC exporters when the collector URL is present."""
    global _histogram
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.info("OTEL disabled (OTEL_EXPORTER_OTLP_ENDPOINT unset).")
        return
    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        ep = _strip(endpoint)
        resource = Resource.create({"service.name": service_name})

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=ep, insecure=True)))
        trace.set_tracer_provider(provider)

        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=ep, insecure=True))
        meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)
        meter = metrics.get_meter(service_name)
        _histogram = meter.create_histogram("rpc.server.duration", unit="ms")
        logger.info("OTEL traces+metrics -> %s", ep)
    except Exception as exc:
        logger.warning("OTEL setup skipped: %s", exc)


def record_rpc(duration_ms: float, status_code: str = "0") -> None:
    """Record one RPC duration. No-op when telemetry is disabled."""
    if _histogram is None:
        return
    _histogram.record(duration_ms, {"rpc.grpc.status_code": status_code, "service.name": "grpc-python"})


class RpcMetricsInterceptor(grpc.ServerInterceptor):
    """gRPC server interceptor — records rpc.server.duration for Grafana RED."""

    def intercept_service(self, continuation, handler_call_details):  # type: ignore[no-untyped-def]
        handler = continuation(handler_call_details)
        if handler is None or handler.unary_unary is None:
            return handler

        inner = handler.unary_unary

        def wrapper(request, context):  # type: ignore[no-untyped-def]
            started = time.perf_counter()
            try:
                return inner(request, context)
            finally:
                code = "0"
                try:
                    code = str(int(context.code().value[0])) if context.code() else "0"
                except Exception:
                    code = "2"
                record_rpc((time.perf_counter() - started) * 1000.0, code)

        return grpc.unary_unary_rpc_method_handler(
            wrapper,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )
