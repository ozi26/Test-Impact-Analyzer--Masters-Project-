# ============================================================================== 
# In-memory OpenTelemetry exporter used to build the runtime dependency map.
# ============================================================================== 

import json  # Import JSON support for saving the dependency map.
from pathlib import Path  # Import Path for safe output-file handling.
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult  # Import the OpenTelemetry exporter classes.
from .tracing import export_span_dependency  # Import the span-to-record conversion helper.

# ------------------------------------------------------------------------------
# Collect runtime dependency records without a database.
# ------------------------------------------------------------------------------
class DependencyMapExporter(SpanExporter):
    """Collect test spans and save their configuration dependencies as JSON."""

    # --------------------------------------------------------------------------
    # Create an empty exporter.
    # --------------------------------------------------------------------------
    def __init__(self):
        self.records = []  # Store completed test dependency records in memory.

    # --------------------------------------------------------------------------
    # Receive completed spans from OpenTelemetry.
    # --------------------------------------------------------------------------
    def export(self, spans):
        """Collect completed test spans."""
        for span in spans:  # Visit every completed span.
            if span.name == "test":  # Keep only spans representing tests.
                self.records.append(export_span_dependency(span))  # Convert and store the dependency record.
        return SpanExportResult.SUCCESS  # Tell OpenTelemetry that export succeeded.

    # --------------------------------------------------------------------------
    # Shut down the exporter.
    # --------------------------------------------------------------------------
    def shutdown(self):
        """Shut down the exporter."""
        return None  # No external resource needs to be closed.

    # --------------------------------------------------------------------------
    # Flush the exporter.
    # --------------------------------------------------------------------------
    def force_flush(self, timeout_millis=30000):
        """Report success because records are held in memory."""
        return True  # Return success because no remote exporter is involved.

    # --------------------------------------------------------------------------
    # Save the dependency map as JSON.
    # --------------------------------------------------------------------------
    def save(self, output_file):
        """Write captured dependency records to a JSON file."""
        path = Path(output_file)  # Convert the output location into a Path object.
        path.parent.mkdir(parents=True, exist_ok=True)  # Create the output directory when needed.
        path.write_text(json.dumps(self.records, indent=2), encoding="utf-8")  # Save readable dependency data.
