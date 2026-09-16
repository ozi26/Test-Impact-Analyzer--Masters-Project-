# ============================================================================== 
# Runtime configuration-aware test selection.
# ============================================================================== 

from .text_utils import normalize_relative_path  # Import path normalization for stable comparisons.

# ------------------------------------------------------------------------------
# Select tests using exact runtime configuration dependencies.
# ------------------------------------------------------------------------------
class ConfigurationAwareSelector:
    """Select tests whose traced configuration keys were changed."""

    # --------------------------------------------------------------------------
    # Create an empty runtime dependency selector.
    # --------------------------------------------------------------------------
    def __init__(self):
        self.test_dependencies = {}  # Store each test ID and its file-key dependencies.
        self.test_files = {}  # Store each test ID and its physical test file.

    # --------------------------------------------------------------------------
    # Load the saved runtime dependency records.
    # --------------------------------------------------------------------------
    def load_records(self, records):
        """Build an in-memory test-to-configuration dependency map."""
        for record in records or []:  # Visit every runtime trace record.
            test_id = str(record.get("test_id", ""))  # Read the test identifier.
            if not test_id:  # Ignore records that do not identify a test.
                continue  # Move to the next record.
            self.test_dependencies.setdefault(test_id, set())  # Create the dependency set when needed.
            test_file = record.get("test_file")  # Read the physical test file when it is available.
            if test_file:  # Store the test file when the trace contains it.
                self.test_files[test_id] = normalize_relative_path(test_file)  # Normalize the test path.
            for dependency in record.get("dependencies", []):  # Visit every configuration access.
                file_name = normalize_relative_path(dependency.get("file", ""))  # Normalize the configuration file path.
                key = str(dependency.get("key", ""))  # Read the exact configuration key.
                if file_name and key:  # Keep only complete file-key pairs.
                    self.test_dependencies[test_id].add((file_name, key))  # Save the exact runtime dependency.

    # --------------------------------------------------------------------------
    # Register a test file when trace data does not contain its path.
    # --------------------------------------------------------------------------
    def register_test_file(self, test_id, test_file):
        """Associate a test identifier with a test file."""
        self.test_files[str(test_id)] = normalize_relative_path(test_file)  # Store the normalized test path.

    # --------------------------------------------------------------------------
    # Select tests affected by changed configuration settings.
    # --------------------------------------------------------------------------
    def select_tests(self, changed_settings):
        """Return tests whose traced settings intersect the changed settings."""
        changed = {  # Build normalized file-key pairs for changed settings.
            (normalize_relative_path(item["file"]), str(item["key"]))
            for item in changed_settings
        }
        selected = []  # Create the runtime selection list.
        for test_id, dependencies in self.test_dependencies.items():  # Check every traced test.
            affected = sorted(changed.intersection(dependencies))  # Find exact settings shared by test and change.
            if affected:  # Select the test when at least one setting matches.
                selected.append({  # Save the test and the exact settings that caused selection.
                    "test_id": test_id,  # Store the test identifier.
                    "test_file": self.test_files.get(test_id),  # Store the test file.
                    "settings": [  # Convert matching tuples into JSON-friendly objects.
                        {"file": file_name, "key": key} for file_name, key in affected  # Store each matching file-key pair.
                    ],
                })
        return selected  # Return the exact runtime-based test selections.
