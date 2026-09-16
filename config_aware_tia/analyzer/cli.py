"""Command-line interface for the Test Impact Analyzer."""  # Explain this module.

import argparse  # Import command-line argument support.
import json  # Import JSON report writing.
from pathlib import Path  # Import Path for output files.
from .analyzer import analyze_repository  # Import the main analyzer.

def build_parser():  # Create the command-line parser.
    """Create and return the CLI argument parser."""  # Explain the function.
    parser = argparse.ArgumentParser(description="Configuration-aware Test Impact Analyzer.")  # Create the parser.
    parser.add_argument("--repo", default=".", help="Git repository to analyze.")  # Add repository argument.
    parser.add_argument("--tests", default="tests", help="Directory containing test files.")  # Add test directory argument.
    parser.add_argument("--base", default="HEAD~1", help="Old Git revision.")  # Add old revision argument.
    parser.add_argument("--target", default="HEAD", help="New Git revision.")  # Add new revision argument.
    parser.add_argument("--trace-map", default="", help="Optional JSON file created from runtime tracing.")  # Add trace map argument.
    parser.add_argument("--output", default="tia-report.json", help="Output JSON report.")  # Add report path argument.
    parser.add_argument("--minimum-score", type=float, default=0.0, help="Minimum lexical score.")  # Add lexical threshold.
    return parser  # Return the configured parser.

def main():  # Run the command-line analyzer.
    """Parse arguments, analyze the repository, and write a report."""  # Explain the function.
    args = build_parser().parse_args()  # Read command-line arguments.
    trace_records = []  # Start with no runtime trace records.
    if args.trace_map:  # Check whether a trace map was supplied.
        trace_records = json.loads(Path(args.trace_map).read_text(encoding="utf-8"))  # Load the trace map.
    report = analyze_repository(args.repo, args.tests, args.base, args.target, trace_records, args.minimum_score)  # Run the analysis.
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")  # Save the report.
    print(json.dumps(report, indent=2))  # Also show the report on the terminal.

if __name__ == "__main__":  # Check whether this file was run directly.
    main()  # Start the CLI.
