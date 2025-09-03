"""
API module for PharmaRAG service.
Handles FastAPI routes and middleware.
"""

import time
import os
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from .config import (
        SERVICE_NAME, SERVICE_VERSION, ALLOWED_ORIGINS, 
        CHROMA_PATH, ENABLE_CACHE, CACHE_TTL_MINUTES, CACHE_MAX_SIZE
    )
    from .models import (
        RAGRequest, RAGResponse, DocumentInfo, DocumentsResponse, 
        MedicineNamesResponse, PaginatedMedicineNamesResponse
    )
    from .rag_core import query
    from .database import (
        get_medicine_names_from_chroma, get_document_by_name, 
        get_documents_from_chroma, _embeddings_instance, get_paginated_medicine_names, search_medicine_names
    )
    from .cache import (
        get_cache_stats, invalidate_medicine_names_cache, 
        refresh_medicine_names_cache, medicine_names_cache
    )
    from .performance_monitor import get_performance_report, reset_performance_stats
except ImportError:
    from config import (
        SERVICE_NAME, SERVICE_VERSION, ALLOWED_ORIGINS, 
        CHROMA_PATH, ENABLE_CACHE, CACHE_TTL_MINUTES, CACHE_MAX_SIZE
    )
    from models import (
        RAGRequest, RAGResponse, DocumentInfo, DocumentsResponse, 
        MedicineNamesResponse, PaginatedMedicineNamesResponse
    )
    from rag_core import query
    from database import (
        get_medicine_names_from_chroma, get_document_by_name, 
        get_documents_from_chroma, _embeddings_instance, get_paginated_medicine_names, search_medicine_names
    )
    from cache import (
        get_cache_stats, invalidate_medicine_names_cache, 
        refresh_medicine_names_cache, medicine_names_cache
    )
    from performance_monitor import get_performance_report, reset_performance_stats

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # FastAPI app initialization
    app = FastAPI(
        title=SERVICE_NAME,
        description="A RAG service for pharmaceutical information queries",
        version=SERVICE_VERSION
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

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

    # Add a test endpoint to verify CORS
    @app.get("/test-cors")
    async def test_cors():
        """Test endpoint to verify CORS is working"""
        logger.info("CORS test endpoint accessed")
        return {"message": "CORS is working!", "timestamp": time.time()}

    @app.get("/medicine-names", response_model=MedicineNamesResponse)
    async def get_medicine_names():
        """Get list of all medicine names (fast, no content)"""
        logger.info("Received request for medicine names")
        
        try:
            names = get_medicine_names_from_chroma()
            return MedicineNamesResponse(names=names, total_count=len(names))
        except Exception as e:
            logger.error(f"Error in get_medicine_names: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.get("/medicine-names/paginated", response_model=PaginatedMedicineNamesResponse)
    async def get_paginated_medicine_names_endpoint(page: int = 1, page_size: int = 20):
        """Get paginated list of medicine names"""
        logger.info(f"Received request for paginated medicine names (page {page}, size {page_size})")
        
        try:
            # Validate parameters
            if page < 1:
                raise HTTPException(status_code=400, detail="Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
            
            names, total_count, total_pages, has_next, has_previous = get_paginated_medicine_names(page, page_size)
            
            return PaginatedMedicineNamesResponse(
                names=names,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_paginated_medicine_names_endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.get("/medicine-names/search", response_model=PaginatedMedicineNamesResponse)
    async def search_medicine_names_endpoint(query: str, page: int = 1, page_size: int = 20):
        """Search medicine names across all medicines"""
        logger.info(f"Received search request for medicine names: '{query}' (page {page}, size {page_size})")
        
        try:
            # Validate parameters
            if page < 1:
                raise HTTPException(status_code=400, detail="Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
            if not query or not query.strip():
                raise HTTPException(status_code=400, detail="Search query cannot be empty")
            
            names, total_count, total_pages, has_next, has_previous = search_medicine_names(query, page, page_size)
            
            return PaginatedMedicineNamesResponse(
                names=names,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_medicine_names_endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.post("/medicine-names/refresh", response_model=Dict[str, Any])
    async def refresh_medicine_names():
        """Force refresh the list of medicine names in the cache."""
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
        """Get statistics about the medicine names cache."""
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
        """Get a specific document by medicine name"""
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
        """Get list of all documents in the database"""
        logger.info("Received request for documents list")
        
        try:
            documents = get_documents_from_chroma()
            return DocumentsResponse(documents=documents, total_count=len(documents))
        except Exception as e:
            logger.error(f"Error in get_documents: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.post("/rag/answer", response_model=RAGResponse)
    async def get_rag_answer(request: RAGRequest):
        """Get RAG answer for a given question"""
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
        """Handle CORS preflight request for /rag/answer"""
        logger.info("OPTIONS request received for /rag/answer")
        return {"message": "CORS preflight handled"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint with cache status"""
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
                "service": SERVICE_NAME,
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
                "service": SERVICE_NAME,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    @app.post("/cache/invalidate", response_model=Dict[str, str])
    async def invalidate_cache():
        """Invalidate the medicine names cache"""
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
        """Force refresh the medicine names cache"""
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
        """Get comprehensive cache statistics and performance metrics"""
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
        """Clear all cache entries"""
        logger.info("Received request to clear all cache entries")
        try:
            medicine_names_cache.clear()
            logger.info("All cache entries cleared successfully")
            return {"status": "success", "message": "All cache entries cleared successfully"}
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.get("/performance/report", response_model=Dict[str, Any])
    async def get_performance_metrics():
        """Get comprehensive performance metrics and insights"""
        logger.info("Received request for performance metrics")
        try:
            report = get_performance_report()
            logger.info("Performance report generated successfully")
            return report
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.post("/performance/reset", response_model=Dict[str, str])
    async def reset_performance_metrics():
        """Reset all performance statistics"""
        logger.info("Received request to reset performance metrics")
        try:
            result = reset_performance_stats()
            logger.info("Performance metrics reset successfully")
            return result
        except Exception as e:
            logger.error(f"Error resetting performance metrics: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        logger.info("Root endpoint accessed")
        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
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
                "performance_management": {
                    "report": "/performance/report",
                    "reset": "/performance/reset"
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

    return app
