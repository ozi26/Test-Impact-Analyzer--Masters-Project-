# ============================================================================== 
# Simple language-independent lexical test scoring.
# ============================================================================== 

from pathlib import Path  # Import Path for stable test-file paths.
from .text_utils import extract_words, read_text_file  # Import shared text helpers.

# ------------------------------------------------------------------------------
# Calculate one test's lexical relevance score.
# ------------------------------------------------------------------------------
def calculate_score(changed_terms, test_file):
    """Return the fraction of changed terms found in one test."""
    terms = set(changed_terms)  # Copy the changed terms into a set.
    if not terms:  # Check whether there are no terms to compare.
        return 0.0  # Return zero when the change contains no searchable terms.
    test_terms = extract_words(read_text_file(test_file))  # Extract searchable words from the test file.
    common_terms = terms & test_terms  # Find terms shared by the change and the test.
    return len(common_terms) / len(terms)  # Return the simple relevance ratio.

# ------------------------------------------------------------------------------
# Rank candidate tests by lexical relevance.
# ------------------------------------------------------------------------------
def prioritize_tests(changed_terms, test_files, minimum_score=0.0):
    """Return candidate tests ordered from highest to lowest relevance."""
    results = []  # Create the ranking result list.
    for test_file in test_files:  # Score every candidate test.
        score = calculate_score(changed_terms, test_file)  # Calculate the test's lexical score.
        if score >= minimum_score:  # Keep tests meeting the configured threshold.
            results.append({  # Store the test and its score.
                "test": Path(test_file).as_posix(),  # Store the test path in a stable format.
                "score": round(score, 3),  # Store a readable score.
            })
    return sorted(results, key=lambda item: (-item["score"], item["test"]))  # Sort by score and then path.
