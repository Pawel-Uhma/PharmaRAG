#!/usr/bin/env python3
"""
Script to extract all unique h1 values from Chroma database and save them to medicine_names_minimal.json
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import Set, List

# Constants
CHROMA_DB_PATH = "chroma/chroma.sqlite3"
JSON_FILE_PATH = "medicine_names_minimal.json"

def extract_h1_values_from_chroma() -> Set[str]:
    """
    Extract all unique h1 values from the Chroma SQLite database.
    
    Returns:
        Set of unique h1 values
    """
    print("Connecting to Chroma SQLite database...")
    
    if not os.path.exists(CHROMA_DB_PATH):
        raise FileNotFoundError(f"Chroma database not found at {CHROMA_DB_PATH}")
    
    h1_values = set()
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(CHROMA_DB_PATH)
        cursor = conn.cursor()
        
        # Query to get all unique h1 values from the embedding_metadata table
        # Chroma stores metadata as key-value pairs in embedding_metadata table
        query = """
        SELECT DISTINCT string_value as h1_value
        FROM embedding_metadata
        WHERE key = 'h1' 
        AND string_value IS NOT NULL 
        AND string_value != ''
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            h1_value = row[0]
            if h1_value and h1_value.strip():
                h1_values.add(h1_value.strip())
        
        print(f"Found {len(h1_values)} unique h1 values from database")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
    
    return h1_values

def load_existing_json() -> dict:
    """
    Load the existing medicine_names_minimal.json file.
    
    Returns:
        Dictionary containing the JSON data
    """
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Create new structure if file doesn't exist
        return {"names": []}

def save_json_with_h1_values(h1_values: Set[str], json_data: dict) -> None:
    """
    Save the h1 values to the names field in the JSON file.
    
    Args:
        h1_values: Set of unique h1 values
        json_data: Existing JSON data
    """
    # Convert set to sorted list for consistent ordering
    h1_list = sorted(list(h1_values))
    
    # Update the names field
    json_data["names"] = h1_list
    
    # Save to file
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(h1_list)} h1 values to {JSON_FILE_PATH}")

def main():
    """Main function to extract h1 values and update JSON file."""
    try:
        # Check if Chroma database exists
        if not os.path.exists(CHROMA_DB_PATH):
            print(f"Error: Chroma database not found at {CHROMA_DB_PATH}")
            print("Please ensure the Chroma database exists before running this script.")
            return
        
        # Extract h1 values from Chroma
        h1_values = extract_h1_values_from_chroma()
        
        if not h1_values:
            print("No h1 values found in the Chroma database")
            return
        
        # Load existing JSON data
        json_data = load_existing_json()
        
        # Save h1 values to JSON
        save_json_with_h1_values(h1_values, json_data)
        
        print("Script completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()