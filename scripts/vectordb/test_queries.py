#!/usr/bin/env python3
"""Validation tests for the vector database."""

import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from query import query_database


# Test cases: (query, expected_file, keywords that should appear)
TEST_CASES = [
    (
        "rc.S initialization PID 1 boot sequence phase",
        "BOOT_FLOW.md",
        ["init", "rc.S", "PID"]
    ),
    (
        "What is the first-run script?",
        "SCRIPTS_REFERENCE.md",
        ["first-run", "welcome", "wizard"]
    ),
    (
        "What are the ARM64 differences?",
        "X86_ARM64_DIFF.md",
        ["ARM64", "x86"]
    ),
    (
        "How do I debug network issues?",
        "TROUBLESHOOTING.md",
        ["network", "eth0", "end0"]
    ),
    (
        "lcon configuration file format /tmp/config persistence",
        "CONFIG_SYSTEM.md",
        ["/tmp/config", "lcon"]
    ),
]


def run_tests(verbose: bool = False) -> tuple:
    """
    Run all validation tests.

    Returns:
        Tuple of (passed_count, failed_count, results_list)
    """
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("Vector Database Validation Tests")
    print("=" * 60)

    for i, (query, expected_file, keywords) in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}/{len(TEST_CASES)}: {query[:50]}...")

        try:
            # Get top 3 results
            results_list = query_database(query, top_k=3, verbose=False)

            if not results_list:
                print(f"  FAIL: No results returned")
                failed += 1
                results.append({
                    "query": query,
                    "expected": expected_file,
                    "actual": None,
                    "passed": False,
                    "reason": "No results returned"
                })
                continue

            # Check if expected file is in top 3
            top_files = [r["source_file"] for r in results_list]
            found = expected_file in top_files

            if found:
                rank = top_files.index(expected_file) + 1
                print(f"  PASS: Found '{expected_file}' at rank {rank}")
                passed += 1
                results.append({
                    "query": query,
                    "expected": expected_file,
                    "actual": top_files,
                    "rank": rank,
                    "passed": True
                })
            else:
                print(f"  FAIL: Expected '{expected_file}' in top 3")
                print(f"        Got: {top_files}")
                failed += 1
                results.append({
                    "query": query,
                    "expected": expected_file,
                    "actual": top_files,
                    "passed": False,
                    "reason": f"Expected file not in top 3"
                })

            if verbose:
                print(f"  Top results:")
                for r in results_list:
                    print(f"    - {r['source_file']} (score: {r['score']:.4f})")

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            results.append({
                "query": query,
                "expected": expected_file,
                "actual": None,
                "passed": False,
                "reason": str(e)
            })

    return passed, failed, results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run validation tests for the vector database"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    passed, failed, results = run_tests(verbose=args.verbose)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{len(TEST_CASES)}")
    print(f"Failed: {failed}/{len(TEST_CASES)}")

    if args.json:
        import json
        print("\nJSON Results:")
        print(json.dumps(results, indent=2))

    # Exit with error code if any tests failed
    if failed > 0:
        print(f"\n{failed} test(s) FAILED")
        sys.exit(1)
    else:
        print("\nAll tests PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
