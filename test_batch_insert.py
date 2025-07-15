#!/usr/bin/env python3
"""
Simple test script for batch product insertion API
"""

import json
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-1234567890"

def test_batch_insert():
    """Test the batch insert functionality"""
    print("🚀 Testing Batch Product Insert API")
    print("=" * 40)
    
    # Load the sample payload
    try:
        with open("sample_batch_payload.json", "r") as f:
            payload = json.load(f)
    except FileNotFoundError:
        print("❌ sample_batch_payload.json not found!")
        return False
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"📤 Sending batch insert request for {len(payload['products'])} products...")
    
    try:
        # Send batch insert request
        response = requests.post(
            f"{API_BASE_URL}/api/v1/products/batch",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Batch insert successful!")
            print(f"   - Success count: {result['success_count']}")
            print(f"   - Failure count: {result['failure_count']}")
            print(f"   - Execution time: {result['execution_time_ms']:.2f}ms")
            
            if result['failed']:
                print("⚠️  Some products failed:")
                for failure in result['failed']:
                    print(f"   - {failure['id']}: {failure['error']}")
            
            return True
        else:
            print(f"❌ Batch insert failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_search():
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    
    # Wait a moment for indexing
    time.sleep(2)
    
    search_payload = {
        "query": "laptop professional development",
        "search_type": "hybrid",
        "top_k": 3,
        "include_product_details": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/search/",
            headers={"Content-Type": "application/json"},
            json=search_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful!")
            print(f"   - Query: '{result['query']}'")
            print(f"   - Search type: {result['search_type']}")
            print(f"   - Results found: {result['total_results']}")
            print(f"   - Execution time: {result['execution_time_ms']:.2f}ms")
            
            if result['results']:
                print("   - Top results:")
                for i, res in enumerate(result['results'][:3], 1):
                    print(f"     {i}. {res['product_id']} (score: {res['score']:.3f})")
                    if res.get('product'):
                        print(f"        Title: {res['product']['title']}")
            
            return True
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Search request failed: {e}")
        return False

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test execution"""
    
    # Check if API is running
    if not check_api_health():
        print("❌ API is not running or not accessible at http://localhost:8000")
        print("   Please start the API first:")
        print("   python main.py")
        return
    
    print("✅ API is running")
    
    # Run tests
    batch_success = test_batch_insert()
    if batch_success:
        test_search()
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    main() 