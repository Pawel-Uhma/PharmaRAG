#!/bin/bash

# Frontend Medicine Names Update Script
# This script updates the static medicine names data in the frontend

echo "🔄 Frontend Medicine Names Update"
echo "=================================="

# Check if we're in the right directory
if [ ! -d "public" ]; then
    echo "❌ Error: Please run this script from the rag_web directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: rag_web/"
    exit 1
fi

# Check if rag_service directory exists
if [ ! -d "../rag_service" ]; then
    echo "❌ Error: rag_service directory not found"
    echo "   Expected: ../rag_service/"
    exit 1
fi

echo "📊 Extracting medicine names from database..."
cd ../rag_service

# Run the extraction script
python extract_medicine_names.py

if [ $? -eq 0 ]; then
    echo "✅ Medicine names extracted successfully!"
    
    # Copy to frontend
    echo "📁 Copying to frontend..."
    cp medicine_names_minimal.json ../rag_web/public/
    
    if [ $? -eq 0 ]; then
        echo "✅ Frontend updated successfully!"
        echo ""
        echo "📋 Update completed:"
        echo "  - medicine_names_minimal.json copied to public folder"
        echo "  - Frontend will now use updated data"
        echo ""
        echo "💡 Next steps:"
        echo "  1. Restart your frontend development server"
        echo "  2. Test the library view - should show updated data"
        echo "  3. Verify instant loading performance"
    else
        echo "❌ Error copying file to frontend"
        exit 1
    fi
    
else
    echo "❌ Error: Failed to extract medicine names"
    echo "   Please check the error messages above"
    exit 1
fi
