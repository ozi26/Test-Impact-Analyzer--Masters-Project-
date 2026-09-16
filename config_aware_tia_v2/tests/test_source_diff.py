# ============================================================================== 
# Unit tests for Git source-code change extraction.
# ============================================================================== 

import subprocess  # Import subprocess for creating the temporary Git repository.
from analyzer.git_changes import get_source_change_lines  # Import the Git diff helper.

# ------------------------------------------------------------------------------
# Test that added and removed source lines are extracted.
# ------------------------------------------------------------------------------
def test_source_change_extraction(tmp_path):
    """Check that Git returns both removed and added source lines."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)  # Initialize a temporary Git repository.
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)  # Configure a test email.
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)  # Configure a test name.
    source_file = tmp_path / "app.py"  # Define the temporary source file.
    source_file.write_text("def retry_request():\n    return 1\n", encoding="utf-8")  # Write the first source version.
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)  # Stage the first source version.
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=tmp_path, check=True)  # Create the first commit.
    source_file.write_text("def retry_request():\n    return 2\n", encoding="utf-8")  # Write the changed source version.
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)  # Stage the changed source version.
    subprocess.run(["git", "commit", "-q", "-m", "change"], cwd=tmp_path, check=True)  # Create the second commit.
    lines = get_source_change_lines(tmp_path, "HEAD~1", "HEAD", "app.py")  # Extract changed source lines.
    assert any("return 1" in line for line in lines)  # Verify the removed line is present.
    assert any("return 2" in line for line in lines)  # Verify the added line is present.
