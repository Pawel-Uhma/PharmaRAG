"""
Test script for Medicine Names endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_medicine_names_endpoints():
    """Test all medicine names endpoints."""
    
    print("Testing Medicine Names Endpoints")
    print("=" * 40)
    
    # Test 1: Get paginated names
    print("\n1. Testing /medicine-names/paginated")
    try:
        response = requests.get(f"{BASE_URL}/medicine-names/paginated?page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Got {len(data['names'])} names")
            print(f"   Pagination: page {data['pagination']['page']} of {data['pagination']['total_pages']}")
            print(f"   Sample names: {data['names'][:3]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Search names
    print("\n2. Testing /medicine-names/search")
    try:
        response = requests.get(f"{BASE_URL}/medicine-names/search?query=aspirin&page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {data['pagination']['total_items']} results for 'aspirin'")
            print(f"   Sample results: {data['names'][:3]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Get total count
    print("\n3. Testing /medicine-names/count")
    try:
        response = requests.get(f"{BASE_URL}/medicine-names/count")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Total count is {data['total_count']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 4: Test pagination with different page sizes
    print("\n4. Testing pagination with different page sizes")
    try:
        response = requests.get(f"{BASE_URL}/medicine-names/paginated?page=2&page_size=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Page 2 with 10 items - got {len(data['names'])} names")
            print(f"   Pagination info: {data['pagination']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_medicine_names_endpoints()
