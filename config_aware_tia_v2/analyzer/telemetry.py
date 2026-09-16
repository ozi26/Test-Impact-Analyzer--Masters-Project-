# ============================================================================== 
# OpenTelemetry setup used by the runtime tracing demonstration.
# ============================================================================== 

from opentelemetry import trace  # Import the OpenTelemetry global tracing API.
from opentelemetry.sdk.resources import Resource  # Import resource metadata support.
from opentelemetry.sdk.trace import TracerProvider  # Import the OpenTelemetry SDK tracer provider.
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # Import the synchronous span processor.
from .trace_store import DependencyMapExporter  # Import the local JSON dependency exporter.

# ------------------------------------------------------------------------------
# Configure OpenTelemetry once for the current Python process.
# ------------------------------------------------------------------------------
def configure_tracing(service_name="configuration-aware-tia"):
    """Install a local OpenTelemetry provider and return its exporter."""
    resource = Resource.create({"service.name": service_name})  # Give generated spans a readable service name.
    provider = TracerProvider(resource=resource)  # Create a new SDK tracer provider.
    exporter = DependencyMapExporter()  # Create the in-memory dependency collector.
    provider.add_span_processor(SimpleSpanProcessor(exporter))  # Send completed spans to the collector.
    trace.set_tracer_provider(provider)  # Make this provider the process-wide OpenTelemetry provider.
    return exporter  # Return the exporter so the caller can save the dependency map.
