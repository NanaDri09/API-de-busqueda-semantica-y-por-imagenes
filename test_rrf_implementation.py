#!/usr/bin/env python3
"""
Test script for RRF and Multi-Stage Search Implementation
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.product_service import ProductService
from core.services.rrf_service import RRFService
from core.models.search_config import SearchStrategy
import time

def test_rrf_service():
    """Test the RRF service directly."""
    print("🧪 Testing RRF Service...")
    
    rrf_service = RRFService()
    
    # Test data: simulated search results
    bm25_results = ["prod1", "prod2", "prod3", "prod4", "prod5"]
    vector_results = ["prod3", "prod1", "prod6", "prod7", "prod2"]
    
    # Test basic RRF combination
    combined = rrf_service.combine_search_results(
        bm25_results=bm25_results,
        vector_results=vector_results,
        k=60,
        top_k=5
    )
    
    print(f"✅ RRF combination successful: {combined}")
    
    # Test multiple search combination
    search_results = {
        "bm25": bm25_results,
        "vector": vector_results,
        "manual": ["prod1", "prod8", "prod3"]
    }
    
    multi_combined = rrf_service.combine_multiple_searches(
        search_results=search_results,
        k=60,
        top_k=5
    )
    
    print(f"✅ Multi-search RRF successful: {multi_combined}")
    print()

def test_product_service_with_sample_data():
    """Test ProductService with sample data."""
    print("🧪 Testing ProductService with RRF...")
    
    # Initialize service
    service = ProductService()
    
    # Clear any existing data
    service.clear_all_data()
    
    # Add sample products
    sample_products = [
        {
            "id": "laptop-001",
            "title": "MacBook Pro",
            "description": "Professional laptop for developers and creative professionals"
        },
        {
            "id": "phone-001", 
            "title": "iPhone 15",
            "description": "Latest smartphone with advanced camera and AI features"
        },
        {
            "id": "tablet-001",
            "title": "iPad Pro",
            "description": "Professional tablet for digital art and productivity"
        },
        {
            "id": "watch-001",
            "title": "Apple Watch",
            "description": "Smart watch with health monitoring and fitness tracking"
        }
    ]
    
    print("📝 Creating sample products...")
    for product_data in sample_products:
        service.create_product(**product_data)
    
    print(f"✅ Created {len(sample_products)} products")
    
    # Test different search types
    test_query = "professional laptop development"
    
    print(f"\n🔍 Testing search with query: '{test_query}'")
    
    # Test traditional hybrid search
    print("\n1. Traditional Hybrid Search:")
    hybrid_results = service.search_products(
        query=test_query,
        search_type="hybrid",
        top_k=3
    )
    print(f"   Results: {hybrid_results}")
    
    # Test RRF search
    print("\n2. RRF Search:")
    rrf_results = service.search_products(
        query=test_query,
        search_type="rrf",
        top_k=3
    )
    print(f"   Results: {rrf_results}")
    
    # Test strategy-based search
    print("\n3. Strategy-based Search:")
    strategies = ["balanced", "speed_first", "quality_first", "rrf_only"]
    
    for strategy in strategies:
        try:
            start_time = time.time()
            strategy_results = service.search_with_strategy(
                query=test_query,
                strategy=strategy,
                top_k=3
            )
            execution_time = (time.time() - start_time) * 1000
            
            print(f"   {strategy}: {strategy_results['results']} ({execution_time:.1f}ms)")
            print(f"      Strategy: {strategy_results.get('strategy', 'N/A')}")
            print(f"      Stages: {strategy_results.get('stages_executed', 'N/A')}")
            
        except Exception as e:
            print(f"   {strategy}: ❌ Error - {e}")
    
    print()

def test_available_strategies():
    """Test listing available strategies."""
    print("🧪 Testing Available Strategies...")
    
    service = ProductService()
    strategies = service.get_available_strategies()
    
    print("📋 Available Search Strategies:")
    for strategy in strategies:
        print(f"   • {strategy['name']} ({strategy['type']})")
        print(f"     Description: {strategy['description']}")
        print(f"     Expected latency: {strategy['expected_latency_ms']}ms")
        print(f"     Quality score: {strategy['quality_score']}")
        print(f"     Stages: {strategy['stages']}")
        print()

def run_performance_comparison():
    """Compare performance of different search methods."""
    print("🧪 Performance Comparison...")
    
    service = ProductService()
    
    # Ensure we have some data
    if service.get_product_count() == 0:
        print("⚠️  No products found. Run the sample data test first.")
        return
    
    test_queries = [
        "professional laptop",
        "smartphone camera",
        "tablet productivity",
        "fitness tracking"
    ]
    
    search_methods = [
        ("hybrid", {"search_type": "hybrid"}),
        ("rrf", {"search_type": "rrf"}),
        ("balanced", {"strategy": "balanced"})
    ]
    
    print("📊 Performance Results:")
    print("Query".ljust(20) + "Method".ljust(12) + "Time(ms)".ljust(10) + "Results")
    print("-" * 60)
    
    for query in test_queries:
        for method_name, method_params in search_methods:
            try:
                start_time = time.time()
                
                if "strategy" in method_params:
                    results = service.search_with_strategy(query=query, **method_params, top_k=3)
                    result_list = results["results"]
                else:
                    result_list = service.search_products(query=query, **method_params, top_k=3)
                
                execution_time = (time.time() - start_time) * 1000
                
                print(f"{query[:19].ljust(20)}{method_name.ljust(12)}{execution_time:7.1f}   {len(result_list)} items")
                
            except Exception as e:
                print(f"{query[:19].ljust(20)}{method_name.ljust(12)}ERROR     {str(e)[:20]}")
    
    print()

def main():
    """Main test execution."""
    print("🚀 Testing RRF and Multi-Stage Search Implementation")
    print("=" * 60)
    
    try:
        # Test 1: RRF Service
        test_rrf_service()
        
        # Test 2: ProductService with RRF
        test_product_service_with_sample_data()
        
        # Test 3: Available Strategies
        test_available_strategies()
        
        # Test 4: Performance Comparison
        run_performance_comparison()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 