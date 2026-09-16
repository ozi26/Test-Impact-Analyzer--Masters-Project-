# ============================================================================== 
# Text and path helper functions used by the analyzer.
# ============================================================================== 

import re  # Import regular expressions for simple word extraction.
from pathlib import Path  # Import Path for safe file and path handling.

# ------------------------------------------------------------------------------
# Read a text file.
# ------------------------------------------------------------------------------
def read_text_file(file_path):
    """Read a UTF-8 text file and return its contents."""
    path = Path(file_path)  # Convert the supplied path into a Path object.
    return path.read_text(encoding="utf-8", errors="replace")  # Read the file safely.

# ------------------------------------------------------------------------------
# Extract searchable words from source or configuration text.
# ------------------------------------------------------------------------------
def extract_words(text):
    """Return normalized identifiers and configuration-like words."""
    words = re.findall(r"[A-Za-z_][A-Za-z0-9_.-]*", text)  # Find identifiers and dotted configuration words.
    expanded = set()  # Create a set for complete identifiers and their useful parts.
    for word in words:  # Visit every extracted identifier.
        normalized = word.lower()  # Normalize the identifier.
        expanded.add(normalized)  # Keep the complete identifier.
        expanded.update(part for part in re.split(r"[_.-]+", normalized) if part)  # Also keep individual identifier parts.
    return expanded  # Return complete identifiers and searchable parts.

# ------------------------------------------------------------------------------
# Convert a path to a stable report representation.
# ------------------------------------------------------------------------------
def path_to_string(file_path):
    """Return a path using forward slashes."""
    return Path(file_path).as_posix()  # Use one path format on every operating system.

# ------------------------------------------------------------------------------
# Normalize a repository-relative path.
# ------------------------------------------------------------------------------
def normalize_relative_path(file_path):
    """Normalize path separators and remove a leading './'."""
    value = path_to_string(file_path).replace("\\", "/")  # Normalize Windows path separators.
    return value[2:] if value.startswith("./") else value  # Remove an unnecessary relative-path prefix.
