# ============================================================================== 
# Main Configuration-Aware Test Impact Analyzer engine.
# ============================================================================== 

from pathlib import Path  # Import Path for repository and test paths.
from .config_parser import configuration_terms, find_configuration_changes_from_text  # Import configuration comparison helpers.
from .config_selection import ConfigurationAwareSelector  # Import exact runtime configuration selection.
from .file_detector import is_config_file, is_source_file  # Import file-type detection helpers.
from .git_changes import get_changed_files, get_file_at_revision, get_source_change_lines  # Import Git change helpers.
from .lexical_selector import prioritize_tests  # Import lexical test ranking.
from .text_utils import extract_words, normalize_relative_path  # Import common text and path helpers.

# ------------------------------------------------------------------------------
# Find all Python tests inside a test directory.
# ------------------------------------------------------------------------------
def get_all_test_files(tests_root):
    """Return Python test files recursively."""
    root = Path(tests_root)  # Convert the supplied test directory into a Path object.
    if not root.exists():  # Check whether the directory exists.
        return []  # Return an empty list when there are no tests.
    return sorted(root.rglob("test_*.py"))  # Find files using the normal pytest naming pattern.

# ------------------------------------------------------------------------------
# Safely read one Git revision of a file.
# ------------------------------------------------------------------------------
def _revision_file_text(repo_path, revision, relative_file):
    """Return file text from Git or an empty string when the file is absent."""
    try:  # Try to read the file from the requested revision.
        return get_file_at_revision(repo_path, revision, relative_file)  # Return the stored file content.
    except Exception:  # Handle files that were added or deleted.
        return ""  # Treat a missing revision copy as an empty file.

