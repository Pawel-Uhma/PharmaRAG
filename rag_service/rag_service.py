"""
PharmaRAG FastAPI Service - Orchestrator

Main FastAPI service that orchestrates RAG functionality using modular components.
"""

import os
import logging
import time
import re
import unicodedata
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our modules
from ask import OpenAIService
from utils.medicine_names_service import MedicineNamesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TEMPERATURE = 0.2

# PostgreSQL configuration
POSTGRES_CONNECTION_STRING = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/pharmarag')
COLLECTION_NAME = "pharma_documents"

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Get API key directly from environment variables (for Docker/App Runner)
API_KEY = os.getenv("API_KEY")

# Log API key status (without exposing the actual key)
if API_KEY:
    logger.info("API_KEY loaded successfully")
else:
    logger.warning("API_KEY not found in environment variables")

def normalize_document_name(name: str) -> str:
    """
    Normalize document name by handling Polish characters and special characters.
    
    Rules:
    - Keep dots (.) and plus signs (+) as they are
    - Convert forward slashes (/) to underscores
    - Replace other non-alphanumeric characters with "_"
    - Normalize Polish characters: ą→a, ć→c, ę→e, ł→l, ń→n, ó→o, ś→s, ź→z, ż→z
    - Remove ł entirely (as per requirement)
    - Convert to lowercase
    
    Args:
        name: Original document name
        
    Returns:
        Normalized document name
    """
    # Polish character mappings (excluding ł which should be removed)
    polish_mappings = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    
    # Apply Polish character mappings first (before any normalization)
    normalized = name
    for polish_char, replacement in polish_mappings.items():
        normalized = normalized.replace(polish_char, replacement)
    
    # Remove ł and Ł entirely
    normalized = normalized.replace('ł', '').replace('Ł', '')
    
    # Now normalize unicode characters (after Polish character replacement)
    normalized = unicodedata.normalize('NFD', normalized)
    
    # Convert forward slashes to underscores first
    normalized = normalized.replace('/', '_')
    
    # Replace all remaining non-alphanumeric characters (except dots and plus signs) with underscore
    normalized = re.sub(r'[^a-zA-Z0-9.+\-]', '_', normalized)
    
    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)
    
    # Remove leading and trailing underscores
    normalized = normalized.strip('_')
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    return normalized

