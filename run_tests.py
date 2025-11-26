#!/usr/bin/env python3
"""
Test runner for chklst application.

Runs comprehensive test suite with coverage reporting.
Usage:
    pipenv run python run_tests.py              # Run all tests with coverage
    pipenv run python run_tests.py --no-cov     # Run tests without coverage
    pipenv run python run_tests.py --verbose    # Run with verbose output
    pipenv run python run_tests.py -k test_name # Run specific test
"""

import subprocess
import sys
import argparse
from pathlib import Path


def main():
    """Run the test suite with optional coverage reporting."""
    parser = argparse.ArgumentParser(
        description='chklst Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pipenv run python run_tests.py                      # All tests with coverage
  pipenv run python run_tests.py --no-cov             # All tests without coverage
  pipenv run python run_tests.py -v                   # Verbose output
  pipenv run python run_tests.py -k test_health       # Specific test
  pipenv run python run_tests.py tests/test_models.py # Specific file
        """
    )

    parser.add_argument(
        '--no-cov',
        action='store_true',
        help='Run tests without coverage reporting'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '-k',
        type=str,
        help='Run tests matching pattern (e.g., test_health)'
    )

    parser.add_argument(
        '--tb',
        type=str,
        default='short',
        choices=['short', 'long', 'native', 'no'],
        help='Traceback print mode (default: short)'
    )

    parser.add_argument(
        'tests',
        nargs='*',
        help='Specific test files or directories to run'
    )

    args = parser.parse_args()

    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest']

    # Add coverage if requested (default)
    if not args.no_cov:
        cmd.extend([
            '--cov=backend',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-report=term',
        ])

    # Add verbosity
    if args.verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')

    # Add traceback mode
    cmd.extend(['--tb', args.tb])

    # Add test path pattern
    if args.k:
        cmd.extend(['-k', args.k])

    # Add specific tests if provided
    if args.tests:
        cmd.extend(args.tests)
    else:
        cmd.append('tests/')

    # Add additional options for better output
    cmd.extend([
        '--strict-markers',
        '--disable-warnings',
        '-ra',  # Show all test summary
    ])

    print("=" * 70)
    print("chklst Test Suite")
    print("=" * 70)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 70)
    print()

    # Run pytest
    result = subprocess.run(cmd)

    # Print summary
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("Test Suite PASSED")
    else:
        print("Test Suite FAILED")
    print("=" * 70)

    if not args.no_cov:
        print("\nCoverage report generated in: htmlcov/index.html")
        print("Open it in a browser to view detailed coverage information.")

    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
