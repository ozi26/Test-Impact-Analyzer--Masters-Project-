# ============================================================================== 
# Runtime tracing demonstration for the sample microservices.
# This module records the exact configuration settings used by each test.
# ============================================================================== 

import json  # Import JSON support for writing the dependency map.
import sys  # Import Python path support.
from pathlib import Path  # Import Path for project-path handling.

# ------------------------------------------------------------------------------
# Find the project root before importing the local analyzer package.
# ------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]  # Calculate the project root from this file.
sys.path.insert(0, str(ROOT))  # Allow the script to import the analyzer package.

from analyzer.telemetry import configure_tracing  # Import the local OpenTelemetry setup.
from analyzer.tracing import record_config_access, trace_test  # Import test and configuration tracing helpers.

# ------------------------------------------------------------------------------
# Trace one logical test and its runtime configuration accesses.
# ------------------------------------------------------------------------------
def run_test(test_id, test_file, accesses):
    """Create a test span and record every configuration setting it accesses."""
    with trace_test(test_id, test_file) as span:  # Start one span representing the test.
        for config_file, config_key in accesses:  # Visit every configuration setting used by the test.
            record_config_access(config_file, config_key)  # Record the exact file and configuration key.
        span.add_event("test.completed")  # Record that the demonstration test completed.

# ------------------------------------------------------------------------------
# Generate the complete runtime dependency map.
# ------------------------------------------------------------------------------
def main():
    """Create a runtime test-to-configuration dependency map."""
    exporter = configure_tracing("tia-sample-tests")  # Configure OpenTelemetry once for this process.
    run_test(  # Trace the checkout test and its two inventory settings.
        "test_checkout",  # Give the test a stable identifier.
        "tests/test_checkout.py",  # Store the physical test file.
        [
            ("sample_microservices/order_service/config.yaml", "inventory.timeout"),  # Trace the inventory timeout used by checkout.
            ("sample_microservices/order_service/config.yaml", "inventory.retry.attempts"),  # Trace the inventory retry setting used by checkout.
        ],
    )
    run_test(  # Trace the inventory retry test.
        "test_inventory_retry",  # Give the test a stable identifier.
        "tests/test_inventory.py",  # Store the physical test file.
        [
            ("sample_microservices/order_service/config.yaml", "inventory.retry.attempts"),  # Trace the inventory retry setting used by the test.
        ],
    )
    run_test(  # Trace the pricing timeout test.
        "test_pricing_timeout",  # Give the test a stable identifier.
        "tests/test_pricing.py",  # Store the physical test file.
        [
            ("sample_microservices/pricing_service/config.yaml", "timeout"),  # Trace the pricing timeout setting used by the test.
        ],
    )
    exporter.force_flush()  # Ensure all completed spans have reached the in-memory exporter.
    output_file = ROOT / "trace-map.json"  # Define the runtime dependency-map output path.
    output_file.write_text(json.dumps(exporter.records, indent=2), encoding="utf-8")  # Save the dependency map as JSON.
    print(f"Runtime dependency map written to: {output_file}")  # Tell the user where the map was saved.

# ------------------------------------------------------------------------------
# Start the tracing demonstration when this file is executed directly.
# ------------------------------------------------------------------------------
if __name__ == "__main__":  # Check whether the script was started directly.
    main()  # Start the runtime tracing demonstration.
