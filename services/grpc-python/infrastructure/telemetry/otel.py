"""
File: infrastructure/telemetry/otel.py
Purpose: Optional OTLP export. No-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set
so local gRPC still starts without the collector (Phase C wires the endpoint).
SOLID: SRP — telemetry bootstrap only.
"""

import logging
import os

logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str = "grpc-python") -> None:
    """Attach OTLP gRPC exporter when the collector URL is present."""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.info("OTEL disabled (OTEL_EXPORTER_OTLP_ENDPOINT unset).")
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        trace.set_tracer_provider(provider)
        logger.info("OTEL traces -> %s", endpoint)
    except Exception as exc:
        logger.warning("OTEL setup skipped: %s", exc)
