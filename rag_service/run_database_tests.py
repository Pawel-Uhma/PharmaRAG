#!/usr/bin/env python3
"""
Main test runner for PharmaRAG database ingestion tests.

This script should be run from the rag_service directory and will
execute the database ingestion tests from the tests/ subdirectory.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import from tests
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the test runner
if __name__ == "__main__":
    try:
        from tests.run_tests import main
        main()
    except ImportError as e:
        print(f"Error importing test runner: {e}")
        print("Make sure you're running this from the rag_service directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
