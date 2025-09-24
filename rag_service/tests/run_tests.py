#!/usr/bin/env python3
"""
Simple test runner for PharmaRAG database ingestion tests.

This script provides an easy way to run the database ingestion tests
with different verbosity levels and options.
"""

import sys
import argparse
import os
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def main():
    """Main function to run the database ingestion tests."""
    parser = argparse.ArgumentParser(
        description="Run PharmaRAG database ingestion tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests with default settings
  python run_tests.py --verbose          # Run with verbose output
  python run_tests.py --quick            # Run only essential tests
  python run_tests.py --check-only       # Only check if database is online
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Run only essential tests (connectivity, document count, basic search)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check if database is online and has documents (minimal testing)'
    )
    
    parser.add_argument(
        '--log-file',
        default='test_database_results.log',
        help='Specify log file name (default: test_database_results.log)'
    )
    
    args = parser.parse_args()
    
    # Import the test module
    try:
        from .test_database_ingestion import DatabaseIngestionTester
    except ImportError as e:
        print(f"Error: Could not import test module: {e}")
        print("Make sure you're running this from the rag_service directory")
        sys.exit(1)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("Warning: .env file not found. Make sure your environment variables are set.")
    
    print("PharmaRAG Database Ingestion Test Runner")
    print("=" * 50)
    
    if args.verbose:
        print("[INFO] Running with verbose output")
    if args.quick:
        print("[QUICK] Running quick tests only")
    if args.check_only:
        print("[CHECK] Running minimal connectivity check only")
    
    print(f"[LOG] Log file: {args.log_file}")
    print()
    
    # Create tester instance
    tester = DatabaseIngestionTester()
    
    try:
        # Run tests based on options
        if args.check_only:
            # Run only essential connectivity tests
            essential_tests = [
                ("Environment Variables", tester.test_environment_variables),
                ("Database Connectivity", tester.test_database_connectivity),
                ("Document Count Check", tester.test_document_count)
            ]
            
            print("Running essential connectivity tests...")
            for test_name, test_func in essential_tests:
                print(f"  [TEST] {test_name}")
                try:
                    result = test_func()
                    print(f"    [PASS] PASSED")
                except Exception as e:
                    print(f"    [FAIL] FAILED: {e}")
                    sys.exit(1)
            
            print("\n[SUCCESS] Database is online and has documents!")
            
        elif args.quick:
            # Run quick test suite
            print("Running quick test suite...")
            results = tester.run_all_tests()
            
            # Check if critical tests passed
            critical_tests = [
                "Environment Variables",
                "Database Connectivity", 
                "Document Count Check",
                "Search Functionality"
            ]
            
            failed_critical = any(
                results[test]['status'] == 'FAIL' 
                for test in critical_tests 
                if test in results
            )
            
            if failed_critical:
                print("\n[FAIL] Critical tests failed!")
                sys.exit(1)
            else:
                print("\n[PASS] All critical tests passed!")
                
        else:
            # Run full test suite
            print("Running full test suite...")
            results = tester.run_all_tests()
            
            # Check overall status
            failed_tests = sum(1 for result in results.values() if result['status'] == 'FAIL')
            if failed_tests > 0:
                print(f"\n[FAIL] {failed_tests} tests failed!")
                sys.exit(1)
            else:
                print("\n[SUCCESS] All tests passed!")
        
    except KeyboardInterrupt:
        print("\n[STOP] Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
