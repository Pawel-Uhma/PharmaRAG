"""
Medicine Names Service

Service for handling paginated medicine names from the JSON file.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MedicineNamesService:
    """Service for handling medicine names with pagination."""
    
    def __init__(self, json_file_path: str = "medicine_names_minimal.json"):
        """
        Initialize the MedicineNamesService.
        
        Args:
            json_file_path: Path to the JSON file containing medicine names
        """
        self.json_file_path = json_file_path
        self._medicine_names = None
        self._total_count = 0
        self._load_medicine_names()
    
    def _load_medicine_names(self):
        """Load medicine names from the JSON file."""
        try:
            file_path = Path(self.json_file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Medicine names file not found: {self.json_file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            self._medicine_names = data.get("names", [])
            self._total_count = data.get("total_count", len(self._medicine_names))
            
            logger.info(f"Loaded {len(self._medicine_names)} medicine names from {self.json_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading medicine names: {str(e)}")
            self._medicine_names = []
            self._total_count = 0
            raise
    
    def get_paginated_names(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get paginated medicine names.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary containing paginated data with names, pagination info, and total count
        """
        try:
            if not self._medicine_names:
                raise ValueError("Medicine names not loaded")
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20
            if page_size > 100:  # Limit page size to prevent performance issues
                page_size = 100
            
            # Calculate pagination
            total_items = len(self._medicine_names)
            total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
            
            # Adjust page if it exceeds total pages
            if page > total_pages:
                page = total_pages if total_pages > 0 else 1
            
            # Calculate start and end indices
            start_index = (page - 1) * page_size
            end_index = min(start_index + page_size, total_items)
            
            # Get the slice of names for the current page
            page_names = self._medicine_names[start_index:end_index]
            
            # Build response
            response = {
                "names": page_names,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }
            
            logger.info(f"Returning page {page} of {total_pages} with {len(page_names)} items")
            return response
            
        except Exception as e:
            logger.error(f"Error getting paginated names: {str(e)}")
            raise
    
    def get_total_count(self) -> int:
        """Get the total count of medicine names."""
        return self._total_count
    
    def search_names(self, query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Search medicine names by query with pagination.
        
        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary containing filtered and paginated data
        """
        try:
            if not self._medicine_names:
                raise ValueError("Medicine names not loaded")
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20
            if page_size > 100:
                page_size = 100
            
            # Filter names by query (case-insensitive)
            query_lower = query.lower()
            filtered_names = [
                name for name in self._medicine_names 
                if query_lower in name.lower()
            ]
            
            total_items = len(filtered_names)
            total_pages = (total_items + page_size - 1) // page_size
            
            # Adjust page if it exceeds total pages
            if page > total_pages:
                page = total_pages if total_pages > 0 else 1
            
            # Calculate start and end indices
            start_index = (page - 1) * page_size
            end_index = min(start_index + page_size, total_items)
            
            # Get the slice of filtered names for the current page
            page_names = filtered_names[start_index:end_index]
            
            # Build response
            response = {
                "names": page_names,
                "query": query,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }
            
            logger.info(f"Search '{query}' returned {total_items} results, showing page {page} of {total_pages}")
            return response
            
        except Exception as e:
            logger.error(f"Error searching names: {str(e)}")
            raise
