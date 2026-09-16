# ============================================================================== 
# OpenTelemetry helpers for runtime test-to-configuration tracing.
# ============================================================================== 

from contextlib import contextmanager  # Import contextmanager for readable test tracing blocks.
from opentelemetry import trace  # Import the OpenTelemetry tracing API.

# Give the project tracer a stable name.
TRACER_NAME = "configuration-aware-tia"

# ------------------------------------------------------------------------------
# Return the project's OpenTelemetry tracer.
# ------------------------------------------------------------------------------
def get_tracer():
    """Return the tracer used by the project."""
    return trace.get_tracer(TRACER_NAME)  # Return the named tracer.

# ------------------------------------------------------------------------------
# Create one span representing one test execution.
# ------------------------------------------------------------------------------
@contextmanager  # Turn the function into a context manager.
def trace_test(test_id, test_file=None):
    """Create a test span and attach test metadata."""
    tracer = get_tracer()  # Get the project tracer.
    with tracer.start_as_current_span("test") as span:  # Start one test span.
        span.set_attribute("tia.test_id", str(test_id))  # Store the test identifier on the span.
        if test_file is not None:  # Check whether the physical test file is known.
            span.set_attribute("tia.test_file", str(test_file))  # Store the physical test file.
        yield span  # Give the caller access to the active span.

# ------------------------------------------------------------------------------
# Record one exact runtime configuration access.
# ------------------------------------------------------------------------------
def record_config_access(config_file, config_key):
    """Attach one configuration file/key dependency to the current test span."""
    span = trace.get_current_span()  # Get the active test span.
    if not span.is_recording():  # Check whether the active span is recording data.
        return  # Stop when tracing is not active.
    span.add_event(  # Add one configuration-access event to the span.
        "configuration.access",  # Give the event a stable name.
        {  # Store the exact dependency information.
            "config.file": str(config_file),  # Store the configuration file path.
            "config.key": str(config_key),  # Store the exact configuration key.
        },
    )

# ------------------------------------------------------------------------------
# Convert one completed span into a JSON-friendly dependency record.
# ------------------------------------------------------------------------------
def export_span_dependency(span_data):
    """Extract test and configuration dependencies from a completed span."""
    dependencies = []  # Create an empty dependency list.
    for event in span_data.events:  # Visit every event recorded on the span.
        if event.name != "configuration.access":  # Ignore events that are not configuration accesses.
            continue  # Move to the next event.
        attributes = dict(event.attributes or {})  # Convert event attributes into a normal dictionary.
        dependencies.append({  # Save one configuration dependency.
            "file": str(attributes.get("config.file", "")),  # Store the configuration file.
            "key": str(attributes.get("config.key", "")),  # Store the configuration key.
        })
    return {  # Return the complete test dependency record.
        "test_id": str(span_data.attributes.get("tia.test_id", "")),  # Store the test identifier.
        "test_file": str(span_data.attributes.get("tia.test_file", "")),  # Store the test file path.
        "dependencies": dependencies,  # Store all exact configuration accesses.
    }
