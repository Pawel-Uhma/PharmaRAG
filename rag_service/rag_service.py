"""
PharmaRAG FastAPI Service - Orchestrator

Main FastAPI service that orchestrates RAG functionality using modular components.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our modules
from ask import OpenAIService
from medicine_names_service import MedicineNamesService
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CHROMA_PATH = "chroma"
TEMPERATURE = 0.2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key
API_KEY = os.getenv("API_KEY")

# Log API key status (without exposing the actual key)
if API_KEY:
    logger.info("API_KEY loaded successfully")
else:
    logger.warning("API_KEY not found in environment variables")

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
        
        if not API_KEY:
            raise ValueError("API_KEY not found in environment variables")
        
        # Initialize OpenAI service
        openai_service = OpenAIService(API_KEY)
        logger.info("OpenAI service initialized")
        
        # Initialize Medicine Names service
        medicine_names_service = MedicineNamesService()
        logger.info("Medicine Names service initialized")
        
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
    
    try:
        if not openai_service:
            raise HTTPException(status_code=500, detail="OpenAI service not initialized")
        
        response_text, sources, metadata = openai_service.query(request.question)
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
    return {"message": "CORS preflight handled"}

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
        query: Search query string
        page: Page number (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
    
    Returns:
        Filtered and paginated list of medicine names with pagination metadata
    """
    logger.info(f"Received medicine names search request: query='{query}', page={page}, page_size={page_size}")
    
    try:
        if not medicine_names_service:
            raise HTTPException(status_code=500, detail="Medicine Names service not initialized")
        
        result = medicine_names_service.search_names(query=query, page=page, page_size=page_size)
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
        
        # Normalize both names for comparison (remove Polish characters, convert to lowercase)
        def normalize_name(name):
            """Normalize name by removing Polish characters and converting to lowercase"""
            # Polish character mapping
            polish_map = {
                'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
                'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
                'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
            }
            
            # Convert to lowercase first
            normalized = name.lower()
            
            # Replace Polish characters
            for polish_char, latin_char in polish_map.items():
                normalized = normalized.replace(polish_char, latin_char)
            
            # Remove % character (common in medicine names)
            normalized = normalized.replace('%', '')
            
            # Remove + character (common in medicine names like D3+K2)
            normalized = normalized.replace('+', '')
            
            return normalized
        
        def create_variants(name):
            """Create multiple variants of a name for flexible matching"""
            variants = []
            
            # Original name
            variants.append(name.lower())
            
            # Normalized name (without Polish characters, % and +)
            variants.append(normalize_name(name))
            
            # Variant with Polish characters converted to Latin
            polish_to_latin = name.lower()
            polish_map = {
                'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
                'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'
            }
            for polish_char, latin_char in polish_map.items():
                polish_to_latin = polish_to_latin.replace(polish_char, latin_char)
            variants.append(polish_to_latin)
            
            # Variant with Polish characters converted to Latin and + removed
            polish_to_latin_no_plus = polish_to_latin.replace('+', '')
            variants.append(polish_to_latin_no_plus)
            
            # Variant with Polish characters converted to Latin, + removed, and % removed
            polish_to_latin_no_plus_no_percent = polish_to_latin_no_plus.replace('%', '')
            variants.append(polish_to_latin_no_plus_no_percent)
            
            return list(set(variants))  # Remove duplicates
        
        decoded_variants = create_variants(decoded_medicine_name)
        
        for file_path in data_dir.glob("*.md"):
            # Extract medicine name from filename (remove .md extension and replace underscores)
            file_medicine_name = file_path.stem.replace('_', ' ')
            file_variants = create_variants(file_medicine_name)
            
            # Check if any variants match
            for decoded_variant in decoded_variants:
                for file_variant in file_variants:
                    if decoded_variant == file_variant:
                        document_file = file_path
                        break
                if document_file:
                    break
            if document_file:
                break
        
        # If still not found, try exact matching with underscores
        if not document_file:
            underscore_medicine_name = decoded_medicine_name.replace(' ', '_')
            for file_path in data_dir.glob("*.md"):
                file_medicine_name = file_path.stem
                
                # Check if the medicine name matches (case-insensitive)
                if file_medicine_name.lower() == underscore_medicine_name.lower():
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
            "health": "/health"
        }
    }

if __name__ == "__main__":
    try:
        logger.info("Starting PharmaRAG Service...")
        logger.info(f"Chroma path: {CHROMA_PATH}")
        
        # Validate environment
        if not API_KEY:
            logger.error("API_KEY not found! Please check your .env file.")
            exit(1)
        
        # Check if Chroma directory exists
        if not os.path.exists(CHROMA_PATH):
            logger.warning(f"Chroma directory {CHROMA_PATH} does not exist. It will be created on first use.")
        
        logger.info("Service starting on http://0.0.0.0:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}", exc_info=True)
        exit(1)
