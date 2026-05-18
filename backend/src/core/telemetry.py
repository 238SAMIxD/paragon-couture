from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI

def setup_telemetry(app: FastAPI) -> None:
    """
    Set up OpenTelemetry for the FastAPI application.
    Configures a TracerProvider with ConsoleSpanExporter (for development).
    Instruments the FastAPI app.
    """
    # Set the tracer provider
    trace.set_tracer_provider(TracerProvider())
    
    # Get the tracer provider
    tracer_provider = trace.get_tracer_provider()
    
    # Add a console span exporter for development
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)