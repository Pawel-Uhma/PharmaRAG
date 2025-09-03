"""
Ingestion module for PharmaRAG service.
Handles processing and ingesting markdown files into the data directory.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def clean_filename(filename: str) -> str:
    """
    Clean filename to be safe for filesystem.
    
    Args:
        filename: Raw filename
        
    Returns:
        Cleaned filename safe for filesystem
    """
    # Remove or replace problematic characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores and spaces
    cleaned = cleaned.strip('_ ')
    return cleaned


def extract_medicine_name_from_content(content: str) -> Optional[str]:
    """
    Extract medicine name from markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Medicine name or None if not found
    """
    try:
        # Look for the first h1 heading
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                # Extract the medicine name from h1
                medicine_name = line[2:].strip()
                return clean_filename(medicine_name)
        
        # If no h1 found, try to extract from first line
        if lines:
            first_line = lines[0].strip()
            if first_line:
                return clean_filename(first_line)
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting medicine name: {str(e)}")
        return None


def process_markdown_content(content: str) -> str:
    """
    Process and clean markdown content.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Processed markdown content
    """
    try:
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Ensure proper line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove trailing whitespace
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        content = '\n'.join(cleaned_lines)
        
        return content.strip()
        
    except Exception as e:
        logger.error(f"Error processing markdown content: {str(e)}")
        return content


def save_document_to_data_dir(medicine_name: str, content: str) -> bool:
    """
    Save document to the data directory.
    
    Args:
        medicine_name: Name of the medicine
        content: Markdown content
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Clean the medicine name for filename
        clean_name = clean_filename(medicine_name)
        
        # Create file path
        file_path = os.path.join(DATA_DIR, f"{clean_name}.md")
        
        # Process content
        processed_content = process_markdown_content(content)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        logger.info(f"Saved document: {clean_name} to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving document {medicine_name}: {str(e)}")
        return False


def ingest_markdown_file(file_path: str) -> bool:
    """
    Ingest a single markdown file into the data directory.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract medicine name
        medicine_name = extract_medicine_name_from_content(content)
        if not medicine_name:
            logger.warning(f"Could not extract medicine name from {file_path}")
            return False
        
        # Save to data directory
        return save_document_to_data_dir(medicine_name, content)
        
    except Exception as e:
        logger.error(f"Error ingesting file {file_path}: {str(e)}")
        return False


def ingest_markdown_directory(source_dir: str) -> Dict[str, Any]:
    """
    Ingest all markdown files from a directory.
    
    Args:
        source_dir: Source directory containing markdown files
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Find all markdown files
        md_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        results["total_files"] = len(md_files)
        
        # Process each file
        for file_path in md_files:
            try:
                if ingest_markdown_file(file_path):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to ingest: {file_path}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error processing {file_path}: {str(e)}")
        
        logger.info(f"Ingestion completed: {results['successful']} successful, {results['failed']} failed")
        return results
        
    except Exception as e:
        logger.error(f"Error during directory ingestion: {str(e)}")
        return {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "errors": [str(e)]
        }


def get_data_directory_stats() -> Dict[str, Any]:
    """
    Get statistics about the data directory.
    
    Returns:
        Dictionary with data directory statistics
    """
    try:
        if not os.path.exists(DATA_DIR):
            return {
                "exists": False,
                "file_count": 0,
                "total_size": 0
            }
        
        # Count files and calculate total size
        file_count = 0
        total_size = 0
        
        for file in os.listdir(DATA_DIR):
            if file.endswith('.md'):
                file_path = os.path.join(DATA_DIR, file)
                if os.path.isfile(file_path):
                    file_count += 1
                    total_size += os.path.getsize(file_path)
        
        return {
            "exists": True,
            "file_count": file_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting data directory stats: {str(e)}")
        return {
            "exists": False,
            "error": str(e)
        }
