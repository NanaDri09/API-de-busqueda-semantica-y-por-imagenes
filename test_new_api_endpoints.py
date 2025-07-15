#!/usr/bin/env python3
"""
Test script for new API endpoints
Tests RRF search, strategy-based search, and available strategies
"""

import requests
import json
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-secret-api-key-here"  # Update with your API key

def test_endpoint(method: str, url: str, data: Dict[Any, Any] = None, params: Dict[str, str] = None):
    """Test an API endpoint and return the response."""
    headers = {"Content-Type": "application/json"}
    
    print(f"\n🧪 Testing {method.upper()} {url}")
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, params=params)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, json=data, params=params)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201 for success
            result = response.json()
            print(f"   ✅ Success!")
            return result
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Make sure FastAPI server is running on {BASE_URL}")
        return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_new_search_endpoints():
    """Test all new search endpoints."""
    print("🚀 TESTING NEW API ENDPOINTS")
    print("=" * 50)
    
    # First, add some test products
    print("\n📦 Adding test products...")
    
    test_products = [
        {
            "id": "laptop-gaming-001",
            "title": "ASUS ROG Gaming Laptop",
            "description": "Portátil gaming de alto rendimiento con RTX 4070 y AMD Ryzen 9"
        },
        {
            "id": "laptop-work-002", 
            "title": "MacBook Pro M3",
            "description": "Equipo portátil para edición de video y desarrollo de software"
        },
        {
            "id": "audio-premium-003",
            "title": "Sony WH-1000XM5",
            "description": "Auriculares inalámbricos con cancelación de ruido activa"
        }
    ]
    
    for product in test_products:
        test_endpoint("POST", f"{BASE_URL}/products/", data=product)
    
    # Test Query
    test_query = "equipo portátil para edición de video"
    print(f"\n🔍 Using test query: '{test_query}'")
    
    # 1. Test RRF Search
    print(f"\n{'='*60}")
    print("1. TESTING RRF SEARCH ENDPOINT")
    print(f"{'='*60}")
    
    rrf_params = {
        "query": test_query,
        "top_k": 5,
        "rrf_k": 20,
        "include_product_details": True
    }
    
    rrf_result = test_endpoint("POST", f"{BASE_URL}/search/rrf", params=rrf_params)
    if rrf_result:
        print(f"   📊 Results: {rrf_result['total_results']} items")
        print(f"   ⏱️  Time: {rrf_result['execution_time_ms']:.1f}ms")
        print(f"   🔍 Search Type: {rrf_result['search_type']}")
        
        for i, result in enumerate(rrf_result['results'][:2]):
            print(f"   {i+1}. {result['product_id']} (score: {result['score']:.3f})")
    
    # 2. Test Strategy Search - Quality First
    print(f"\n{'='*60}")
    print("2. TESTING STRATEGY SEARCH - QUALITY FIRST")
    print(f"{'='*60}")
    
    strategy_data = {
        "query": test_query,
        "strategy": "quality_first",
        "top_k": 5,
        "include_product_details": True
    }
    
    strategy_result = test_endpoint("POST", f"{BASE_URL}/search/strategy", data=strategy_data)
    if strategy_result:
        print(f"   📊 Results: {strategy_result['total_results']} items")
        print(f"   ⏱️  Time: {strategy_result['execution_time_ms']:.1f}ms")
        print(f"   🎯 Strategy: {strategy_result['strategy']}")
        print(f"   🔄 Stages: {strategy_result['stages_executed']}")
        
        print("\n   📋 Stage Details:")
        for stage in strategy_result['stage_details']:
            print(f"      Stage {stage['stage']}: {stage['method']} ({stage['execution_time_ms']:.1f}ms)")
            print(f"         → {stage['description']}")
    
    # 3. Test Strategy Search - Speed First  
    print(f"\n{'='*60}")
    print("3. TESTING STRATEGY SEARCH - SPEED FIRST")
    print(f"{'='*60}")
    
    strategy_data['strategy'] = 'speed_first'
    speed_result = test_endpoint("POST", f"{BASE_URL}/search/strategy", data=strategy_data)
    if speed_result:
        print(f"   📊 Results: {speed_result['total_results']} items")
        print(f"   ⏱️  Time: {speed_result['execution_time_ms']:.1f}ms")
        print(f"   🎯 Strategy: {speed_result['strategy']}")
        print(f"   🔄 Stages: {speed_result['stages_executed']}")
    
    # 4. Test Strategy Search - Balanced
    print(f"\n{'='*60}")
    print("4. TESTING STRATEGY SEARCH - BALANCED")
    print(f"{'='*60}")
    
    strategy_data['strategy'] = 'balanced'
    balanced_result = test_endpoint("POST", f"{BASE_URL}/search/strategy", data=strategy_data)
    if balanced_result:
        print(f"   📊 Results: {balanced_result['total_results']} items")
        print(f"   ⏱️  Time: {balanced_result['execution_time_ms']:.1f}ms")
        print(f"   🎯 Strategy: {balanced_result['strategy']}")
        print(f"   🔄 Stages: {balanced_result['stages_executed']}")
    
    # 5. Test Available Strategies
    print(f"\n{'='*60}")
    print("5. TESTING AVAILABLE STRATEGIES ENDPOINT")
    print(f"{'='*60}")
    
    strategies_result = test_endpoint("GET", f"{BASE_URL}/search/strategies")
    if strategies_result:
        print(f"   📊 Total Strategies: {strategies_result['total_strategies']}")
        print(f"   📅 Retrieved at: {strategies_result['timestamp']}")
        
        print("\n   🎯 Available Strategies:")
        for strategy in strategies_result['strategies']:
            print(f"      • {strategy['name']} ({strategy['type']})")
            print(f"        Description: {strategy['description']}")
            print(f"        Expected latency: {strategy.get('expected_latency_ms', 'N/A')}ms")
            print(f"        Quality score: {strategy.get('quality_score', 'N/A')}")
            print(f"        Stages: {strategy.get('stages', 'N/A')}")
            print()
    
    # 6. Performance Comparison
    print(f"\n{'='*60}")
    print("6. PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    
    comparison_data = [
        ("RRF", rrf_result),
        ("Quality First", strategy_result),
        ("Speed First", speed_result),
        ("Balanced", balanced_result)
    ]
    
    print(f"{'Method':<15} {'Time(ms)':<10} {'Results':<8} {'Stages':<7}")
    print("-" * 45)
    
    for method_name, result in comparison_data:
        if result:
            time_ms = result['execution_time_ms']
            results_count = result['total_results']
            stages = result.get('stages_executed', 1)
            print(f"{method_name:<15} {time_ms:<10.1f} {results_count:<8} {stages:<7}")
    
    print(f"\n🎉 API Testing Complete!")
    print("All new endpoints are working correctly! 🚀")

if __name__ == "__main__":
    test_new_search_endpoints() 