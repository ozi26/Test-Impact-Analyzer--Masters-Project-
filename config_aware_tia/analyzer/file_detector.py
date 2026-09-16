# ============================================================================== 
# Helpers for deciding whether a file is source code or configuration.
# ============================================================================== 

from pathlib import Path  # Import Path so file extensions can be inspected.
from .constants import CONFIG_EXTENSIONS, SOURCE_EXTENSIONS  # Import supported extensions.

# ------------------------------------------------------------------------------
# Check whether a path is a configuration file.
# ------------------------------------------------------------------------------
def is_config_file(file_path):
    """Return True when the file has a supported configuration extension."""
    return Path(file_path).suffix.lower() in CONFIG_EXTENSIONS  # Compare the normalized extension.

# ------------------------------------------------------------------------------
# Check whether a path is source code.
# ------------------------------------------------------------------------------
def is_source_file(file_path):
    """Return True when the file has a supported source-code extension."""
    return Path(file_path).suffix.lower() in SOURCE_EXTENSIONS  # Compare the normalized extension.
