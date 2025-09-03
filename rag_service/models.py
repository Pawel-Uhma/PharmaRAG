"""
Pydantic models for PharmaRAG service.
Defines request/response schemas for the API.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RAGRequest(BaseModel):
    """Request model for RAG queries."""
    question: str


class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    response: str
    sources: List[Optional[str]]
    metadata: List[dict]  # Metadata including h1 and h2


class DocumentInfo(BaseModel):
    """Model for document information."""
    name: str
    filename: str
    source: Optional[str]
    h1: Optional[str]
    h2: Optional[str]
    content: Optional[str]


class DocumentsResponse(BaseModel):
    """Response model for documents list."""
    documents: List[DocumentInfo]
    total_count: int


class MedicineNamesResponse(BaseModel):
    """Response model for medicine names list."""
    names: List[str]
    total_count: int


class PaginatedMedicineNamesResponse(BaseModel):
    """Response model for paginated medicine names list."""
    names: List[str]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
