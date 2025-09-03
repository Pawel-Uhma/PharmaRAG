"""
RAG core module for PharmaRAG service.
Handles the core RAG functionality with simplified query logic.
"""

import logging
from typing import Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

try:
    from .config import API_KEY, TEMPERATURE, MODEL
    from .database import get_chroma_db, get_embeddings_instance
except ImportError:
    from config import API_KEY, TEMPERATURE, MODEL
    from database import get_chroma_db, get_embeddings_instance

logger = logging.getLogger(__name__)

# Prompt template for RAG responses
PROMPT_TEMPLATE = """
Odpowiedz na pytanie tylko na podstawie poniższych informacji:
{context}
---
Odpowiedz na pytanie tylko na podstawie powyższego kontekstu: {question}

Jeśli w kontekście nie ma istotnych informacji na temat pytania, grzecznie poinformuj o tym użytkownika i zasugeruj, aby zadał pytanie związane z lekami lub farmacją, na które mogę odpowiedzieć na podstawie dostępnych informacji.
"""


def query(query_text: str) -> Tuple[str, List[Optional[str]], List[dict]]:
    """
    Process a RAG query with simplified logic (no medicine name expansion).
    
    Args:
        query_text: The user's question
        
    Returns:
        Tuple of (response_text, sources, metadata)
    """
    logger.info(f"Processing query: {query_text}")
    
    try:
        # Prepare the DB
        logger.info("Getting OpenAI embeddings instance...")
        embedding_function = get_embeddings_instance()
        logger.info("Embeddings instance retrieved successfully")
        
        logger.info(f"Loading Chroma database...")
        db = get_chroma_db()
        logger.info("Chroma database loaded successfully")

        # Search the DB with the original query (no expansion)
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
