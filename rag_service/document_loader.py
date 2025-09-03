"""
Document loader module for PharmaRAG service.
Handles pagination and document retrieval from Chroma database.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

# Constants
CHROMA_PATH = "chroma"
DEFAULT_PAGE_SIZE = 20

class DocumentLoader:
    """Service class for document loading and pagination."""
    
    def __init__(self, api_key: str):
        """Initialize document loader with API key."""
        self.api_key = api_key
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        try:
            logger.info("Initializing document loader...")
            embedding_function = OpenAIEmbeddings(api_key=self.api_key)
            self.db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
            logger.info("Document loader initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing document loader: {str(e)}")
            raise
    
    def get_medicine_names_paginated(self, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        """
        Get paginated list of medicine names.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary with pagination info and medicine names
        """
        try:
            logger.info(f"Getting medicine names: page={page}, page_size={page_size}")
            
            # Get all documents from the database
            all_docs = self.db.get()
            
            if not all_docs or not all_docs['documents']:
                logger.warning("No documents found in database")
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False
                }
            
            # Extract unique medicine names from metadata
            medicine_names = set()
            for metadata in all_docs['metadatas']:
                if metadata and 'h1' in metadata and metadata['h1']:
                    medicine_names.add(metadata['h1'])
            
            # Convert to sorted list
            medicine_names_list = sorted(list(medicine_names))
            total_count = len(medicine_names_list)
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Validate page number
            if page < 1:
                page = 1
            if page > total_pages:
                page = total_pages
            
            # Get items for current page
            page_items = medicine_names_list[start_index:end_index]
            
            # Build response
            response = {
                "items": page_items,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
            
            logger.info(f"Returning {len(page_items)} medicine names (page {page} of {total_pages})")
            return response
            
        except Exception as e:
            logger.error(f"Error getting medicine names: {str(e)}")
            raise
    
    def get_medicine_names_all(self) -> List[str]:
        """
        Get all medicine names without pagination.
        
        Returns:
            List of all medicine names
        """
        try:
            logger.info("Getting all medicine names")
            
            # Get all documents from the database
            all_docs = self.db.get()
            
            if not all_docs or not all_docs['documents']:
                logger.warning("No documents found in database")
                return []
            
            # Extract unique medicine names from metadata
            medicine_names = set()
            for metadata in all_docs['metadatas']:
                if metadata and 'h1' in metadata and metadata['h1']:
                    medicine_names.add(metadata['h1'])
            
            # Convert to sorted list
            medicine_names_list = sorted(list(medicine_names))
            
            logger.info(f"Found {len(medicine_names_list)} unique medicine names")
            return medicine_names_list
            
        except Exception as e:
            logger.error(f"Error getting all medicine names: {str(e)}")
            raise
    
    def search_medicines(self, query: str, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        """
        Search medicines by name with pagination.
        
        Args:
            query: Search query
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary with pagination info and search results
        """
        try:
            logger.info(f"Searching medicines: query='{query}', page={page}, page_size={page_size}")
            
            # Search the database
            results = self.db.similarity_search_with_relevance_scores(query, k=100)  # Get more results for pagination
            
            if not results:
                logger.info("No search results found")
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                    "query": query
                }
            
            # Extract medicine names from results
            medicine_results = []
            for doc, score in results:
                if doc.metadata and 'h1' in doc.metadata and doc.metadata['h1']:
                    medicine_results.append({
                        "name": doc.metadata['h1'],
                        "h2": doc.metadata.get('h2', ''),
                        "source": doc.metadata.get('source', ''),
                        "relevance_score": score,
                        "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    })
            
            # Remove duplicates based on name
            unique_results = []
            seen_names = set()
            for result in medicine_results:
                if result['name'] not in seen_names:
                    unique_results.append(result)
                    seen_names.add(result['name'])
            
            total_count = len(unique_results)
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Validate page number
            if page < 1:
                page = 1
            if page > total_pages:
                page = total_pages
            
            # Get items for current page
            page_items = unique_results[start_index:end_index]
            
            # Build response
            response = {
                "items": page_items,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "query": query
            }
            
            logger.info(f"Returning {len(page_items)} search results (page {page} of {total_pages})")
            return response
            
        except Exception as e:
            logger.error(f"Error searching medicines: {str(e)}")
            raise
    
    def get_medicine_details(self, medicine_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific medicine.
        
        Args:
            medicine_name: Name of the medicine
            
        Returns:
            Dictionary with medicine details
        """
        try:
            logger.info(f"Getting details for medicine: {medicine_name}")
            
            # Search for the specific medicine
            results = self.db.similarity_search_with_relevance_scores(medicine_name, k=10)
            
            if not results:
                logger.warning(f"No details found for medicine: {medicine_name}")
                return {
                    "name": medicine_name,
                    "details": [],
                    "total_sections": 0
                }
            
            # Filter results for the specific medicine
            medicine_details = []
            for doc, score in results:
                if doc.metadata and 'h1' in doc.metadata and doc.metadata['h1'] == medicine_name:
                    detail = {
                        "h2": doc.metadata.get('h2', ''),
                        "content": doc.page_content,
                        "source": doc.metadata.get('source', ''),
                        "relevance_score": score
                    }
                    medicine_details.append(detail)
            
            # Sort by relevance score
            medicine_details.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            response = {
                "name": medicine_name,
                "details": medicine_details,
                "total_sections": len(medicine_details)
            }
            
            logger.info(f"Found {len(medicine_details)} sections for {medicine_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting medicine details: {str(e)}")
            raise
