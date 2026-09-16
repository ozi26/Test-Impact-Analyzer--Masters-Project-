# ============================================================================== 
# Git helpers used to detect source-code and configuration-file changes.
# ============================================================================== 

import subprocess  # Import subprocess so Python can run Git commands.
from pathlib import Path  # Import Path for safe repository path handling.
from .text_utils import normalize_relative_path  # Import path normalization.

# ------------------------------------------------------------------------------
# Run one Git command inside the selected repository.
# ------------------------------------------------------------------------------
def run_git(repo_path, *arguments):
    """Run Git and return its standard output."""
    command = ["git", "-C", str(repo_path), *arguments]  # Build the complete Git command.
    result = subprocess.run(command, capture_output=True, text=True, check=True)  # Execute Git and stop on command errors.
    return result.stdout  # Return the command output to the caller.

# ------------------------------------------------------------------------------
# Check whether a Git revision can be resolved.
# ------------------------------------------------------------------------------
def revision_exists(repo_path, revision):
    """Return True when Git can resolve the supplied revision."""
    try:  # Try to resolve the revision.
        run_git(repo_path, "rev-parse", "--verify", revision)  # Ask Git to verify the revision.
        return True  # Report that the revision exists.
    except subprocess.CalledProcessError:  # Handle a missing or invalid revision.
        return False  # Report that the revision does not exist.

# ------------------------------------------------------------------------------
# Get all files changed between two Git revisions.
# ------------------------------------------------------------------------------
def get_changed_files(repo_path, base_ref="HEAD~1", target_ref="HEAD"):
    """Return repository-relative paths changed between two revisions."""
    output = run_git(repo_path, "diff", "--name-only", base_ref, target_ref, "--")  # Ask Git for changed file names.
    return [normalize_relative_path(line.strip()) for line in output.splitlines() if line.strip()]  # Normalize each path.

# ------------------------------------------------------------------------------
# Read one file from a specific Git revision.
# ------------------------------------------------------------------------------
def get_file_at_revision(repo_path, revision, file_path):
    """Return one file's content from a Git revision."""
    relative_path = normalize_relative_path(file_path)  # Normalize the repository-relative path.
    return run_git(repo_path, "show", f"{revision}:{relative_path}")  # Ask Git for the stored file content.

# ------------------------------------------------------------------------------
# Extract added and removed lines from a source-code diff.
# ------------------------------------------------------------------------------
def get_source_change_lines(repo_path, base_ref, target_ref, file_path):
    """Return added and removed source lines from a Git diff."""
    relative_path = normalize_relative_path(file_path)  # Normalize the file path before calling Git.
    output = run_git(repo_path, "diff", "--unified=0", base_ref, target_ref, "--", relative_path)  # Get a zero-context diff.
    changed_lines = []  # Create a list for added and removed source lines.
    for line in output.splitlines():  # Visit every line in the Git patch.
        if line.startswith(("+++", "---", "@@")):  # Skip diff headers and hunk headers.
            continue  # Move to the next line.
        if line.startswith("+") or line.startswith("-"):  # Keep added and removed content lines.
            changed_lines.append(line[1:])  # Remove the leading Git diff marker.
    return changed_lines  # Return the changed source lines.

# ------------------------------------------------------------------------------
# Keep the old function name as a compatibility wrapper.
# ------------------------------------------------------------------------------
def get_source_change_terms(repo_path, base_ref, target_ref, file_path):
    """Return changed source lines for older callers of this helper."""
    return get_source_change_lines(repo_path, base_ref, target_ref, file_path)  # Reuse the corrected diff function.

# ------------------------------------------------------------------------------
# Read the current working-tree version of a file.
# ------------------------------------------------------------------------------
def read_current_file(repo_path, file_path):
    """Return current file text or an empty string when the file is absent."""
    path = Path(repo_path) / normalize_relative_path(file_path)  # Build the current file path.
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""  # Read the file when it exists.
