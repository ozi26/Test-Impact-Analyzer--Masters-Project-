# ============================================================================== 
# End-to-end test for the Configuration-Aware Test Impact Analyzer.
# ============================================================================== 

import json  # Import JSON support for the generated runtime dependency map.
import subprocess  # Import subprocess for creating a temporary Git history.
from analyzer.analyzer import analyze_repository  # Import the complete analyzer engine.

# ------------------------------------------------------------------------------
# Run one Git command in a temporary repository.
# ------------------------------------------------------------------------------
def git(cwd, *args):
    """Run one Git command and check that it succeeds."""
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)  # Execute the Git command.

# ------------------------------------------------------------------------------
# Test a real configuration change from Git to test selection.
# ------------------------------------------------------------------------------
def test_end_to_end_configuration_change(tmp_path):
    """Check that a changed config key selects the traced impacted test."""
    git(tmp_path, "init", "-q")  # Initialize a temporary Git repository.
    git(tmp_path, "config", "user.email", "test@example.com")  # Configure the temporary Git email.
    git(tmp_path, "config", "user.name", "Test User")  # Configure the temporary Git user name.
    (tmp_path / "tests").mkdir()  # Create the temporary test directory.
    (tmp_path / "service").mkdir()  # Create the temporary service directory.
    (tmp_path / "tests" / "test_checkout.py").write_text("def test_checkout():\n    assert True\n", encoding="utf-8")  # Create the traced test file.
    config = tmp_path / "service" / "config.yaml"  # Define the temporary configuration file.
    config.write_text("inventory:\n  retry:\n    attempts: 2\n", encoding="utf-8")  # Write the original configuration.
    git(tmp_path, "add", ".")  # Stage the first version.
    git(tmp_path, "commit", "-q", "-m", "initial")  # Create the first revision.
    config.write_text("inventory:\n  retry:\n    attempts: 5\n", encoding="utf-8")  # Change the configuration value.
    git(tmp_path, "add", ".")  # Stage the changed version.
    git(tmp_path, "commit", "-q", "-m", "change")  # Create the second revision.
    trace_records = [{  # Create runtime evidence for the test-to-setting relationship.
        "test_id": "test_checkout",  # Identify the test.
        "test_file": "tests/test_checkout.py",  # Identify the test file.
        "dependencies": [{"file": "service/config.yaml", "key": "inventory.retry.attempts"}],  # Record the exact setting used.
    }]
    report = analyze_repository(tmp_path, "tests", trace_records=trace_records)  # Analyze the real Git change.
    assert report["configuration_changes"][0]["changes"]["inventory.retry.attempts"]["new"] == 5  # Verify the changed value.
    assert report["runtime_selected_tests"][0]["test_file"] == "tests/test_checkout.py"  # Verify runtime test selection.
    assert report["selected_tests"][0]["test"] == "tests/test_checkout.py"  # Verify the final selected test.
    assert json.dumps(report)  # Verify that the complete report can be serialized as JSON.
