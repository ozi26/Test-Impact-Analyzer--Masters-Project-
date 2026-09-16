"""Tests for the analyzer components."""  # Explain this test module.

from analyzer.config_parser import find_configuration_changes, parse_configuration  # Import config functions.
from analyzer.lexical_selector import calculate_score  # Import lexical scoring.

def test_yaml_parser(tmp_path):  # Test YAML parsing.
    """Check that nested YAML becomes dotted keys."""  # Explain the test.
    file_path = tmp_path / "config.yaml"  # Create a temporary YAML path.
    file_path.write_text("inventory:\n  retry:\n    attempts: 5\n", encoding="utf-8")  # Write sample YAML.
    result = parse_configuration(file_path)  # Parse the sample YAML.
    assert result["inventory.retry.attempts"] == 5  # Check the flattened key.

def test_configuration_change_detection(tmp_path):  # Test exact configuration change detection.
    """Check that a changed value is detected."""  # Explain the test.
    old_file = tmp_path / "old.yaml"  # Create the old file path.
    new_file = tmp_path / "new.yaml"  # Create the new file path.
    old_file.write_text("retry:\n  attempts: 2\n", encoding="utf-8")  # Write the old value.
    new_file.write_text("retry:\n  attempts: 5\n", encoding="utf-8")  # Write the new value.
    changes = find_configuration_changes(old_file, new_file)  # Compare the files.
    assert changes["retry.attempts"]["old"] == 2  # Check the old value.
    assert changes["retry.attempts"]["new"] == 5  # Check the new value.

def test_lexical_score(tmp_path):  # Test lexical relevance scoring.
    """Check that matching terms produce a positive score."""  # Explain the test.
    test_file = tmp_path / "test_example.py"  # Create a temporary test file.
    test_file.write_text("def test_retry():\n    pass\n", encoding="utf-8")  # Write a test containing retry.
    assert calculate_score({"retry", "attempts"}, test_file) == 0.5  # Verify one of two terms matched.
