"""
Database module for PharmaRAG service.
Handles Chroma database operations and embeddings.
"""

import time
import threading
import json
import os
from typing import List, Optional, Dict, Any
import logging

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

try:
    from .config import CHROMA_PATH, API_KEY, ENABLE_CACHE
    from .cache import medicine_names_cache, generate_cache_key
    from .performance_monitor import monitor_operation, performance_monitor
except ImportError:
    from config import CHROMA_PATH, API_KEY, ENABLE_CACHE
    from cache import medicine_names_cache, generate_cache_key
    from performance_monitor import monitor_operation, performance_monitor

logger = logging.getLogger(__name__)

# Global embeddings instance to avoid reinitialization
_embeddings_instance: Optional[OpenAIEmbeddings] = None
_embeddings_lock = threading.Lock()

# Global Chroma database instance for connection pooling
_chroma_db_instance: Optional[Chroma] = None
_chroma_lock = threading.Lock()

# Global medicine names cache from JSON file
_medicine_names_json: Optional[List[str]] = None
_medicine_names_json_lock = threading.Lock()

# Document cache for frequently accessed documents
_document_cache: Dict[str, Any] = {}
_document_cache_lock = threading.Lock()

# Query result cache for database queries
_query_cache: Dict[str, Any] = {}
_query_cache_lock = threading.Lock()

# Database connection status
_db_initialized = False
_db_init_lock = threading.Lock()


def get_embeddings_instance() -> OpenAIEmbeddings:
    """Get or create OpenAI embeddings instance (singleton pattern)"""
    global _embeddings_instance
    
    if _embeddings_instance is None:
        with _embeddings_lock:
            if _embeddings_instance is None:
                logger.info("Initializing OpenAI embeddings instance")
                _embeddings_instance = OpenAIEmbeddings(api_key=API_KEY)
                logger.info("OpenAI embeddings instance initialized")
    
    return _embeddings_instance


def get_chroma_db() -> Chroma:
    """Get Chroma database instance with connection pooling"""
    global _chroma_db_instance, _db_initialized
    
    if _chroma_db_instance is None:
        with _chroma_lock:
            if _chroma_db_instance is None:
                logger.info("Initializing Chroma database connection pool")
                embedding_function = get_embeddings_instance()
                _chroma_db_instance = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
                _db_initialized = True
                logger.info("Chroma database connection pool initialized")
    
    return _chroma_db_instance


def get_chroma_collection():
    """Get Chroma collection directly for optimized queries"""
    db = get_chroma_db()
    return db._collection


def pre_warm_database():
    """Pre-warm the database connection to avoid cold start"""
    global _db_initialized
    
    if not _db_initialized:
        with _db_init_lock:
            if not _db_initialized:
                logger.info("Pre-warming database connection...")
                try:
                    get_chroma_db()
                    logger.info("Database pre-warmed successfully")
                except Exception as e:
                    logger.warning(f"Database pre-warming failed: {e}")


# Pre-warm database on module import
pre_warm_database()


def cache_query_result(query_key: str, result: Any):
    """Cache query results for faster subsequent access"""
    with _query_cache_lock:
        _query_cache[query_key] = result
        # Limit cache size
        if len(_query_cache) > 50:
            # Remove oldest entry
            oldest_key = next(iter(_query_cache))
            del _query_cache[oldest_key]


def get_cached_query_result(query_key: str) -> Optional[Any]:
    """Get cached query result if available"""
    with _query_cache_lock:
        return _query_cache.get(query_key)


