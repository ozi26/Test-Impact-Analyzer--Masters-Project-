# ============================================================================== 
# Unit tests for the OpenTelemetry tracing helper.
# ============================================================================== 

from opentelemetry.sdk.trace import TracerProvider  # Import the SDK tracer provider.
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # Import the simple span processor.
from analyzer.trace_store import DependencyMapExporter  # Import the local JSON dependency exporter.
from analyzer.tracing import record_config_access  # Import the configuration tracing helper.

# ------------------------------------------------------------------------------
# Test that a test span records an exact configuration access.
# ------------------------------------------------------------------------------
def test_trace_records_configuration_access():
    """Check that runtime configuration access is exported correctly."""
    exporter = DependencyMapExporter()  # Create an in-memory exporter.
    provider = TracerProvider()  # Create an isolated tracer provider.
    provider.add_span_processor(SimpleSpanProcessor(exporter))  # Send completed spans to the exporter.
    tracer = provider.get_tracer("test")  # Get a tracer from the isolated provider.

    with tracer.start_as_current_span("test") as span:  # Start an isolated test span.
        span.set_attribute("tia.test_id", "test_checkout")  # Store the test identifier.
        span.set_attribute("tia.test_file", "tests/test_checkout.py")  # Store the test file path.
        record_config_access("sample_microservices/order_service/config.yaml", "inventory.timeout")  # Record the exact setting.

    exporter.force_flush()  # Ensure the exporter has processed the completed span.
    assert len(exporter.records) == 1  # Verify one test record was exported.
    assert exporter.records[0]["test_id"] == "test_checkout"  # Verify the test identifier.
    assert exporter.records[0]["dependencies"][0]["key"] == "inventory.timeout"  # Verify the exact configuration key.
    provider.shutdown()  # Shut down the isolated provider.
