#!/usr/bin/env python3
"""
Extract medicine names from Chroma database and save as static JSON
This creates a frontend-optimized file for instant loading
"""

import json
import os
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def extract_medicine_names():
    """Extract all medicine names from Chroma database"""
    print("🔍 Extracting medicine names from Chroma database...")
    
    try:
        # Initialize embeddings
        api_key = os.getenv("API_KEY")
        if not api_key:
            print("❌ API_KEY not found in environment variables")
            return
        
        embedding_function = OpenAIEmbeddings(api_key=api_key)
        
        # Load Chroma database
        chroma_path = "chroma"
        if not os.path.exists(chroma_path):
            print(f"❌ Chroma directory {chroma_path} not found")
            return
        
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)
        collection = db._collection
        
        # Get all documents metadata
        print("📊 Fetching metadata from database...")
        results = collection.get(include=['metadatas'])
        
        names = []
        if results and 'metadatas' in results and results['metadatas']:
            for metadata in results['metadatas']:
                if metadata and isinstance(metadata, dict):
                    name = metadata.get('h1', '')
                    if name and isinstance(name, str) and name.strip():
                        names.append(name.strip())
        
        # Remove duplicates and sort
        unique_names = sorted(list(set(names)))
        
        print(f"✅ Found {len(unique_names)} unique medicine names")
        
        # Create the data structure
        medicine_data = {
            "metadata": {
                "total_count": len(unique_names),
                "extracted_at": "2024-01-15T00:00:00Z",
                "source": "Chroma Database",
                "version": "1.0"
            },
            "names": unique_names
        }
        
        # Save to JSON file
        output_file = "medicine_names_static.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(medicine_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(unique_names)} names to {output_file}")
        print(f"📁 File size: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        # Also create a minimal version for frontend
        minimal_data = {
            "names": unique_names,
            "total_count": len(unique_names)
        }
        
        minimal_file = "medicine_names_minimal.json"
        with open(minimal_file, 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved minimal version to {minimal_file}")
        print(f"📁 Minimal file size: {os.path.getsize(minimal_file) / 1024:.2f} KB")
        
        # Show sample names
        print(f"\n📋 Sample names (first 10):")
        for i, name in enumerate(unique_names[:10]):
            print(f"  {i+1}. {name}")
        
        if len(unique_names) > 10:
            print(f"  ... and {len(unique_names) - 10} more")
        
        return unique_names
        
    except Exception as e:
        print(f"❌ Error extracting medicine names: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_frontend_files():
    """Create frontend-optimized files"""
    print("\n🌐 Creating frontend-optimized files...")
    
    try:
        # Create a TypeScript interface file
        ts_interface = """// Medicine names data structure
export interface MedicineNamesData {
  names: string[];
  total_count: number;
}

export interface MedicineNamesMetadata {
  total_count: number;
  extracted_at: string;
  source: string;
  version: string;
}

export interface MedicineNamesFullData {
  metadata: MedicineNamesMetadata;
  names: string[];
}
"""
        
        with open("medicine_names_types.ts", 'w', encoding='utf-8') as f:
            f.write(ts_interface)
        
        print("✅ Created TypeScript interface file")
        
        # Create a React hook for loading medicine names
        react_hook = """import { useState, useEffect } from 'react';
import { MedicineNamesData } from './medicine_names_types';

export const useMedicineNames = () => {
  const [names, setNames] = useState<string[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMedicineNames = async () => {
      try {
        setLoading(true);
        // Load from static JSON file
        const response = await fetch('/medicine_names_minimal.json');
        if (!response.ok) {
          throw new Error('Failed to load medicine names');
        }
        
        const data: MedicineNamesData = await response.json();
        setNames(data.names);
        setTotalCount(data.total_count);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error loading medicine names:', err);
      } finally {
        setLoading(false);
      }
    };

    loadMedicineNames();
  }, []);

  return { names, totalCount, loading, error };
};
"""
        
        with open("useMedicineNames.ts", 'w', encoding='utf-8') as f:
            f.write(react_hook)
        
        print("✅ Created React hook file")
        
        # Create a simple HTML demo
        html_demo = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medicine Names Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .loading { color: #666; }
        .error { color: #d32f2f; }
        .names-list { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }
        .name-item { padding: 5px 0; border-bottom: 1px solid #eee; }
        .stats { background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Medicine Names Demo</h1>
        <div id="content">
            <div class="loading">Loading medicine names...</div>
        </div>
    </div>

    <script>
        async function loadMedicineNames() {
            try {
                const response = await fetch('/medicine_names_minimal.json');
                if (!response.ok) {
                    throw new Error('Failed to load medicine names');
                }
                
                const data = await response.json();
                displayMedicineNames(data);
            } catch (error) {
                displayError(error.message);
            }
        }

        function displayMedicineNames(data) {
            const content = document.getElementById('content');
            
            const statsHtml = `
                <div class="stats">
                    <h3>Statistics</h3>
                    <p><strong>Total names:</strong> ${data.total_count}</p>
                    <p><strong>Loaded from:</strong> Static JSON file</p>
                    <p><strong>Loading time:</strong> Instant (no API call)</p>
                </div>
            `;
            
            const namesHtml = `
                <h3>Medicine Names (${data.names.length})</h3>
                <div class="names-list">
                    ${data.names.map(name => `<div class="name-item">${name}</div>`).join('')}
                </div>
            `;
            
            content.innerHTML = statsHtml + namesHtml;
        }

        function displayError(message) {
            const content = document.getElementById('content');
            content.innerHTML = `<div class="error">Error: ${message}</div>`;
        }

        // Load medicine names when page loads
        loadMedicineNames();
    </script>
</body>
</html>
"""
        
        with open("medicine_names_demo.html", 'w', encoding='utf-8') as f:
            f.write(html_demo)
        
        print("✅ Created HTML demo file")
        
    except Exception as e:
        print(f"❌ Error creating frontend files: {str(e)}")

if __name__ == "__main__":
    print("🚀 Medicine Names Extractor")
    print("=" * 40)
    
    # Extract medicine names
    names = extract_medicine_names()
    
    if names:
        # Create frontend files
        create_frontend_files()
        
        print("\n🎉 Extraction completed successfully!")
        print("\n📁 Generated files:")
        print("  - medicine_names_static.json (full data)")
        print("  - medicine_names_minimal.json (frontend optimized)")
        print("  - medicine_names_types.ts (TypeScript types)")
        print("  - useMedicineNames.ts (React hook)")
        print("  - medicine_names_demo.html (HTML demo)")
        
        print("\n💡 Next steps:")
        print("  1. Copy medicine_names_minimal.json to your frontend public folder")
        print("  2. Use the React hook or load directly with fetch()")
        print("  3. Update your frontend to use the static data instead of API calls")
        
    else:
        print("\n❌ Extraction failed. Please check the error messages above.")