def load_medicine_names_from_json() -> List[str]:
    """
    Load medicine names from JSON file with caching
    
    Returns:
        List of medicine names
        
    Performance targets:
        - First call: Load from JSON file
        - Subsequent calls: Return cached data
        - Memory usage: < 10MB additional
    """
    global _medicine_names_json
    
    if _medicine_names_json is not None:
        return _medicine_names_json
    
    with _medicine_names_json_lock:
        if _medicine_names_json is not None:
            return _medicine_names_json
        
        start_time = time.time()
        json_file_path = os.path.join(os.path.dirname(__file__), 'medicine_names_minimal.json')
        
        try:
            logger.info(f"Loading medicine names from JSON file: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            names = data.get('names', [])
            _medicine_names_json = names
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"Loaded {len(names)} medicine names from JSON file. Response time: {elapsed_time:.2f}ms")
            
            return names
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(f"Error loading medicine names from JSON after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
            raise


@monitor_operation("get_medicine_names_from_chroma")
def get_medicine_names_from_chroma(force_refresh: bool = False) -> List[str]:
    """
    Get list of medicine names from Chroma database with caching and optimization
    
    Args:
        force_refresh: If True, bypass cache and fetch fresh data
        
    Returns:
        List of unique medicine names
        
    Performance targets:
        - First call: Same as current implementation
        - Subsequent calls: < 500ms (cache hit)
        - Memory usage: < 50MB additional
    """
    start_time = time.time()
    cache_key = generate_cache_key("get_medicine_names_from_chroma")
    
    try:
        # Check cache first (unless force refresh)
        if not force_refresh and ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.info(f"Cache HIT for medicine names. Response time: {elapsed_time:.2f}ms")
                return cached_result
        
        # Cache miss or force refresh - fetch from database
        logger.info("Fetching medicine names from Chroma database (cache miss or force refresh)")
        
        # Use optimized database query
        collection = get_chroma_collection()
        
        # Optimize query to fetch only necessary metadata
        results = collection.get(
            include=['metadatas'],  # Only fetch metadata, not full documents
            limit=None  # Get all results
        )
        
        names = []
        if results and 'metadatas' in results and results['metadatas']:
            for metadata in results['metadatas']:
                if metadata and isinstance(metadata, dict):
                    # Get the medicine name from h1 or filename
                    name = metadata.get('h1', '')
                    if name and isinstance(name, str) and name.strip():
                        names.append(name.strip())
        
        # Remove duplicates and sort
        unique_names = sorted(list(set(names)))
        
        # Cache the result
        if ENABLE_CACHE:
            medicine_names_cache.set(cache_key, unique_names)
            logger.info(f"Cached medicine names result (TTL: 10 minutes)")
        
        elapsed_time = (time.time() - start_time) * 1000
        logger.info(f"Database query completed. Found {len(unique_names)} unique medicine names. Response time: {elapsed_time:.2f}ms")
        
        return unique_names
        
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(f"Error fetching medicine names after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
        
        # Try to return cached data as fallback if available
        if ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                logger.warning(f"Returning cached data as fallback due to database error: {str(e)}")
                return cached_result
        
        # Re-raise the exception if no fallback available
        raise


def get_paginated_medicine_names(page: int = 1, page_size: int = 20, force_refresh: bool = False) -> tuple[List[str], int, int, int, bool, bool]:
    """
    Get paginated list of medicine names from JSON file with efficient loading
    
    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        force_refresh: If True, bypass cache and fetch fresh data
        
    Returns:
        Tuple of (names, total_count, total_pages, has_next, has_previous)
        
    Performance targets:
        - First call: Load from JSON file
        - Subsequent calls: < 50ms (memory cache hit)
        - Memory usage: < 10MB additional
    """
    start_time = time.time()
    cache_key = generate_cache_key(f"get_paginated_medicine_names_{page}_{page_size}")
    
    try:
        # Check cache first (unless force refresh)
        if not force_refresh and ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.info(f"Cache HIT for paginated medicine names (page {page}). Response time: {elapsed_time:.2f}ms")
                return cached_result
        
        # Cache miss or force refresh - load from JSON file
        logger.info(f"Loading paginated medicine names from JSON file (page {page}, size {page_size})")
        
        # Load all medicine names from JSON file (this is cached in memory)
        all_names = load_medicine_names_from_json()
        total_count = len(all_names)
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # Get the page of names
        page_names = all_names[start_index:end_index]
        
        # Calculate pagination flags
        has_next = page < total_pages
        has_previous = page > 1
        
        result = (page_names, total_count, total_pages, has_next, has_previous)
        
        # Cache the result
        if ENABLE_CACHE:
            medicine_names_cache.set(cache_key, result)
            logger.info(f"Cached paginated medicine names result (page {page}, TTL: 10 minutes)")
        
        elapsed_time = (time.time() - start_time) * 1000
        logger.info(f"JSON file pagination completed. Page {page}/{total_pages}, {len(page_names)} names. Response time: {elapsed_time:.2f}ms")
        
        return result
        
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(f"Error loading paginated medicine names after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
        
        # Try to return cached data as fallback if available
        if ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                logger.warning(f"Returning cached data as fallback due to JSON loading error: {str(e)}")
                return cached_result
        
        # Re-raise the exception if no fallback available
        raise


def search_medicine_names(query: str, page: int = 1, page_size: int = 20, force_refresh: bool = False) -> tuple[List[str], int, int, int, bool, bool]:
    """
    Search medicine names across all medicines with intelligent search logic
    
    Args:
        query: Search query string
        page: Page number (1-based)
        page_size: Number of items per page
        force_refresh: If True, bypass cache and fetch fresh data
        
    Returns:
        Tuple of (names, total_count, total_pages, has_next, has_previous)
    """
    start_time = time.time()
    cache_key = generate_cache_key(f"search_medicine_names_{query}_{page}_{page_size}")
    
    try:
        # Check cache first (unless force refresh)
        if not force_refresh and ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.info(f"Cache HIT for medicine names search '{query}' (page {page}). Response time: {elapsed_time:.2f}ms")
                return cached_result
        
        # Cache miss or force refresh - load from JSON file
        logger.info(f"Searching medicine names for query '{query}' (page {page}, size {page_size})")
        
        # Load all medicine names from JSON file (this is cached in memory)
        all_names = load_medicine_names_from_json()
        
        # Intelligent search logic based on query length
        query_lower = query.lower().strip()
        query_length = len(query_lower)
        
        if query_length == 1:
            # 1 letter: medicines starting with this letter
            filtered_names = [
                name for name in all_names 
                if name.lower().startswith(query_lower)
            ]
        elif query_length == 2:
            # 2 letters: medicines starting with this sequence
            filtered_names = [
                name for name in all_names 
                if name.lower().startswith(query_lower)
            ]
        else:
            # 3+ letters: medicines containing this sequence anywhere
            filtered_names = [
                name for name in all_names 
                if query_lower in name.lower()
            ]
        
        total_count = len(filtered_names)
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # Get the page of filtered names
        page_names = filtered_names[start_index:end_index]
        
        # Calculate pagination flags
        has_next = page < total_pages
        has_previous = page > 1
        
        result = (page_names, total_count, total_pages, has_next, has_previous)
        
        # Cache the result
        if ENABLE_CACHE:
            medicine_names_cache.set(cache_key, result)
            logger.info(f"Cached medicine names search result for '{query}' (page {page}, TTL: 10 minutes)")
        
        elapsed_time = (time.time() - start_time) * 1000
        search_type = "starts_with" if query_length <= 2 else "contains"
        logger.info(f"JSON file search completed. Query: '{query}' ({search_type}), Page {page}/{total_pages}, {len(page_names)} results. Response time: {elapsed_time:.2f}ms")
        
        return result
        
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(f"Error searching medicine names after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
        
        # Try to return cached data as fallback if available
        if ENABLE_CACHE:
            cached_result = medicine_names_cache.get(cache_key)
            if cached_result is not None:
                logger.warning(f"Returning cached data as fallback due to JSON loading error: {str(e)}")
                return cached_result
        
        # Re-raise the exception if no fallback available
        raise


@monitor_operation("get_document_by_name")
def get_document_by_name(medicine_name: str):
    """
    Get a specific document by medicine name - returns the FULL document by combining all chunks
    Ultra-optimized version with multi-level caching
    """
    overall_start = time.time()
    logger.info(f"Fetching document for medicine: {medicine_name}")
    
    # Initialize timing variables
    cache_time = 0.0
    db_time = 0.0
    query_time = 0.0
    processing_time = 0.0
    sorting_time = 0.0
    reconstruction_time = 0.0
    filename_time = 0.0
    doc_creation_time = 0.0
    cache_set_time = 0.0
    
    # Check memory cache first (fastest)
    cache_start = time.time()
    with _document_cache_lock:
        if medicine_name in _document_cache:
            cache_time = (time.time() - cache_start) * 1000
            logger.info(f"Memory cache HIT for document: {medicine_name}. Cache lookup time: {cache_time:.2f}ms")
            return _document_cache[medicine_name]
    
    # Check persistent cache
    cache_key = generate_cache_key(f"document_{medicine_name}")
    if ENABLE_CACHE:
        cached_result = medicine_names_cache.get(cache_key)
        if cached_result is not None:
            # Store in memory cache for faster future access
            with _document_cache_lock:
                _document_cache[medicine_name] = cached_result
            cache_time = (time.time() - cache_start) * 1000
            logger.info(f"Persistent cache HIT for document: {medicine_name}. Cache lookup time: {cache_time:.2f}ms")
            return cached_result
    
    cache_time = (time.time() - cache_start) * 1000
    logger.info(f"Cache MISS for document: {medicine_name}. Cache lookup time: {cache_time:.2f}ms")
    
    try:
        # Load Chroma database (now cached)
        db_start = time.time()
        collection = get_chroma_collection()
        db_time = (time.time() - db_start) * 1000
        logger.info(f"Database initialization time: {db_time:.2f}ms")
        
        # Single optimized query with intelligent fallback
        matching_chunks = []
        query_start = time.time()
        
        # Check query cache first
        query_key = f"exact_{medicine_name}"
        cached_results = get_cached_query_result(query_key)
        
        if cached_results:
            results = cached_results
            logger.info(f"Query cache HIT for '{medicine_name}'")
        else:
            # Try exact match first (fastest)
            logger.info(f"Trying exact match for '{medicine_name}'")
            query_start = time.time()
            results = collection.get(
                where={"h1": medicine_name},
                include=['metadatas', 'documents'],
                limit=None
            )
            exact_query_time = (time.time() - query_start) * 1000
            performance_monitor.record_operation("db_exact_query", exact_query_time)
            
            # Cache the result
            cache_query_result(query_key, results)
        
        # If no exact match, try case-insensitive search
        if not results or not results.get('metadatas'):
            logger.info(f"No exact match found, trying case-insensitive search")
            
            # Check fuzzy query cache
            fuzzy_query_key = f"fuzzy_{medicine_name.lower()}"
            cached_fuzzy_results = get_cached_query_result(fuzzy_query_key)
            
            if cached_fuzzy_results:
                results = cached_fuzzy_results
                logger.info(f"Fuzzy query cache HIT for '{medicine_name}'")
            else:
                # Use a more efficient query with where clause for case-insensitive search
                query_start = time.time()
                results = collection.get(
                    where={"h1": {"$contains": medicine_name.lower()}},
                    include=['metadatas', 'documents'],
                    limit=100  # Limit results for faster processing
                )
                fuzzy_query_time = (time.time() - query_start) * 1000
                performance_monitor.record_operation("db_fuzzy_query", fuzzy_query_time)
                
                # Cache the fuzzy result
                cache_query_result(fuzzy_query_key, results)
        
        query_time = (time.time() - query_start) * 1000
        logger.info(f"Database query time: {query_time:.2f}ms")
        
        # Process results
        processing_start = time.time()
        if results and results.get('metadatas'):
            logger.info(f"Found {len(results['metadatas'])} potential chunks")
            
            for i, metadata in enumerate(results['metadatas']):
                if metadata and isinstance(metadata, dict):
                    h1 = metadata.get('h1', '')
                    # Check for exact match (case-insensitive)
                    if h1.lower() == medicine_name.lower():
                        chunk_content = results['documents'][i] if i < len(results['documents']) else ""
                        matching_chunks.append({
                            'content': chunk_content,
                            'metadata': metadata
                        })
                        logger.info(f"Found matching chunk {len(matching_chunks)}: h2='{metadata.get('h2', '')}', content_length={len(chunk_content)}")
        
        processing_time = (time.time() - processing_start) * 1000
        logger.info(f"Chunk processing time: {processing_time:.2f}ms")
        
        if not matching_chunks:
            logger.warning(f"No document found for medicine: {medicine_name}")
            return None
        
        # Sort chunks by their order (if available) or by h2 section
        sorting_start = time.time()
        matching_chunks.sort(key=lambda x: (
            x['metadata'].get('h2', ''),  # Sort by h2 section
            x['metadata'].get('chunk_index', 0)  # Then by chunk index if available
        ))
        sorting_time = (time.time() - sorting_start) * 1000
        logger.info(f"Chunk sorting time: {sorting_time:.2f}ms")
        
        # Reconstruct the full document with proper markdown structure
        reconstruction_start = time.time()
        document_sections = []
        current_h2 = None
        
        for chunk in matching_chunks:
            h2 = chunk['metadata'].get('h2', '')
            content = chunk['content'].strip()
            
            # If this is a new h2 section, add the markdown heading
            if h2 and h2 != current_h2:
                # Add ## heading for the new section
                document_sections.append(f"## {h2}")
                current_h2 = h2
                # Add the content after the heading
                if content:
                    document_sections.append(content)
            else:
                # Same section, just add content
                if content:
                    document_sections.append(content)
        
        # Combine all sections with proper spacing
        full_content = "\n\n".join(document_sections)
        reconstruction_time = (time.time() - reconstruction_start) * 1000
        logger.info(f"Document reconstruction time: {reconstruction_time:.2f}ms")
        
        # Extract filename from source path
        filename_start = time.time()
        target_source = matching_chunks[0]['metadata'].get('source', '') if matching_chunks else ''
        filename = target_source.split('/')[-1] if target_source else f"{medicine_name}.md"
        filename_time = (time.time() - filename_start) * 1000
        logger.info(f"Filename extraction time: {filename_time:.2f}ms")
        
        # Create document info with full content
        doc_creation_start = time.time()
        try:
            from .models import DocumentInfo
        except ImportError:
            from models import DocumentInfo
        doc_info = DocumentInfo(
            name=medicine_name,
            filename=filename,
            source=target_source,
            h1=medicine_name,
            h2="",  # Full document doesn't have a specific h2
            content=full_content
        )
        doc_creation_time = (time.time() - doc_creation_start) * 1000
        logger.info(f"DocumentInfo creation time: {doc_creation_time:.2f}ms")
        
        # Cache the result for future requests
        cache_set_start = time.time()
        if ENABLE_CACHE:
            medicine_names_cache.set(cache_key, doc_info)
            logger.info(f"Cached document result for '{medicine_name}' (TTL: 10 minutes)")
        
        # Store in memory cache for fastest future access
        with _document_cache_lock:
            _document_cache[medicine_name] = doc_info
            # Limit memory cache size to prevent memory issues
            if len(_document_cache) > 100:
                # Remove oldest entries (simple FIFO)
                oldest_key = next(iter(_document_cache))
                del _document_cache[oldest_key]
        
        cache_set_time = (time.time() - cache_set_start) * 1000
        logger.info(f"Cache set time: {cache_set_time:.2f}ms")
        
        # Overall timing summary
        overall_time = (time.time() - overall_start) * 1000
        logger.info(f"Found document for {medicine_name}")
        logger.info(f"Combined {len(matching_chunks)} chunks into full document")
        logger.info(f"Document info: name='{doc_info.name}', filename='{doc_info.filename}', content_length={len(doc_info.content) if doc_info.content else 0}")
        logger.info(f"Document sections: {[chunk['metadata'].get('h2', '') for chunk in matching_chunks]}")
        logger.info(f"TOTAL TIME BREAKDOWN:")
        logger.info(f"  - Cache lookup: {cache_time:.2f}ms")
        logger.info(f"  - Database init: {db_time:.2f}ms")
        logger.info(f"  - Database query: {query_time:.2f}ms")
        logger.info(f"  - Chunk processing: {processing_time:.2f}ms")
        logger.info(f"  - Chunk sorting: {sorting_time:.2f}ms")
        logger.info(f"  - Document reconstruction: {reconstruction_time:.2f}ms")
        logger.info(f"  - Filename extraction: {filename_time:.2f}ms")
        logger.info(f"  - DocumentInfo creation: {doc_creation_time:.2f}ms")
        logger.info(f"  - Cache set: {cache_set_time:.2f}ms")
        logger.info(f"  - TOTAL: {overall_time:.2f}ms")
        return doc_info
        
    except Exception as e:
        overall_time = (time.time() - overall_start) * 1000
        logger.error(f"Error fetching document by name after {overall_time:.2f}ms: {str(e)}", exc_info=True)
        raise


def get_documents_from_chroma():
    """
    Get list of all documents from Chroma database
    """
    try:
        collection = get_chroma_collection()
        
        # Get all documents with metadata and content
        results = collection.get(
            include=['metadatas', 'documents'],
            limit=None
        )
        
        documents = []
        if results and 'metadatas' in results and 'documents' in results:
            for i, metadata in enumerate(results['metadatas']):
                if metadata and isinstance(metadata, dict):
                    # Get document content
                    content = results['documents'][i] if i < len(results['documents']) else ""
                    
                    # Create DocumentInfo object
                    try:
                        from .models import DocumentInfo
                    except ImportError:
                        from models import DocumentInfo
                    doc_info = DocumentInfo(
                        name=metadata.get('h1', '') or 'Unknown',
                        filename=metadata.get('source', '').split('/')[-1] if metadata.get('source') else 'Unknown.md',
                        source=metadata.get('source', ''),
                        h1=metadata.get('h1', ''),
                        h2=metadata.get('h2', ''),
                        content=content
                    )
                    documents.append(doc_info)
        
        return documents
        
    except Exception as e:
        logger.error(f"Error fetching documents from Chroma: {str(e)}", exc_info=True)
        raise
