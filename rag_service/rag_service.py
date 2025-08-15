
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
from typing import List, Optional
import uvicorn
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

CHROMA_PATH = "chroma"
TEMPERATURE = 0.2

API_KEY = os.getenv("API_KEY")

# Log API key status (without exposing the actual key)
if API_KEY:
    logger.info("API_KEY loaded successfully")
else:
    logger.warning("API_KEY not found in environment variables")

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
        logger.info("Initializing OpenAI embeddings...")
        embedding_function = OpenAIEmbeddings(api_key=API_KEY)
        logger.info("Embeddings initialized successfully")
        
        logger.info(f"Loading Chroma database from: {CHROMA_PATH}")
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        logger.info("Chroma database loaded successfully")

        # Search the DB.
        logger.info(f"Searching database with k=3...")
        results = db.similarity_search_with_relevance_scores(query_text, k=3)
        logger.info(f"Found {len(results)} results")
        
        # Log relevance scores
        for i, (doc, score) in enumerate(results):
            logger.info(f"Result {i+1}: score={score:.4f}, source={doc.metadata.get('source', 'unknown')}")
        
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
        model = ChatOpenAI(api_key=API_KEY, temperature=TEMPERATURE)
        logger.info("Model initialized successfully")
        
        logger.info("Generating response...")
        response_text = model.predict(prompt)
        logger.info(f"Response generated, length: {len(response_text)} characters")

        # For cases with no relevant results, we don't have sources
        if has_relevant_results:
            sources = [doc.metadata.get("source", None) for doc, _score in results]
        else:
            sources = []
        logger.info(f"Sources: {sources}")
        
        return response_text, sources
        
    except Exception as e:
        logger.error(f"Error in query function: {str(e)}", exc_info=True)
        raise

@app.post("/rag/answer", response_model=RAGResponse)
async def get_rag_answer(request: RAGRequest):
    """
    Get RAG answer for a given question
    """
    logger.info(f"Received RAG request: {request.question}")
    
    try:
        response_text, sources = query(request.question)
        logger.info("RAG query completed successfully")
        return RAGResponse(response=response_text, sources=sources)
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

