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
    logger.info("CORS test endpoint accessed")
    return {"message": "CORS is working!", "timestamp": time.time()}

# Pydantic models for request/response
class RAGRequest(BaseModel):
    question: str

class RAGResponse(BaseModel):
    response: str
    sources: List[Optional[str]]
    metadata: List[dict]

# Global service instances
openai_service = None

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

def initialize_services():
    """Initialize all service components."""
    global openai_service
    
    try:
        logger.info("Initializing services...")
        
        if not API_KEY:
            raise ValueError("API_KEY not found in environment variables")
        
        # Initialize OpenAI service
        openai_service = OpenAIService(API_KEY)
        logger.info("OpenAI service initialized")
        
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
    logger.info("OPTIONS request received for /rag/answer")
    return {"message": "CORS preflight handled"}

# Health and Info Endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.info("Health check requested")
    return {"status": "healthy", "service": "PharmaRAG"}

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
        
        logger.info("Service will be available at http://0.0.0.0:8000")
        logger.info("CORS is enabled for localhost:3000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}", exc_info=True)
        exit(1)