# FastAPI app initialization
app = FastAPI(
    title="PharmaRAG Service",
    description="A RAG service for pharmaceutical information queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add a test endpoint to verify CORS
@app.get("/test-cors")
async def test_cors():
    """
    Test endpoint to verify CORS is working
    """
    return {"message": "CORS is working!", "timestamp": time.time()}

# Pydantic models for request/response
class RAGRequest(BaseModel):
    question: str

class RAGResponse(BaseModel):
    response: str
    sources: List[Optional[str]]
    metadata: List[dict]

class MedicineNamesResponse(BaseModel):
    names: List[str]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class MedicineNamesSearchResponse(BaseModel):
    names: List[str]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class DocumentResponse(BaseModel):
    name: str
    filename: str
    source: Optional[str] = None
    h1: Optional[str] = None
    h2: Optional[str] = None
    content: Optional[str] = None

# Global service instances
openai_service = None
medicine_names_service = None

# Middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code}, time: {process_time:.3f}s")
    
    return response

def initialize_services():
    """Initialize all service components."""
    global openai_service, medicine_names_service
    
    try:
        logger.info("Initializing services...")
        logger.info(f"API_KEY present: {bool(API_KEY)}")
        logger.info(f"API_KEY length: {len(API_KEY) if API_KEY else 0}")
        logger.info(f"API_KEY starts with: {API_KEY[:10] if API_KEY and len(API_KEY) > 10 else 'N/A'}")
        
        if not API_KEY:
            error_msg = "API_KEY not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize OpenAI service
        logger.info("Starting OpenAI service initialization...")
        openai_service = OpenAIService(API_KEY)
        logger.info("OpenAI service initialized successfully")
        
        # Initialize Medicine Names service
        logger.info("Starting Medicine Names service initialization...")
        medicine_names_service = MedicineNamesService()
        logger.info("Medicine Names service initialized successfully")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    initialize_services()

# RAG Endpoints
@app.post("/rag/answer", response_model=RAGResponse)
async def get_rag_answer(request: RAGRequest):
    """
    Get RAG answer for a given question
    """
    logger.info(f"Received RAG request: {request.question}")
    logger.info(f"Request type: {type(request)}")
    logger.info(f"Request question: '{request.question}'")
    
    try:
        # Check if services are initialized
        logger.info(f"OpenAI service status: {openai_service is not None}")
        if not openai_service:
            error_msg = "OpenAI service not initialized"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Check API key
        logger.info(f"API_KEY status: {'Present' if API_KEY else 'Missing'}")
        if not API_KEY:
            error_msg = "API_KEY not found in environment variables"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Validate question
        if not request.question or not request.question.strip():
            error_msg = "Question cannot be empty"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info("Starting RAG query...")
        response_text, sources, metadata = openai_service.query(request.question)
        logger.info(f"RAG query completed successfully. Response length: {len(response_text) if response_text else 0}")
        logger.info(f"Sources count: {len(sources) if sources else 0}")
        logger.info(f"Metadata count: {len(metadata) if metadata else 0}")
        
        return RAGResponse(response=response_text, sources=sources, metadata=metadata)
        
    except HTTPException as he:
        logger.error(f"HTTPException in get_rag_answer: {he.detail} (status: {he.status_code})")
        raise
    except ValueError as ve:
        error_msg = f"Value error in RAG query: {str(ve)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=400, detail=error_msg)
    except ConnectionError as ce:
        error_msg = f"Connection error in RAG query: {str(ce)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except TimeoutError as te:
        error_msg = f"Timeout error in RAG query: {str(te)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        error_msg = f"Unexpected error in get_rag_answer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.options("/rag/answer")
async def options_rag_answer():
    """
    Handle CORS preflight request for /rag/answer
    """
    return {"message": "CORS preflight handled"}

@app.options("/medicine-names/paginated")
async def options_medicine_names_paginated():
    """Handle preflight OPTIONS request for paginated medicine names."""
    return {"message": "OK"}

@app.options("/medicine-names/search")
async def options_medicine_names_search():
    """Handle preflight OPTIONS request for medicine names search."""
    return {"message": "OK"}

@app.options("/documents/{medicine_name}")
async def options_documents(medicine_name: str):
    """Handle preflight OPTIONS request for document endpoint."""
    return {"message": "OK"}

# Medicine Names Endpoints
@app.get("/medicine-names/paginated", response_model=MedicineNamesResponse)
async def get_paginated_medicine_names(page: int = 1, page_size: int = 20):
    """
    Get paginated medicine names
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
    
    Returns:
        Paginated list of medicine names with pagination metadata
    """
    logger.info(f"Received medicine names request: page={page}, page_size={page_size}")
    
    try:
        if not medicine_names_service:
            raise HTTPException(status_code=500, detail="Medicine Names service not initialized")
        
        result = medicine_names_service.get_paginated_names(page=page, page_size=page_size)
        logger.info("Medicine names pagination completed successfully")
        return MedicineNamesResponse(**result)
        
    except HTTPException:
        logger.warning("HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_paginated_medicine_names: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/medicine-names/search", response_model=MedicineNamesSearchResponse)
async def search_medicine_names(query: str, page: int = 1, page_size: int = 20):
    """
    Search medicine names by query with pagination
    
    Args:
        query: Search query string (URL-encoded)
        page: Page number (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
    
    Returns:
        Filtered and paginated list of medicine names with pagination metadata
    """
    # Import urllib.parse for URL decoding
    from urllib.parse import unquote
    
    # Decode the URL-encoded query
    decoded_query = unquote(query)
    
    logger.info(f"Received medicine names search request: original_query='{query}', decoded_query='{decoded_query}', page={page}, page_size={page_size}")
    
    try:
        if not medicine_names_service:
            raise HTTPException(status_code=500, detail="Medicine Names service not initialized")
        
        result = medicine_names_service.search_names(query=decoded_query, page=page, page_size=page_size)
        logger.info("Medicine names search completed successfully")
        return MedicineNamesSearchResponse(**result)
        
    except HTTPException:
        logger.warning("HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_medicine_names: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/medicine-names/count")
async def get_medicine_names_count():
    """
    Get total count of medicine names
    
    Returns:
        Total count of available medicine names
    """
    logger.info("Received medicine names count request")
    
    try:
        if not medicine_names_service:
            raise HTTPException(status_code=500, detail="Medicine Names service not initialized")
        
        count = medicine_names_service.get_total_count()
        logger.info(f"Medicine names count: {count}")
        return {"total_count": count}
        
    except HTTPException:
        logger.warning("HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_medicine_names_count: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Documents Endpoint
@app.get("/documents/{medicine_name}", response_model=DocumentResponse)
async def get_document(medicine_name: str):
    """
    Get document content for a specific medicine name
    
    Args:
        medicine_name: URL-encoded medicine name (path parameter)
    
    Returns:
        Document information including content, metadata, and source
    """
    logger.info(f"Received document request for medicine: {medicine_name}")
    
    try:
        # Import urllib.parse for URL decoding
        from urllib.parse import unquote
        
        # Decode the URL-encoded medicine name and replace underscores with spaces
        decoded_medicine_name = unquote(medicine_name).replace('_', ' ')
        
        # Look for the document file in the data directory
        data_dir = Path("data")
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail="Data directory not found")
        
        # Find the document file that matches the medicine name
        document_file = None
        
        # Normalize the requested medicine name
        normalized_requested_name = normalize_document_name(decoded_medicine_name)
        logger.info(f"Normalized requested name: '{decoded_medicine_name}' -> '{normalized_requested_name}'")
        
        # Match against normalized filenames
        for file_path in data_dir.glob("*.md"):
            # Extract medicine name from filename (remove .md extension and replace underscores with spaces)
            file_medicine_name = file_path.stem.replace('_', ' ')
            
            # Normalize the filename for comparison
            normalized_filename = normalize_document_name(file_medicine_name)
            logger.debug(f"Normalized filename: '{file_medicine_name}' -> '{normalized_filename}'")
            
            # Compare normalized names
            if normalized_filename == normalized_requested_name:
                document_file = file_path
                break
        
        if not document_file:
            raise HTTPException(status_code=404, detail=f"Document not found for medicine: {decoded_medicine_name}")
        
        # Read the document content
        with open(document_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content to extract metadata
        lines = content.split('\n')
        h1 = None
        h2 = None
        source = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and not h1:
                h1 = line[2:].strip()
            elif line.startswith('## ') and not h2:
                h2 = line[3:].strip()
            elif line.startswith('## Źródło') or line.startswith('## Source'):
                # Extract source URL from the next line or from the same line
                if 'http' in line:
                    source = line.split('http')[1].strip()
                    if not source.startswith('s://'):
                        source = 'http' + source
                elif len(lines) > lines.index(line) + 1:
                    next_line = lines[lines.index(line) + 1].strip()
                    if 'http' in next_line:
                        source = next_line.split('http')[1].strip()
                        if not source.startswith('s://'):
                            source = 'http' + source
        
        # Create response object
        document_response = DocumentResponse(
            name=decoded_medicine_name,
            filename=document_file.name,
            source=source,
            h1=h1,
            h2=h2,
            content=content
        )
        
        logger.info(f"Document loaded successfully for: {decoded_medicine_name}")
        return document_response
        
    except HTTPException:
        logger.warning("HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health and Info Endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "PharmaRAG"}

@app.get("/debug/status")
async def debug_status():
    """
    Debug endpoint to check service status
    """
    status = {
        "api_key_present": bool(API_KEY),
        "api_key_length": len(API_KEY) if API_KEY else 0,
        "api_key_prefix": API_KEY[:10] if API_KEY and len(API_KEY) > 10 else "N/A",
        "openai_service_initialized": openai_service is not None,
        "medicine_names_service_initialized": medicine_names_service is not None,
        "postgres_connection": POSTGRES_CONNECTION_STRING,
        "collection_name": COLLECTION_NAME,
        "temperature": TEMPERATURE
    }
    
    if openai_service:
        try:
            # Try to get some basic info about the OpenAI service
            status["openai_service_type"] = type(openai_service).__name__
            status["openai_service_has_embeddings"] = openai_service.embedding_function is not None
            status["openai_service_has_model"] = openai_service.model is not None
            status["openai_service_has_db"] = openai_service.db is not None
        except Exception as e:
            status["openai_service_error"] = str(e)
    
    return status

@app.get("/debug/test-openai")
async def test_openai():
    """
    Test endpoint to verify OpenAI API key works
    """
    try:
        if not API_KEY:
            return {"error": "API_KEY not found"}
        
        # Simple test - just try to create embeddings
        from langchain_openai import OpenAIEmbeddings
        test_embeddings = OpenAIEmbeddings(api_key=API_KEY)
        
        # Try to embed a simple text
        result = test_embeddings.embed_query("test")
        
        return {
            "status": "success",
            "api_key_works": True,
            "embedding_dimension": len(result) if result else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "api_key_works": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.post("/debug/test-simple-rag")
async def test_simple_rag():
    """
    Test endpoint with minimal RAG processing
    """
    try:
        if not openai_service:
            return {"error": "OpenAI service not initialized"}
        
        # Test just the database search without OpenAI call
        logger.info("Testing database search...")
        results = openai_service.db.similarity_search_with_relevance_scores("test question", k=1)
        logger.info(f"Database search successful, found {len(results)} results")
        
        # Test OpenAI model directly
        logger.info("Testing OpenAI model...")
        test_response = openai_service.model.predict("Hello, this is a test.")
        logger.info("OpenAI model test successful")
        
        return {
            "status": "success",
            "database_results": len(results),
            "openai_test": "success",
            "test_response_length": len(test_response) if test_response else 0
        }
        
    except Exception as e:
        logger.error(f"Error in test_simple_rag: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.options("/debug/test-simple-rag")
async def options_test_simple_rag():
    """Handle preflight OPTIONS request for test endpoint."""
    return {"message": "OK"}

@app.get("/debug/postgres-info")
async def debug_postgres_info():
    """
    Debug endpoint to check PostgreSQL database information
    """
    try:
        postgres_info = {
            "connection_string": POSTGRES_CONNECTION_STRING,
            "collection_name": COLLECTION_NAME,
        }
        
        # Check if database is accessible
        if openai_service and openai_service.db:
            try:
                # Try a simple similarity search
                try:
                    test_results = openai_service.db.similarity_search("test", k=1)
                    postgres_info["similarity_search_works"] = True
                    postgres_info["test_search_results"] = len(test_results)
                except Exception as search_error:
                    postgres_info["similarity_search_works"] = False
                    postgres_info["search_error"] = str(search_error)
                
                postgres_info["database_accessible"] = True
                postgres_info["database_type"] = type(openai_service.db).__name__
            except Exception as e:
                postgres_info["database_accessible"] = False
                postgres_info["database_error"] = str(e)
        else:
            postgres_info["database_accessible"] = False
            postgres_info["database_error"] = "OpenAI service or database not initialized"
        
        return postgres_info
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/test-normalize/{text}")
async def test_normalize(text: str):
    """
    Test endpoint to verify document name normalization
    """
    from urllib.parse import unquote
    decoded_text = unquote(text)
    normalized = normalize_document_name(decoded_text)
    return {
        "original": decoded_text,
        "normalized": normalized,
        "examples": {
            "polish_chars": normalize_document_name("ąęćłńóśźż"),
            "special_chars": normalize_document_name("test@#$%^&*()"),
            "spaces_and_dashes": normalize_document_name("test - name with spaces")
        }
    }

@app.get("/")
async def root():
    """
    Root endpoint with service information
    """
    return {
        "service": "PharmaRAG Service",
        "version": "1.0.0",
        "endpoints": {
            "rag_answer": "/rag/answer",
            "medicine_names_paginated": "/medicine-names/paginated",
            "medicine_names_search": "/medicine-names/search",
            "medicine_names_count": "/medicine-names/count",
            "documents": "/documents/{medicineName}",
            "test_normalize": "/test-normalize/{text}",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    try:
        logger.info("Starting PharmaRAG Service...")
        logger.info(f"PostgreSQL connection: {POSTGRES_CONNECTION_STRING}")
        
        # Validate environment
        if not API_KEY:
            logger.error("API_KEY not found! Please check your .env file.")
            exit(1)
        
        logger.info("Service starting on http://0.0.0.0:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}", exc_info=True)
        exit(1)
