"""
OpenAI interaction module for PharmaRAG service.
Handles embeddings, model initialization, and RAG query processing.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from sqlalchemy import create_engine
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

# Constants
TEMPERATURE = 0.2

# PostgreSQL configuration
POSTGRES_CONNECTION_STRING = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/pharmarag')
COLLECTION_NAME = "pharma_documents"

PROMPT_TEMPLATE = """
Odpowiedz na pytanie tylko na podstawie poniższych informacji:
{context}
---
Odpowiedz na pytanie tylko na podstawie kontekstu: {question}

Jeśli w kontekście nie ma istotnych informacji na temat pytania, grzecznie poinformuj o tym użytkownika i zasugeruj, aby zadał pytanie związane z lekami lub farmacją, na które mogę odpowiedzieć na podstawie dostępnych informacji.
"""

class OpenAIService:
    """Service class for OpenAI interactions."""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI service with API key."""
        self.api_key = api_key
        self.embedding_function = None
        self.model = None
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize embeddings, model, and database."""
        try:
            logger.info("Initializing OpenAI embeddings...")
            self.embedding_function = OpenAIEmbeddings(api_key=self.api_key)
            logger.info("Embeddings initialized successfully")
            
            logger.info(f"Loading PostgreSQL database from: {POSTGRES_CONNECTION_STRING}")
            try:
                # Use PostgreSQL with pgvector
                self.db = PGVector(
                    embeddings=self.embedding_function,
                    connection=POSTGRES_CONNECTION_STRING,
                    collection_name=COLLECTION_NAME,
                )
                logger.info("PostgreSQL database loaded successfully")
                
                # Test the database by trying a simple search
                try:
                    # Try a simple similarity search to verify database is working
                    test_results = self.db.similarity_search("test", k=1)
                    logger.info(f"Database test successful, found {len(test_results)} test results")
                except Exception as test_error:
                    logger.warning(f"Database test failed: {str(test_error)}")
                    raise Exception(f"Database test failed: {str(test_error)}")
                    
            except Exception as db_error:
                logger.warning(f"Failed to load existing PostgreSQL database: {str(db_error)}")
                logger.info("Creating new PostgreSQL database...")
                
                # Try to create a new database
                try:
                    self.db = PGVector(
                        embeddings=self.embedding_function,
                        connection=POSTGRES_CONNECTION_STRING,
                        collection_name=COLLECTION_NAME,
                        pre_delete_collection=True,  # Clear existing collection
                    )
                    logger.info("New PostgreSQL database created successfully")
                except Exception as create_error:
                    logger.error(f"Failed to create new PostgreSQL database: {str(create_error)}")
                    raise create_error
            
            logger.info("Initializing ChatOpenAI model...")
            self.model = ChatOpenAI(api_key=self.api_key, temperature=TEMPERATURE)
            logger.info("Model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI service: {str(e)}")
            raise
    
    def query(self, query_text: str) -> Tuple[str, List[Optional[str]], List[Dict]]:
        """
        Process a RAG query and return response with sources and metadata.
        
        Args:
            query_text: The question to answer
            
        Returns:
            Tuple of (response_text, sources, metadata)
        """
        logger.info(f"Processing query: {query_text}")
        
        try:
            # Search the database
            logger.info(f"Searching database with k=3...")
            results = self.db.similarity_search_with_relevance_scores(query_text, k=3)
            logger.info(f"Found {len(results)} results")
            
            # Check if we have any results and if the best score is reasonable
            has_relevant_results = len(results) > 0 and results[0][1] >= 0.7
            
            logger.info(f"Relevance threshold: 0.7, Best score: {results[0][1] if results else 'no results'}")
            
            if not has_relevant_results:
                logger.warning(f"No relevant results found. Best score: {results[0][1] if results else 'no results'}")
                # Create fallback context
                context_text = "Nie znaleziono żadnych istotnych informacji w bazie danych na temat tego zapytania. Baza danych zawiera informacje o lekach i farmacji, ale to konkretne zapytanie nie pasuje do dostępnych danych."
                logger.info("Using fallback context for no relevant results")
            else:
                context_text = self._format_context(results)
                logger.info(f"Context length: {len(context_text)} characters")

            # Generate response
            response_text = self._generate_response(context_text, query_text)
            logger.info(f"Response generated, length: {len(response_text)} characters")

            # Extract sources and metadata
            if has_relevant_results:
                sources = self._extract_sources(results)
                metadata = self._extract_metadata(results)
            else:
                sources = []
                metadata = []
                
            logger.info(f"Sources: {sources}")
            
            return response_text, sources, metadata
            
        except Exception as e:
            logger.error(f"Error in query function: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error args: {e.args}")
            logger.error(f"Database status: {self.db is not None}")
            logger.error(f"Model status: {self.model is not None}")
            logger.error(f"Embedding function status: {self.embedding_function is not None}")
            raise
    
    def _extract_sources(self, results: List[Tuple]) -> List[Optional[str]]:
        """Extract source filenames from search results."""
        sources = []
        for doc, _score in results:
            # Try different metadata fields for source
            source = None
            metadata = doc.metadata
            
            # Check various possible source fields
            if 'source' in metadata and metadata['source']:
                source = metadata['source']
            elif 'path' in metadata and metadata['path']:
                source = metadata['path']
            elif 'doc_id' in metadata and metadata['doc_id']:
                source = metadata['doc_id']
            elif 'filename' in metadata and metadata['filename']:
                source = metadata['filename']
            
            # If source is a full path, extract just the filename
            if source:
                if os.path.sep in source:
                    source = os.path.basename(source)
                # Remove file extension if present
                if '.' in source:
                    source = os.path.splitext(source)[0]
            
            sources.append(source)
        
        # Remove duplicates while preserving order
        unique_sources = []
        seen = set()
        for source in sources:
            if source and source not in seen:
                unique_sources.append(source)
                seen.add(source)
        
        return unique_sources
    
    def _format_context(self, results: List[Tuple]) -> str:
        """Format search results into context text."""
        def _fmt_chunk(doc):
            # Prefer direct h1/h2; fall back to parent_section if stored that way
            ps = doc.metadata.get("parent_section", {}) or {}
            h1 = doc.metadata.get("h1") or ps.get("h1") or ""
            h2 = doc.metadata.get("h2") or ps.get("h2") or ""
            src = doc.metadata.get("source") or doc.metadata.get("path") or doc.metadata.get("doc_id") or ""

            title_parts = [p for p in [h1, h2] if p]
            title = " > ".join(title_parts) if title_parts else "Fragment"

            header_lines = [f"## {title}"]
            if src:
                # Extract filename from path if needed
                if os.path.sep in src:
                    src = os.path.basename(src)
                header_lines.append(f"[Source: {src}]")
            header = "\n".join(header_lines)

            body = doc.page_content.strip()
            return f"{header}\n{body}"

        context_text = "\n\n---\n\n".join([_fmt_chunk(doc) for doc, _score in results])
        return context_text
    
    def _generate_response(self, context_text: str, query_text: str) -> str:
        """Generate response using OpenAI model."""
        try:
            logger.info("Starting response generation...")
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=query_text)
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            # Log the complete prompt sent to OpenAI
            logger.info(f"Complete prompt sent to OpenAI: {prompt}")
            
            logger.info("Calling OpenAI model...")
            response_text = self.model.predict(prompt)
            logger.info(f"OpenAI response received, length: {len(response_text) if response_text else 0}")
            return response_text
            
        except Exception as e:
            logger.error(f"Error in _generate_response: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Model status: {self.model is not None}")
            logger.error(f"API key present: {bool(self.api_key)}")
            raise
    
    def _extract_metadata(self, results: List[Tuple]) -> List[Dict]:
        """Extract metadata from search results."""
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
        return metadata
