#!/usr/bin/env python3
"""
Database Ingestion Test Script for PharmaRAG

This script tests if the PostgreSQL database with pgvector extension is online
and properly ingested with pharmaceutical documents. It performs comprehensive
checks including connectivity, document counts, vector embeddings, and search functionality.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Database and vector store imports
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

# Configure logging with proper encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tests/test_database_results.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from parent directory
load_dotenv('../.env')

# Configuration
POSTGRES_CONNECTION_STRING = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('DB_NAME', 'pharmarag')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
API_KEY = os.getenv('API_KEY')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'pharma_documents')
DATA_PATH = os.getenv('DATA_PATH', 'data')

class DatabaseIngestionTester:
    """Comprehensive test suite for database connectivity and document ingestion."""
    
    def __init__(self):
        self.test_results = {}
        self.connection = None
        self.engine = None
        self.vector_store = None
        self.embeddings = None
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all database and ingestion tests."""
        logger.info("=" * 80)
        logger.info("STARTING PHARMARAG DATABASE INGESTION TESTS")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Test sequence
        tests = [
            ("Environment Variables", self.test_environment_variables),
            ("Database Connectivity", self.test_database_connectivity),
            ("PostgreSQL Extensions", self.test_postgresql_extensions),
            ("Vector Store Initialization", self.test_vector_store_initialization),
            ("Document Count Check", self.test_document_count),
            ("Vector Embeddings Test", self.test_vector_embeddings),
            ("Search Functionality", self.test_search_functionality),
            ("Sample Document Retrieval", self.test_sample_document_retrieval),
            ("Data Directory Check", self.test_data_directory),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*20} {test_name.upper()} {'='*20}")
            try:
                result = test_func()
                self.test_results[test_name] = {
                    'status': 'PASS',
                    'result': result,
                    'error': None
                }
                logger.info(f"[PASS] {test_name}: PASSED")
            except Exception as e:
                self.test_results[test_name] = {
                    'status': 'FAIL',
                    'result': None,
                    'error': str(e)
                }
                logger.error(f"[FAIL] {test_name}: FAILED - {str(e)}")
        
        # Generate summary
        total_time = time.time() - start_time
        self._generate_summary(total_time)
        
        return self.test_results
    
    def test_environment_variables(self) -> Dict[str, Any]:
        """Test if all required environment variables are present."""
        required_vars = {
            'DATABASE_URL': POSTGRES_CONNECTION_STRING,
            'API_KEY': API_KEY,
            'DB_HOST': DB_HOST,
            'DB_USER': DB_USER,
            'DB_PASSWORD': DB_PASSWORD
        }
        
        missing_vars = []
        present_vars = {}
        
        for var_name, var_value in required_vars.items():
            if var_value:
                present_vars[var_name] = f"{var_value[:10]}..." if len(str(var_value)) > 10 else "Present"
            else:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return {
            'present_variables': present_vars,
            'missing_variables': missing_vars,
            'total_required': len(required_vars),
            'total_present': len(present_vars)
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test basic PostgreSQL database connectivity."""
        try:
            # Test basic connection
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = self.connection.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Test database size
            cursor.execute(f"""
                SELECT pg_size_pretty(pg_database_size('{DB_NAME}')) as size;
            """)
            db_size = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'connection_status': 'Connected',
                'postgresql_version': version,
                'database_size': db_size,
                'database_name': DB_NAME
            }
            
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def test_postgresql_extensions(self) -> Dict[str, Any]:
        """Test if required PostgreSQL extensions are installed."""
        if not self.connection:
            raise Exception("No database connection available")
        
        cursor = self.connection.cursor()
        
        # Check for pgvector extension
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        
        # Check for other useful extensions
        cursor.execute("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm');")
        other_exts = cursor.fetchall()
        
        cursor.close()
        
        extensions_status = {
            'vector': bool(vector_ext),
            'uuid_ossp': any(ext[0] == 'uuid-ossp' for ext in other_exts),
            'pg_trgm': any(ext[0] == 'pg_trgm' for ext in other_exts)
        }
        
        if not extensions_status['vector']:
            raise Exception("pgvector extension not installed")
        
        return {
            'extensions': extensions_status,
            'vector_version': vector_ext[0] if vector_ext else None
        }
    
    def test_vector_store_initialization(self) -> Dict[str, Any]:
        """Test if the vector store can be initialized properly."""
        try:
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(api_key=API_KEY)
            
            # Create database engine
            self.engine = create_engine(POSTGRES_CONNECTION_STRING)
            
            # Initialize vector store
            self.vector_store = PGVector(
                embeddings=self.embeddings,
                connection=POSTGRES_CONNECTION_STRING,
                collection_name=COLLECTION_NAME,
            )
            
            return {
                'embeddings_initialized': True,
                'engine_initialized': True,
                'vector_store_initialized': True,
                'collection_name': COLLECTION_NAME,
                'embedding_model': 'text-embedding-ada-002'  # Default OpenAI model
            }
            
        except Exception as e:
            raise Exception(f"Vector store initialization failed: {str(e)}")
    
    def test_document_count(self) -> Dict[str, Any]:
        """Test if documents are present in the vector store."""
        if not self.vector_store:
            raise Exception("Vector store not initialized")
        
        try:
            # Get document count using SQL query
            with self.engine.connect() as conn:
                # Query the langchain_pg_collection and langchain_pg_embedding tables
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as doc_count 
                    FROM langchain_pg_embedding 
                    WHERE collection_id IN (
                        SELECT uuid FROM langchain_pg_collection 
                        WHERE name = '{COLLECTION_NAME}'
                    );
                """))
                doc_count = result.fetchone()[0]
                
                # Also check collection info
                result = conn.execute(text(f"""
                    SELECT uuid, name, cmetadata 
                    FROM langchain_pg_collection 
                    WHERE name = '{COLLECTION_NAME}';
                """))
                collection_info = result.fetchone()
                
                if not collection_info:
                    raise Exception(f"Collection '{COLLECTION_NAME}' not found")
                
                return {
                    'document_count': doc_count,
                    'collection_name': collection_info[1],
                    'collection_id': str(collection_info[0]),
                    'collection_metadata': collection_info[2],
                    'has_documents': doc_count > 0
                }
                
        except Exception as e:
            raise Exception(f"Document count check failed: {str(e)}")
    
    def test_vector_embeddings(self) -> Dict[str, Any]:
        """Test if vector embeddings are working properly."""
        if not self.embeddings or not self.vector_store:
            raise Exception("Embeddings or vector store not initialized")
        
        try:
            # Test embedding generation
            test_text = "Test pharmaceutical document content"
            embedding = self.embeddings.embed_query(test_text)
            
            # Test similarity search with the test embedding
            results = self.vector_store.similarity_search(test_text, k=1)
            
            return {
                'embedding_generated': True,
                'embedding_dimension': len(embedding),
                'test_query': test_text,
                'similarity_search_works': len(results) >= 0,
                'search_results_count': len(results)
            }
            
        except Exception as e:
            raise Exception(f"Vector embeddings test failed: {str(e)}")
    
    def test_search_functionality(self) -> Dict[str, Any]:
        """Test various search functionalities."""
        if not self.vector_store:
            raise Exception("Vector store not initialized")
        
        test_queries = [
            "leki przeciwbólowe",
            "antybiotyki",
            "dawkowanie",
            "skutki uboczne",
            "interakcje lekowe"
        ]
        
        search_results = {}
        
        for query in test_queries:
            try:
                # Test similarity search
                results = self.vector_store.similarity_search(query, k=3)
                
                # Test similarity search with scores
                scored_results = self.vector_store.similarity_search_with_relevance_scores(query, k=3)
                
                search_results[query] = {
                    'basic_search_results': len(results),
                    'scored_search_results': len(scored_results),
                    'best_score': scored_results[0][1] if scored_results else 0,
                    'has_results': len(results) > 0
                }
                
            except Exception as e:
                search_results[query] = {
                    'error': str(e),
                    'has_results': False
                }
        
        # Check if any searches returned results
        successful_searches = sum(1 for r in search_results.values() if r.get('has_results', False))
        
        if successful_searches == 0:
            raise Exception("No search queries returned results - database may be empty")
        
        return {
            'total_test_queries': len(test_queries),
            'successful_searches': successful_searches,
            'search_results': search_results,
            'search_functionality_working': successful_searches > 0
        }
    
    def test_sample_document_retrieval(self) -> Dict[str, Any]:
        """Test retrieving and analyzing sample documents."""
        if not self.vector_store:
            raise Exception("Vector store not initialized")
        
        try:
            # Get some sample documents
            results = self.vector_store.similarity_search("leki", k=5)
            
            if not results:
                raise Exception("No documents found for sample retrieval")
            
            sample_docs = []
            for i, doc in enumerate(results):
                sample_doc = {
                    'index': i + 1,
                    'content_length': len(doc.page_content),
                    'metadata_keys': list(doc.metadata.keys()),
                    'has_h1': 'h1' in doc.metadata,
                    'has_h2': 'h2' in doc.metadata,
                    'has_source': 'source' in doc.metadata,
                    'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sample_docs.append(sample_doc)
            
            return {
                'sample_documents_found': len(sample_docs),
                'sample_documents': sample_docs,
                'average_content_length': sum(doc['content_length'] for doc in sample_docs) / len(sample_docs),
                'documents_with_metadata': sum(1 for doc in sample_docs if doc['metadata_keys'])
            }
            
        except Exception as e:
            raise Exception(f"Sample document retrieval failed: {str(e)}")
    
    def test_data_directory(self) -> Dict[str, Any]:
        """Test if the source data directory exists and contains documents."""
        data_path = Path(DATA_PATH)
        
        if not data_path.exists():
            raise Exception(f"Data directory '{DATA_PATH}' does not exist")
        
        # Count markdown files
        md_files = list(data_path.glob("**/*.md"))
        
        if not md_files:
            raise Exception(f"No markdown files found in '{DATA_PATH}'")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in md_files)
        
        return {
            'data_directory_exists': True,
            'data_directory_path': str(data_path.absolute()),
            'markdown_files_count': len(md_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'sample_files': [f.name for f in md_files[:5]]
        }
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test database performance metrics."""
        if not self.vector_store:
            raise Exception("Vector store not initialized")
        
        performance_tests = {}
        
        # Test search performance
        start_time = time.time()
        results = self.vector_store.similarity_search("test", k=10)
        search_time = time.time() - start_time
        
        performance_tests['search_time_10_results'] = round(search_time, 3)
        
        # Test embedding performance
        start_time = time.time()
        embedding = self.embeddings.embed_query("performance test query")
        embedding_time = time.time() - start_time
        
        performance_tests['embedding_time'] = round(embedding_time, 3)
        
        return {
            'search_performance': performance_tests,
            'performance_acceptable': search_time < 5.0,  # Search should take less than 5 seconds
            'embedding_performance_acceptable': embedding_time < 2.0  # Embedding should take less than 2 seconds
        }
    
    def _generate_summary(self, total_time: float):
        """Generate a comprehensive test summary."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        total_tests = len(self.test_results)
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Execution Time: {total_time:.2f} seconds")
        
        # Overall status
        if failed_tests == 0:
            logger.info("\n[SUCCESS] ALL TESTS PASSED! Database is online and properly ingested.")
        else:
            logger.info(f"\n[WARNING] {failed_tests} TESTS FAILED. Please review the issues above.")
        
        # Failed tests details
        if failed_tests > 0:
            logger.info("\nFAILED TESTS:")
            for test_name, result in self.test_results.items():
                if result['status'] == 'FAIL':
                    logger.error(f"  [FAIL] {test_name}: {result['error']}")
        
        # Key metrics
        logger.info("\nKEY METRICS:")
        try:
            if 'Document Count Check' in self.test_results and self.test_results['Document Count Check']['status'] == 'PASS':
                doc_count = self.test_results['Document Count Check']['result']['document_count']
                logger.info(f"  [DOCS] Documents in database: {doc_count}")
            
            if 'Search Functionality' in self.test_results and self.test_results['Search Functionality']['status'] == 'PASS':
                successful_searches = self.test_results['Search Functionality']['result']['successful_searches']
                logger.info(f"  [SEARCH] Successful search queries: {successful_searches}")
            
            if 'Performance Metrics' in self.test_results and self.test_results['Performance Metrics']['status'] == 'PASS':
                search_time = self.test_results['Performance Metrics']['result']['search_performance']['search_time_10_results']
                logger.info(f"  [PERF] Average search time: {search_time}s")
                
        except Exception as e:
            logger.warning(f"Could not extract key metrics: {e}")
        
        logger.info("=" * 80)
    
    def cleanup(self):
        """Clean up database connections."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

def main():
    """Main function to run the database ingestion tests."""
    tester = DatabaseIngestionTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results.values() if result['status'] == 'FAIL')
        sys.exit(0 if failed_tests == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during test execution: {str(e)}")
        sys.exit(1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
