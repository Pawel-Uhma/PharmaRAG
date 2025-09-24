"""
PharmaRAG Test Suite

This package contains comprehensive tests for the PharmaRAG system,
including database connectivity, document ingestion, and search functionality tests.
"""

__version__ = "1.0.0"
__author__ = "PharmaRAG Team"

# Import main test classes for easy access
from .test_database_ingestion import DatabaseIngestionTester

__all__ = [
    "DatabaseIngestionTester",
]
