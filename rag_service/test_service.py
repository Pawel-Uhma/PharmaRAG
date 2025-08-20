import requests
import json

# Test the FastAPI service
def test_rag_service():
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Service not running. Start the service first with: python rag_service.py")
        return
    
    # Test root endpoint
    print("\nTesting root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Root: {response.status_code} - {response.json()}")
    
    # Test RAG answer endpoint
    print("\nTesting RAG answer endpoint...")
    test_question = "Jakie są skutki uboczne metforminy?"
    
    payload = {
        "question": test_question
    }
    
    try:
        response = requests.post(
            f"{base_url}/rag/answer",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"RAG Answer: {response.status_code}")
            print(f"Response: {result['response']}")
            print(f"Sources: {result['sources']}")
            print(f"Metadata: {result.get('metadata', [])}")
            
            # Display metadata in a more readable format
            if result.get('metadata'):
                print("\nDetailed Metadata:")
                for i, meta in enumerate(result['metadata']):
                    print(f"  Result {i+1}:")
                    print(f"    H1 (Name): {meta.get('h1', 'N/A')}")
                    print(f"    H2 (Heading): {meta.get('h2', 'N/A')}")
                    print(f"    Source: {meta.get('source', 'N/A')}")
                    print(f"    Relevance Score: {meta.get('relevance_score', 'N/A')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the service")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rag_service()