# ------------------------------------------------------------------------------
# Analyze one Git change and produce a JSON-friendly report.
# ------------------------------------------------------------------------------
def analyze_repository(repo_path, tests_root, base_ref="HEAD~1", target_ref="HEAD", trace_records=None, minimum_score=0.0):
    """Detect source/configuration changes and select impacted tests."""
    repo = Path(repo_path).resolve()  # Normalize the repository path.
    changed_files = get_changed_files(repo, base_ref, target_ref)  # Ask Git for all changed files.
    changed_terms = set()  # Create the combined lexical change-term set.
    source_changes = []  # Create detailed source-change results.
    configuration_changes = []  # Create detailed configuration-change results.

    # --------------------------------------------------------------------------
    # Process each changed repository file.
    # --------------------------------------------------------------------------
    for relative_file in changed_files:  # Visit every changed file.
        relative_path = normalize_relative_path(relative_file)  # Normalize the repository-relative path.
        full_path = repo / relative_path  # Build the current working-tree path.

        if is_source_file(full_path):  # Check whether the changed file is source code.
            changed_lines = get_source_change_lines(repo, base_ref, target_ref, relative_path)  # Get added and removed source lines.
            source_terms = extract_words("\n".join(changed_lines))  # Extract searchable terms from the exact diff.
            changed_terms.update(source_terms)  # Add source terms to the global term set.
            source_changes.append({  # Save the source change details.
                "file": relative_path,  # Store the changed source file.
                "changed_lines": changed_lines,  # Store the exact added and removed lines.
                "terms": sorted(source_terms),  # Store searchable terms from the diff.
            })
            continue  # Move to the next changed file.

        if is_config_file(full_path):  # Check whether the changed file is configuration.
            old_text = _revision_file_text(repo, base_ref, relative_path)  # Read the old configuration version.
            new_text = _revision_file_text(repo, target_ref, relative_path)  # Read the new configuration version.
            extension = Path(relative_path).suffix  # Read the configuration extension.
            try:  # Try to parse and compare both configurations.
                changes = find_configuration_changes_from_text(old_text, new_text, extension)  # Detect exact key-level changes.
            except Exception as error:  # Handle malformed configuration without hiding the problem.
                changes = {  # Store a clear parser error in the report.
                    "__parse_error__": {"type": "parse_error", "old": None, "new": str(error)}  # Save the parser error details.
                }
            configuration_changes.append({  # Save the configuration change details.
                "file": relative_path,  # Store the changed configuration file.
                "changes": changes,  # Store added, removed, and modified keys.
            })
            changed_terms.update(configuration_terms(changes))  # Add configuration terms to lexical analysis.

    test_files = get_all_test_files(repo / tests_root)  # Find all candidate Python tests.
    lexical_results = prioritize_tests(changed_terms, test_files, minimum_score)  # Rank tests by lexical relevance.
    for result in lexical_results:  # Visit every lexical test result.
        test_path = Path(result["test"]).resolve()  # Convert the reported test path into an absolute path temporarily.
        try:  # Try to convert the path into a repository-relative path.
            result["test"] = normalize_relative_path(test_path.relative_to(repo))  # Store a stable relative test path.
        except ValueError:  # Handle a test path that is outside the repository.
            result["test"] = normalize_relative_path(result["test"])  # Keep the original normalized path.

    runtime_selector = ConfigurationAwareSelector()  # Create the runtime configuration selector.
    runtime_selector.load_records(trace_records or [])  # Load the saved runtime dependency map.

    changed_settings = []  # Create the exact changed configuration file/key list.
    for item in configuration_changes:  # Visit every changed configuration file.
        for key, details in item["changes"].items():  # Visit every changed configuration key.
            if key == "__parse_error__":  # Skip parser-error pseudo-keys.
                continue  # Do not treat an error as a real setting.
            changed_settings.append({  # Add one changed file/key pair.
                "file": item["file"],  # Store the configuration file.
                "key": key,  # Store the exact configuration key.
                "type": details["type"],  # Store the change type.
            })

    runtime_results = runtime_selector.select_tests(changed_settings)  # Select tests that accessed changed configuration keys.
    selected_by_path = {}  # Create an ordered mapping for the final selected tests.

    for item in lexical_results:  # Visit lexical test rankings.
        if item["score"] > 0:  # Keep tests that share at least one changed term.
            selected_by_path[item["test"]] = {  # Store the lexical selection.
                "test": item["test"],  # Store the test path.
                "score": item["score"],  # Store the lexical relevance score.
                "selection_reason": "lexical_match",  # Explain why the test was selected.
            }

    for item in runtime_results:  # Visit exact runtime selections.
        test_file = item.get("test_file", "")  # Read the selected test path.
        if not test_file:  # Ignore incomplete trace records.
            continue  # Move to the next runtime result.
        if test_file not in selected_by_path:  # Add tests not already selected lexically.
            selected_by_path[test_file] = {  # Store the runtime selection.
                "test": test_file,  # Store the test path.
                "score": 1.0,  # Give an exact runtime match a full score.
                "selection_reason": "runtime_configuration_trace",  # Explain the runtime selection.
                "settings": item["settings"],  # Store the exact changed settings.
            }
        else:  # Handle a test selected by both methods.
            selected_by_path[test_file]["selection_reason"] = "lexical_match_and_runtime_trace"  # Explain both selection paths.
            selected_by_path[test_file]["settings"] = item["settings"]  # Store the exact runtime settings.

    return {  # Return the complete analyzer report.
        "base_revision": base_ref,  # Include the old Git revision.
        "target_revision": target_ref,  # Include the new Git revision.
        "changed_files": changed_files,  # Include every changed file.
        "source_changes": source_changes,  # Include source-code change details.
        "configuration_changes": configuration_changes,  # Include exact configuration changes.
        "changed_terms": sorted(changed_terms),  # Include all searchable change terms.
        "lexical_test_results": lexical_results,  # Include lexical rankings.
        "runtime_selected_tests": runtime_results,  # Include exact runtime selections.
        "selected_tests": list(selected_by_path.values()),  # Include the final merged test subset.
    }
