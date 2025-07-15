#!/usr/bin/env python3
"""
Comprehensive API test script for the Semantic Search API.
Tests all endpoints and functionality.
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-1234567890"  # For testing endpoints that require auth

class APITester:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_products = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def get_headers(self, auth_required: bool = False) -> Dict[str, str]:
        """Get headers for requests."""
        headers = {"Content-Type": "application/json"}
        if auth_required and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def test_health_check(self):
        """Test health check endpoints."""
        print("🔍 Testing health check endpoints...")
        
        # Root health check
        response = await self.client.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Root health check passed")
        
        # Detailed health check
        response = await self.client.get(f"{self.base_url}/api/v1/search/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "dependencies" in data
        print("✅ Detailed health check passed")
    
    async def test_root_endpoint(self):
        """Test root endpoint."""
        print("🔍 Testing root endpoint...")
        
        response = await self.client.get(f"{self.base_url}/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Semantic Search API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        print("✅ Root endpoint passed")
    
    async def test_product_crud(self):
        """Test product CRUD operations."""
        print("🔍 Testing product CRUD operations...")
        
        # Create a product
        product_data = {
            "id": "test-laptop-001",
            "title": "Test MacBook Pro",
            "description": "High-performance laptop for testing with M2 chip and 16GB RAM"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/products/",
            json=product_data,
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 201
        created_product = response.json()
        assert created_product["id"] == product_data["id"]
        assert created_product["title"] == product_data["title"]
        self.test_products.append(product_data["id"])
        print("✅ Product creation passed")
        
        # Get the product
        response = await self.client.get(f"{self.base_url}/api/v1/products/{product_data['id']}")
        assert response.status_code == 200
        retrieved_product = response.json()
        assert retrieved_product["id"] == product_data["id"]
        print("✅ Product retrieval passed")
        
        # Update the product
        update_data = {
            "title": "Updated MacBook Pro M3",
            "description": "Updated high-performance laptop with M3 chip and 32GB RAM"
        }
        
        response = await self.client.put(
            f"{self.base_url}/api/v1/products/{product_data['id']}",
            json=update_data,
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 200
        updated_product = response.json()
        assert updated_product["title"] == update_data["title"]
        print("✅ Product update passed")
        
        # List products
        response = await self.client.get(f"{self.base_url}/api/v1/products/?page=1&size=10")
        assert response.status_code == 200
        products_list = response.json()
        assert "products" in products_list
        assert "total" in products_list
        assert products_list["total"] >= 1
        print("✅ Product listing passed")
    
    async def test_batch_operations(self):
        """Test batch operations."""
        print("🔍 Testing batch operations...")
        
        # Batch create products
        batch_data = {
            "products": [
                {
                    "id": "batch-phone-001",
                    "title": "iPhone 15 Pro",
                    "description": "Latest iPhone with advanced camera and A17 chip"
                },
                {
                    "id": "batch-tablet-001", 
                    "title": "iPad Pro 12.9",
                    "description": "Professional tablet with M2 chip and Liquid Retina display"
                },
                {
                    "id": "batch-watch-001",
                    "title": "Apple Watch Series 9",
                    "description": "Advanced smartwatch with health monitoring and GPS"
                }
            ]
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/products/batch",
            json=batch_data,
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 201
        batch_result = response.json()
        assert batch_result["success_count"] == 3
        assert batch_result["failure_count"] == 0
        
        # Add to test products for cleanup
        self.test_products.extend([p["id"] for p in batch_data["products"]])
        print("✅ Batch product creation passed")
    
    async def test_search_functionality(self):
        """Test search functionality."""
        print("🔍 Testing search functionality...")
        
        # Wait a moment for indexing
        await asyncio.sleep(2)
        
        # Test hybrid search
        search_data = {
            "query": "laptop professional development",
            "search_type": "hybrid",
            "top_k": 5,
            "bm25_weight": 0.4,
            "vector_weight": 0.6,
            "include_product_details": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/",
            json=search_data
        )
        assert response.status_code == 200
        search_result = response.json()
        assert "results" in search_result
        assert search_result["search_type"] == "hybrid"
        assert "weights" in search_result
        print("✅ Hybrid search passed")
        
        # Test semantic search
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/semantic",
            params={
                "query": "mobile phone communication",
                "top_k": 3,
                "include_product_details": True
            }
        )
        assert response.status_code == 200
        search_result = response.json()
        assert search_result["search_type"] == "semantic"
        print("✅ Semantic search passed")
        
        # Test keyword search
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/keyword",
            params={
                "query": "iPhone camera",
                "top_k": 3,
                "include_product_details": False
            }
        )
        assert response.status_code == 200
        search_result = response.json()
        assert search_result["search_type"] == "keyword"
        print("✅ Keyword search passed")
    
    async def test_search_statistics(self):
        """Test search statistics."""
        print("🔍 Testing search statistics...")
        
        response = await self.client.get(f"{self.base_url}/api/v1/search/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_products" in stats
        assert "vector_index_size" in stats
        assert "bm25_index_size" in stats
        assert "vector_dimension" in stats
        assert stats["total_products"] >= 4  # We created at least 4 products
        print("✅ Search statistics passed")
    
    async def test_error_handling(self):
        """Test error handling."""
        print("🔍 Testing error handling...")
        
        # Test 404 - product not found
        response = await self.client.get(f"{self.base_url}/api/v1/products/nonexistent-product")
        assert response.status_code == 404
        error_data = response.json()
        assert "error" in error_data
        assert "message" in error_data
        print("✅ 404 error handling passed")
        
        # Test 409 - duplicate product creation
        duplicate_data = {
            "id": "test-laptop-001",  # This already exists
            "title": "Duplicate Product",
            "description": "This should fail"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/products/",
            json=duplicate_data,
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 409
        print("✅ 409 conflict handling passed")
        
        # Test 422 - validation error
        invalid_data = {
            "id": "",  # Empty ID should fail validation
            "title": "Invalid Product",
            "description": "This should fail validation"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/products/",
            json=invalid_data,
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 422
        print("✅ 422 validation error handling passed")
    
    async def test_admin_operations(self):
        """Test admin operations."""
        print("🔍 Testing admin operations...")
        
        # Test rebuild indexes
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/rebuild",
            headers=self.get_headers(auth_required=True)
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        print("✅ Index rebuild passed")
        
        # Wait for rebuild to complete
        await asyncio.sleep(2)
        
        # Verify search still works after rebuild
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/semantic",
            params={"query": "laptop", "top_k": 1}
        )
        assert response.status_code == 200
        print("✅ Search after rebuild passed")
    
    async def cleanup(self):
        """Clean up test data."""
        print("🧹 Cleaning up test data...")
        
        # Delete individual products
        for product_id in self.test_products:
            try:
                response = await self.client.delete(
                    f"{self.base_url}/api/v1/products/{product_id}",
                    headers=self.get_headers(auth_required=True)
                )
                if response.status_code == 200:
                    print(f"✅ Deleted product {product_id}")
                elif response.status_code == 404:
                    print(f"⚠️  Product {product_id} not found (may have been deleted already)")
                else:
                    print(f"❌ Failed to delete product {product_id}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error deleting product {product_id}: {e}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting comprehensive API tests...")
        print(f"🎯 Testing API at: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Core functionality tests
            await self.test_health_check()
            await self.test_root_endpoint()
            await self.test_product_crud()
            await self.test_batch_operations()
            await self.test_search_functionality()
            await self.test_search_statistics()
            await self.test_error_handling()
            await self.test_admin_operations()
            
            execution_time = time.time() - start_time
            
            print("=" * 60)
            print(f"🎉 All tests passed successfully!")
            print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
            print(f"📊 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main test execution."""
    async with APITester(BASE_URL, API_KEY) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    # Check if server is running
    try:
        import httpx
        response = httpx.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server is not responding correctly at {BASE_URL}")
            print("Please make sure the API server is running:")
            print("  python main.py")
            print("  or")
            print("  uvicorn main:app --reload")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"Error: {e}")
        print("Please make sure the API server is running:")
        print("  python main.py")
        print("  or")
        print("  uvicorn main:app --reload")
        exit(1)
    
    # Run tests
    asyncio.run(main()) 