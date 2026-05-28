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
    resource = Resource.create(attributes={
        SERVICE_NAME: "paragon-couture"
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    tracer_provider = trace.get_tracer_provider()
    
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    FastAPIInstrumentor.instrument_app(app)