#!/usr/bin/env python3
"""
Debug script to investigate search method issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.product_service import ProductService
from core.models.product import Product
import json

def debug_search_methods():
    """Debug each search method individually"""
    print("🔍 DEBUGGING SEARCH METHODS")
    print("=" * 50)
    
    # Initialize service
    product_service = ProductService()
    
    # Add a few test products
    test_products = [
        {
            "id": "laptop-001", 
            "title": "MacBook Pro Gaming",
            "description": "Portátil gaming de alto rendimiento con procesador M3 Max"
        },
        {
            "id": "phone-001", 
            "title": "iPhone 15 Pro",
            "description": "Smartphone con cámara profesional de 48MP"
        },
        {
            "id": "tablet-001", 
            "title": "iPad Pro",
            "description": "Tablet para productividad empresarial y diseño"
        }
    ]
    
    # Clear and add products
    product_service.clear_all_data()
    for product in test_products:
        product_service.create_product(
            id=product["id"],
            title=product["title"], 
            description=product["description"]
        )
    
    print(f"✅ Added {len(test_products)} test products")
    
    # Test query
    test_query = "laptop gaming alto rendimiento"
    print(f"\n🔍 Testing query: '{test_query}'")
    
    # Test each method individually
    methods_to_test = ["semantic", "keyword", "hybrid", "rrf"]
    
    for method in methods_to_test:
        print(f"\n🧪 Testing {method.upper()} search:")
        try:
            results = product_service.search_products(
                query=test_query,
                search_type=method,
                top_k=5
            )
            print(f"   ✅ Results: {results}")
            print(f"   📊 Count: {len(results)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test multi-stage methods
    strategies = ["balanced", "speed_first", "quality_first"]
    
    for strategy in strategies:
        print(f"\n🧪 Testing {strategy.upper()} strategy:")
        try:
            result_dict = product_service.search_with_strategy(
                query=test_query,
                strategy=strategy,
                top_k=5
            )
            print(f"   ✅ Full result: {json.dumps(result_dict, indent=2)}")
            results = result_dict.get("results", [])
            print(f"   📊 Results count: {len(results)}")
            print(f"   📋 Results: {results}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_search_methods() 