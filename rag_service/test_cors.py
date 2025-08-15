#!/usr/bin/env python3
"""
Test script to verify CORS and API functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_cors():
    """Test CORS functionality"""
    print("Testing CORS functionality...")
    
    # Test OPTIONS request (CORS preflight)
    try:
        response = requests.options(f"{BASE_URL}/rag/answer")
        print(f"OPTIONS /rag/answer: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"OPTIONS request failed: {e}")
    
    # Test GET request to test-cors endpoint
    try:
        response = requests.get(f"{BASE_URL}/test-cors")
        print(f"GET /test-cors: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"GET test-cors failed: {e}")
    
    # Test POST request with CORS headers
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
        data = {"question": "What is paracetamol?"}
        response = requests.post(f"{BASE_URL}/rag/answer", 
                               headers=headers, 
                               data=json.dumps(data))
        print(f"POST /rag/answer: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"POST request failed: {e}")

def test_no_relevant_info():
    """Test behavior when no relevant information is found"""
    print("\nTesting no relevant information handling...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
        # Test with a query that should have no relevant results
        data = {"question": "uiesfhesihf"}
        response = requests.post(f"{BASE_URL}/rag/answer", 
                               headers=headers, 
                               data=json.dumps(data))
        print(f"POST /rag/answer (no relevant info): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Sources: {result['sources']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Test failed: {e}")

def test_health():
    """Test health endpoint"""
    print("\nTesting health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    print("PharmaRAG CORS Test")
    print("=" * 30)
    
    test_health()
    test_cors()
    test_no_relevant_info()
    
    print("\nTest completed!")
