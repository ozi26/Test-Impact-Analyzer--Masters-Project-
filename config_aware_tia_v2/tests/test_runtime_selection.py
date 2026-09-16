# ============================================================================== 
# Unit tests for runtime configuration-aware test selection.
# ============================================================================== 

from analyzer.config_selection import ConfigurationAwareSelector  # Import the runtime selector.

# ------------------------------------------------------------------------------
# Test exact configuration file and key matching.
# ------------------------------------------------------------------------------
def test_runtime_configuration_selection():
    """Select only tests that used the changed configuration setting."""
    selector = ConfigurationAwareSelector()  # Create the runtime selector.
    selector.load_records([  # Load two traced test records.
        {
            "test_id": "test_checkout",  # Identify the checkout test.
            "test_file": "tests/test_checkout.py",  # Store its test file.
            "dependencies": [  # Store the settings accessed by the test.
                {"file": "sample_microservices/order_service/config.yaml", "key": "inventory.timeout"},  # Record the inventory timeout dependency.
            ],
        },
        {
            "test_id": "test_pricing_timeout",  # Identify the pricing test.
            "test_file": "tests/test_pricing.py",  # Store its test file.
            "dependencies": [  # Store the settings accessed by the test.
                {"file": "sample_microservices/pricing_service/config.yaml", "key": "timeout"},  # Record the pricing timeout dependency.
            ],
        },
    ])  # Finish loading the test records.
    result = selector.select_tests([  # Change only the inventory timeout setting.
        {"file": "sample_microservices/order_service/config.yaml", "key": "inventory.timeout"},  # Define the changed setting.
    ])  # Run runtime-based selection.
    assert len(result) == 1  # Verify that one test was selected.
    assert result[0]["test_file"] == "tests/test_checkout.py"  # Verify the correct impacted test.
