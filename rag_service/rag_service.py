
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import time
import threading
from functools import lru_cache
from datetime import datetime, timedelta
import json
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

CHROMA_PATH = "chroma"
TEMPERATURE = 0.2

# Cache configuration
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "10"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL","gpt-4o-mini")

# Log API key status (without exposing the actual key)
if API_KEY:
    logger.info("API_KEY loaded successfully")
else:
    logger.warning("API_KEY not found in environment variables")

# Global cache storage with thread safety
class ThreadSafeCache:
    def __init__(self, ttl_minutes: int = 10, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_minutes * 60
        self.max_size = max_size
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check"""
        with self.lock:
            self.stats["total_requests"] += 1
            
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            cache_entry = self.cache[key]
            if time.time() > cache_entry["expires_at"]:
                # Expired, remove it
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return cache_entry["value"]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL"""
        with self.lock:
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size:
                self._evict_expired_and_old()
            
            self.cache[key] = {
                "value": value,
                "expires_at": time.time() + self.ttl_seconds,
                "created_at": time.time()
            }
    
    def _evict_expired_and_old(self) -> None:
        """Evict expired entries and oldest entries if still over limit"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = [k for k, v in self.cache.items() if current_time > v["expires_at"]]
        for key in expired_keys:
            del self.cache[key]
        
        # If still over limit, remove oldest entries
        if len(self.cache) >= self.max_size:
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1]["created_at"])
            entries_to_remove = len(sorted_entries) - self.max_size + 1
            for i in range(entries_to_remove):
                del self.cache[sorted_entries[i][0]]
                self.stats["evictions"] += 1
    
    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (self.stats["hits"] / max(self.stats["total_requests"], 1)) * 100
            return {
                **self.stats,
                "hit_rate_percent": round(hit_rate, 2),
                "current_size": len(self.cache),
                "max_size": self.max_size,
                "ttl_minutes": self.ttl_seconds / 60
            }

# Initialize global cache
medicine_names_cache = ThreadSafeCache(ttl_minutes=CACHE_TTL_MINUTES, max_size=CACHE_MAX_SIZE)

# Global embeddings instance to avoid reinitialization
_embeddings_instance: Optional[OpenAIEmbeddings] = None
_embeddings_lock = threading.Lock()

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
    """Get Chroma database instance with optimized configuration"""
    embedding_function = get_embeddings_instance()
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """Generate a unique cache key for function calls"""
    # Create a hash of the function name and arguments
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": kwargs,
        "chroma_path": CHROMA_PATH  # Include database path in cache key
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()

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
        db = get_chroma_db()
        collection = db._collection
        
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
            logger.info(f"Cached medicine names result (TTL: {CACHE_TTL_MINUTES} minutes)")
        
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

def invalidate_medicine_names_cache() -> Dict[str, str]:
    """Invalidate the medicine names cache"""
    try:
        cache_key = generate_cache_key("get_medicine_names_from_chroma")
        medicine_names_cache.invalidate(cache_key)
        logger.info("Medicine names cache invalidated successfully")
        return {"status": "success", "message": "Cache invalidated successfully"}
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Failed to invalidate cache: {str(e)}"}

def refresh_medicine_names_cache() -> Dict[str, Any]:
    """Force refresh the medicine names cache"""
    start_time = time.time()
    try:
        # Force refresh by calling with force_refresh=True
        names = get_medicine_names_from_chroma(force_refresh=True)
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"Cache refreshed successfully. Found {len(names)} names. Refresh time: {elapsed_time:.2f}ms")
        
        return {
            "status": "success",
            "message": "Cache refreshed successfully",
            "names_count": len(names),
            "refresh_time_ms": round(elapsed_time, 2)
        }
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(f"Error refreshing cache after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to refresh cache: {str(e)}",
            "refresh_time_ms": round(elapsed_time, 2)
        }

def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    try:
        cache_stats = medicine_names_cache.get_stats()
        
        # Add additional performance metrics
        performance_metrics = {
            "cache_enabled": ENABLE_CACHE,
            "cache_ttl_minutes": CACHE_TTL_MINUTES,
            "cache_max_size": CACHE_MAX_SIZE,
            "embeddings_instance_initialized": _embeddings_instance is not None,
            "chroma_path": CHROMA_PATH,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "cache_stats": cache_stats,
            "performance_metrics": performance_metrics
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}", exc_info=True)
        return {"error": f"Failed to get cache stats: {str(e)}"}

PROMPT_TEMPLATE = """
Odpowiedz na pytanie tylko na podstawie poniższych informacji:
{context}
---
Odpowiedz na pytanie tylko na podstawie powyższego kontekstu: {question}

Jeśli w kontekście nie ma istotnych informacji na temat pytania, grzecznie poinformuj o tym użytkownika i zasugeruj, aby zadał pytanie związane z lekami lub farmacją, na które mogę odpowiedzieć na podstawie dostępnych informacji.
"""

# FastAPI app initialization
app = FastAPI(
    title="PharmaRAG Service",
    description="A RAG service for pharmaceutical information queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add a test endpoint to verify CORS
@app.get("/test-cors")
async def test_cors():
    """
    Test endpoint to verify CORS is working
    """
    logger.info("CORS test endpoint accessed")
    return {"message": "CORS is working!", "timestamp": time.time()}

# Pydantic models for request/response
class RAGRequest(BaseModel):
    question: str

class RAGResponse(BaseModel):
    response: str
    sources: List[Optional[str]]
    metadata: List[dict]  # New field for metadata including h1 and h2

class DocumentInfo(BaseModel):
    name: str
    filename: str
    source: Optional[str]
    h1: Optional[str]
    h2: Optional[str]
    content: Optional[str]

class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int

class MedicineNamesResponse(BaseModel):
    names: List[str]
    total_count: int

def get_documents_from_chroma() -> List[DocumentInfo]:
    """
    Get list of all documents from Chroma database
    """
    try:
        db = get_chroma_db()
        collection = db._collection
        
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

# Middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Log CORS-specific headers
    origin = request.headers.get("origin")
    if origin:
        logger.info(f"CORS Origin: {origin}")
    
    # Log request body for POST requests
    if request.method == "POST":
        try:
            body = await request.body()
            if body:
                logger.info(f"Request body: {body.decode()}")
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Response time: {process_time:.3f}s")
    
    # Log CORS response headers
    cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
    if cors_headers:
        logger.info(f"CORS Response headers: {cors_headers}")
    
    return response

def query(query_text: str):
    logger.info(f"Processing query: {query_text}")
    
    try:
        # Prepare the DB.
        logger.info("Getting OpenAI embeddings instance...")
        embedding_function = get_embeddings_instance()
        logger.info("Embeddings instance retrieved successfully")
        
        logger.info(f"Loading Chroma database from: {CHROMA_PATH}")
        db = get_chroma_db()
        logger.info("Chroma database loaded successfully")

        # Search the DB.
        logger.info(f"Searching database with k=3...")
        results = db.similarity_search_with_relevance_scores(query_text, k=3)
        logger.info(f"Found {len(results)} results")
        
        # Log relevance scores
        for i, (doc, score) in enumerate(results):
            logger.info(f"Result {i+1}: score={score:.4f}, source={doc.metadata.get('source', 'unknown')}")
            logger.info(f"Result {i+1} metadata: h1='{doc.metadata.get('h1', '')}', h2='{doc.metadata.get('h2', '')}'")
        
        # Check if we have any results and if the best score is reasonable
        has_relevant_results = len(results) > 0 and results[0][1] >= 0.7
        
        logger.info(f"Relevance threshold: 0.7, Best score: {results[0][1] if results else 'no results'}")
        
        if not has_relevant_results:
            logger.warning(f"No relevant results found. Best score: {results[0][1] if results else 'no results'}")
            # Instead of raising an error, we'll create a context indicating no relevant information
            context_text = "Nie znaleziono żadnych istotnych informacji w bazie danych na temat tego zapytania. Baza danych zawiera informacje o lekach i farmacji, ale to konkretne zapytanie nie pasuje do dostępnych danych."
            logger.info("Using fallback context for no relevant results")
            logger.info(f"Fallback context: {context_text}")
        else:
            def _fmt_chunk(doc):
                # Prefer direct h1/h2; fall back to parent_section if you stored it that way
                ps = doc.metadata.get("parent_section", {}) or {}
                h1 = doc.metadata.get("h1") or ps.get("h1") or ""
                h2 = doc.metadata.get("h2") or ps.get("h2") or ""
                src = doc.metadata.get("source") or doc.metadata.get("path") or doc.metadata.get("doc_id") or ""

                title_parts = [p for p in [h1, h2] if p]
                title = " > ".join(title_parts) if title_parts else "Fragment"

                header_lines = [f"## {title}"]
                if src:
                    header_lines.append(f"[Source: {src}]")
                header = "\n".join(header_lines)

                body = doc.page_content.strip()
                return f"{header}\n{body}"

            context_text = "\n\n---\n\n".join([_fmt_chunk(doc) for doc, _score in results])
            logger.info(f"Context length: {len(context_text)} characters")

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        # Log a truncated version of the prompt for debugging
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        logger.info(f"Prompt preview: {prompt_preview}")
        
        logger.info("Initializing ChatOpenAI model...")
        model = ChatOpenAI(api_key=API_KEY, temperature=TEMPERATURE, model=MODEL)
        logger.info("Model initialized successfully")
        
        logger.info("Generating response...")
        response_text = model.predict(prompt)
        logger.info(f"Response generated, length: {len(response_text)} characters")

        # For cases with no relevant results, we don't have sources
        if has_relevant_results:
            sources = [doc.metadata.get("source", None) for doc, _score in results]
            # Extract metadata including h1 and h2 headers
            metadata = []
            for doc, _score in results:
                doc_metadata = {
                    "h1": doc.metadata.get("h1", ""),
                    "h2": doc.metadata.get("h2", ""),
                    "source": doc.metadata.get("source", ""),
                    "relevance_score": _score,
                    "chunk_content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                metadata.append(doc_metadata)
        else:
            sources = []
            metadata = []
        logger.info(f"Sources: {sources}")
        logger.info(f"Metadata: {metadata}")
        
        return response_text, sources, metadata
        
    except Exception as e:
        logger.error(f"Error in query function: {str(e)}", exc_info=True)
        raise

def get_document_by_name(medicine_name: str):
    """
    Get a specific document by medicine name - returns the FULL document by combining all chunks
    """
    logger.info(f"Fetching document for medicine: {medicine_name}")
    
    try:
        # Load Chroma database
        db = get_chroma_db()
        collection = db._collection
        
        # Get ALL documents from the collection
        results = collection.get(
            include=['metadatas', 'documents'],
            limit=None
        )
        
        # Find all chunks that belong to the same document (same h1)
        matching_chunks = []
        target_source = None
        target_h1 = None
        
        logger.info(f"Searching through {len(results.get('metadatas', []))} total chunks for medicine: {medicine_name}")
        
        if results and 'metadatas' in results and 'documents' in results:
            for i, metadata in enumerate(results['metadatas']):
                if metadata and isinstance(metadata, dict):
                    h1 = metadata.get('h1', '')
                    if h1.lower() == medicine_name.lower():
                        chunk_content = results['documents'][i] if i < len(results['documents']) else ""
                        matching_chunks.append({
                            'content': chunk_content,
                            'metadata': metadata
                        })
                        if target_source is None:
                            target_source = metadata.get('source', '')
                            target_h1 = h1
                        logger.info(f"Found matching chunk {len(matching_chunks)}: h2='{metadata.get('h2', '')}', content_length={len(chunk_content)}")
        
        if not matching_chunks:
            logger.warning(f"No document found for medicine: {medicine_name}")
            return None
        
        # Sort chunks by their order (if available) or by h2 section
        matching_chunks.sort(key=lambda x: (
            x['metadata'].get('h2', ''),  # Sort by h2 section
            x['metadata'].get('chunk_index', 0)  # Then by chunk index if available
        ))
        
        # Combine all chunks into a single document
        full_content = "\n\n".join([chunk['content'] for chunk in matching_chunks])
        
        # Extract filename from source path
        filename = target_source.split('/')[-1] if target_source else f"{medicine_name}.md"
        
        # Create document info with full content
        doc_info = DocumentInfo(
            name=target_h1 or medicine_name,
            filename=filename,
            source=target_source,
            h1=target_h1,
            h2="",  # Full document doesn't have a specific h2
            content=full_content
        )
        
        logger.info(f"Found document for {medicine_name}")
        logger.info(f"Combined {len(matching_chunks)} chunks into full document")
        logger.info(f"Document info: name='{doc_info.name}', filename='{doc_info.filename}', content_length={len(doc_info.content) if doc_info.content else 0}")
        return doc_info
        
    except Exception as e:
        logger.error(f"Error fetching document by name: {str(e)}", exc_info=True)
        raise

@app.get("/medicine-names", response_model=MedicineNamesResponse)
async def get_medicine_names():
    """
    Get list of all medicine names (fast, no content)
    """
    logger.info("Received request for medicine names")
    
    try:
        names = get_medicine_names_from_chroma()
        return MedicineNamesResponse(names=names, total_count=len(names))
    except Exception as e:
        logger.error(f"Error in get_medicine_names: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/medicine-names/refresh", response_model=Dict[str, Any])
async def refresh_medicine_names():
    """
    Force refresh the list of medicine names in the cache.
    """
    logger.info("Received request to refresh medicine names cache")
    try:
        refresh_result = refresh_medicine_names_cache()
        logger.info(f"Medicine names cache refreshed. Result: {refresh_result}")
        return refresh_result
    except Exception as e:
        logger.error(f"Error refreshing medicine names cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/medicine-names/stats", response_model=Dict[str, Any])
async def get_medicine_names_stats():
    """
    Get statistics about the medicine names cache.
    """
    logger.info("Received request for medicine names cache statistics")
    try:
        stats = get_cache_stats()
        logger.info(f"Medicine names cache stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error getting medicine names cache stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/documents/{medicine_name}", response_model=DocumentInfo)
async def get_document_by_name_endpoint(medicine_name: str):
    """
    Get a specific document by medicine name
    """
    logger.info(f"Received request for document: {medicine_name}")
    
    try:
        document = get_document_by_name(medicine_name)
        if document:
            return document
        else:
            raise HTTPException(status_code=404, detail=f"Document not found for medicine: {medicine_name}")
    except Exception as e:
        logger.error(f"Error in get_document_by_name_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    """
    Get list of all documents in the database
    """
    logger.info("Received request for documents list")
    
    try:
        db = get_chroma_db()
        collection = db._collection
        
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
                    doc_info = DocumentInfo(
                        name=metadata.get('h1', '') or 'Unknown',
                        filename=metadata.get('source', '').split('/')[-1] if metadata.get('source') else 'Unknown.md',
                        source=metadata.get('source', ''),
                        h1=metadata.get('h1', ''),
                        h2=metadata.get('h2', ''),
                        content=content
                    )
                    documents.append(doc_info)
        
        return DocumentsResponse(documents=documents, total_count=len(documents))
        
    except Exception as e:
        logger.error(f"Error in get_documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/rag/answer", response_model=RAGResponse)
async def get_rag_answer(request: RAGRequest):
    """
    Get RAG answer for a given question
    """
    logger.info(f"Received RAG request: {request.question}")
    
    try:
        response_text, sources, metadata = query(request.question)
        logger.info("RAG query completed successfully")
        return RAGResponse(response=response_text, sources=sources, metadata=metadata)
    except HTTPException:
        logger.warning("HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_rag_answer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.options("/rag/answer")
async def options_rag_answer():
    """
    Handle CORS preflight request for /rag/answer
    """
    logger.info("OPTIONS request received for /rag/answer")
    return {"message": "CORS preflight handled"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint with cache status
    """
    logger.info("Health check requested")
    
    try:
        # Get cache statistics
        cache_stats = get_cache_stats()
        
        # Check if embeddings instance is available
        embeddings_status = "available" if _embeddings_instance is not None else "not_initialized"
        
        # Check if Chroma directory exists
        chroma_status = "available" if os.path.exists(CHROMA_PATH) else "not_found"
        
        return {
            "status": "healthy",
            "service": "PharmaRAG",
            "timestamp": datetime.now().isoformat(),
            "cache": {
                "enabled": ENABLE_CACHE,
                "status": cache_stats.get("cache_stats", {}).get("hit_rate_percent", 0),
                "size": cache_stats.get("cache_stats", {}).get("current_size", 0)
            },
            "embeddings": embeddings_status,
            "chroma_database": chroma_status,
            "performance": {
                "cache_hit_rate": f"{cache_stats.get('cache_stats', {}).get('hit_rate_percent', 0)}%",
                "total_requests": cache_stats.get("cache_stats", {}).get("total_requests", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}", exc_info=True)
        return {
            "status": "degraded",
            "service": "PharmaRAG",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/cache/invalidate", response_model=Dict[str, str])
async def invalidate_cache():
    """
    Invalidate the medicine names cache
    """
    logger.info("Received request to invalidate medicine names cache")
    try:
        result = invalidate_medicine_names_cache()
        logger.info(f"Cache invalidation completed. Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/cache/refresh", response_model=Dict[str, Any])
async def refresh_cache():
    """
    Force refresh the medicine names cache
    """
    logger.info("Received request to refresh medicine names cache")
    try:
        result = refresh_medicine_names_cache()
        logger.info(f"Cache refresh completed. Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error refreshing cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_statistics():
    """
    Get comprehensive cache statistics and performance metrics
    """
    logger.info("Received request for cache statistics")
    try:
        stats = get_cache_stats()
        logger.info(f"Cache statistics retrieved successfully")
        return stats
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/cache/clear", response_model=Dict[str, str])
async def clear_cache():
    """
    Clear all cache entries
    """
    logger.info("Received request to clear all cache entries")
    try:
        medicine_names_cache.clear()
        logger.info("All cache entries cleared successfully")
        return {"status": "success", "message": "All cache entries cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint with service information
    """
    logger.info("Root endpoint accessed")
    return {
        "service": "PharmaRAG Service",
        "version": "1.0.0",
        "endpoints": {
            "rag_answer": "/rag/answer",
            "health": "/health",
            "medicine_names": "/medicine-names",
            "cache_management": {
                "stats": "/cache/stats",
                "refresh": "/cache/refresh",
                "invalidate": "/cache/invalidate",
                "clear": "/cache/clear"
            },
            "documents": "/documents",
            "document_by_name": "/documents/{medicine_name}"
        },
        "cache_config": {
            "enabled": ENABLE_CACHE,
            "ttl_minutes": CACHE_TTL_MINUTES,
            "max_size": CACHE_MAX_SIZE
        }
    }

if __name__ == "__main__":
    try:
        logger.info("Starting PharmaRAG Service...")
        logger.info(f"Chroma path: {CHROMA_PATH}")
        logger.info(f"Temperature: {TEMPERATURE}")
        
        # Validate environment
        if not API_KEY:
            logger.error("API_KEY not found! Please check your .env file.")
            exit(1)
        
        # Check if Chroma directory exists
        if not os.path.exists(CHROMA_PATH):
            logger.warning(f"Chroma directory {CHROMA_PATH} does not exist. It will be created on first use.")
        
        logger.info("Service will be available at http://0.0.0.0:8000")
        logger.info("CORS is enabled for localhost:3000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}", exc_info=True)
        exit(1)

