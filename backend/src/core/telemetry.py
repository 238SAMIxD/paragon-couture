import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI

def setup_telemetry(app: FastAPI) -> None:
    """
    Set up OpenTelemetry for the FastAPI application.
    Configures a TracerProvider with OTLPSpanExporter (for Jaeger).
    Instruments the FastAPI app.
    """
    if os.getenv("OTEL_ENABLED", "true").lower() in {"0", "false", "no", "off"}:
        return

    resource = Resource.create(attributes={SERVICE_NAME: "paragon-couture"})

    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    tracer_provider = trace.get_tracer_provider()
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower()
        in {"1", "true", "yes", "on"},
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    FastAPIInstrumentor.instrument_app(app)
