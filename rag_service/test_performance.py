"""
Performance testing script for PharmaRAG service.
Tests the optimized database operations and caching.
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_MEDICINE_NAMES = [
    "4Flex - proszek",
    "Acard",
    "Acenocumarol",
    "Acetylocysteina",
    "Aciclovir",
    "Gefitinib Accord - tabletki powlekane"
]

def test_document_retrieval(medicine_name: str) -> Dict[str, Any]:
    """Test document retrieval for a specific medicine name."""
    start_time = time.time()
    
    try:
        response = requests.get(f"{BASE_URL}/documents/{medicine_name}")
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            "medicine_name": medicine_name,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "success": response.status_code == 200,
            "content_length": len(response.text) if response.status_code == 200 else 0
        }
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "medicine_name": medicine_name,
            "status_code": None,
            "duration_ms": duration_ms,
            "success": False,
            "error": str(e)
        }

def test_cache_performance():
    """Test cache performance by making repeated requests."""
    print("Testing cache performance...")
    
    results = []
    
    # First request (cache miss)
    print(f"Making first request for '{TEST_MEDICINE_NAMES[0]}' (cache miss)...")
    first_result = test_document_retrieval(TEST_MEDICINE_NAMES[0])
    results.append(first_result)
    print(f"First request: {first_result['duration_ms']:.2f}ms")
    
    # Second request (cache hit)
    print(f"Making second request for '{TEST_MEDICINE_NAMES[0]}' (cache hit)...")
    second_result = test_document_retrieval(TEST_MEDICINE_NAMES[0])
    results.append(second_result)
    print(f"Second request: {second_result['duration_ms']:.2f}ms")
    
    # Calculate improvement
    if first_result['success'] and second_result['success']:
        improvement = ((first_result['duration_ms'] - second_result['duration_ms']) / first_result['duration_ms']) * 100
        print(f"Cache improvement: {improvement:.1f}%")
    
    return results

def test_multiple_medicines():
    """Test performance across multiple medicine names."""
    print("Testing multiple medicine names...")
    
    results = []
    
    for medicine_name in TEST_MEDICINE_NAMES:
        print(f"Testing '{medicine_name}'...")
        result = test_document_retrieval(medicine_name)
        results.append(result)
        print(f"  Duration: {result['duration_ms']:.2f}ms")
    
    return results

def get_performance_metrics():
    """Get performance metrics from the service."""
    try:
        response = requests.get(f"{BASE_URL}/performance/report")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get performance metrics: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting performance metrics: {e}")
        return None

def get_cache_stats():
    """Get cache statistics from the service."""
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get cache stats: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return None

def print_performance_summary(results: List[Dict[str, Any]]):
    """Print a summary of performance results."""
    print("\n" + "="*50)
    print("PERFORMANCE SUMMARY")
    print("="*50)
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        durations = [r['duration_ms'] for r in successful_results]
        
        print(f"Total requests: {len(results)}")
        print(f"Successful requests: {len(successful_results)}")
        print(f"Success rate: {(len(successful_results) / len(results)) * 100:.1f}%")
        print(f"Average response time: {statistics.mean(durations):.2f}ms")
        print(f"Median response time: {statistics.median(durations):.2f}ms")
        print(f"Min response time: {min(durations):.2f}ms")
        print(f"Max response time: {max(durations):.2f}ms")
        
        # Performance categories
        fast_requests = len([d for d in durations if d < 100])
        medium_requests = len([d for d in durations if 100 <= d < 1000])
        slow_requests = len([d for d in durations if d >= 1000])
        
        print(f"\nPerformance breakdown:")
        print(f"  Fast (<100ms): {fast_requests} requests")
        print(f"  Medium (100-1000ms): {medium_requests} requests")
        print(f"  Slow (>1000ms): {slow_requests} requests")
        
        # Calculate improvement over baseline
        baseline_time = 6800  # 6.8 seconds baseline
        avg_time = statistics.mean(durations)
        improvement = ((baseline_time - avg_time) / baseline_time) * 100
        print(f"\nImprovement over baseline (6.8s): {improvement:.1f}%")
    
    # Print failed requests
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print(f"\nFailed requests:")
        for result in failed_results:
            print(f"  {result['medicine_name']}: {result.get('error', 'Unknown error')}")

def main():
    """Main performance test function."""
    print("PharmaRAG Performance Test")
    print("="*50)
    
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Service is not healthy. Please start the service first.")
            return
    except Exception as e:
        print(f"Service is not running. Please start the service first: {e}")
        return
    
    print("Service is running. Starting performance tests...")
    
    # Test cache performance
    cache_results = test_cache_performance()
    
    # Test multiple medicines
    multiple_results = test_multiple_medicines()
    
    # Get performance metrics
    print("\nGetting performance metrics...")
    perf_metrics = get_performance_metrics()
    
    # Get cache stats
    print("Getting cache statistics...")
    cache_stats = get_cache_stats()
    
    # Print summary
    all_results = cache_results + multiple_results
    print_performance_summary(all_results)
    
    # Print detailed metrics
    if perf_metrics:
        print(f"\nPerformance Metrics:")
        print(json.dumps(perf_metrics, indent=2))
    
    if cache_stats:
        print(f"\nCache Statistics:")
        print(json.dumps(cache_stats, indent=2))

if __name__ == "__main__":
    main()
