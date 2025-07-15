#!/usr/bin/env python3
"""
Test script to verify Spanish dataset loads correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.spanish_tech_products import get_all_products, get_test_queries

def test_dataset():
    """Test the Spanish dataset"""
    print("🧪 Testing Spanish Tech Product Dataset")
    print("=" * 50)
    
    # Test products
    products = get_all_products()
    print(f"📦 Products loaded: {len(products)}")
    
    if products:
        print(f"\n📱 Sample products:")
        for i, product in enumerate(products[:5]):
            print(f"{i+1}. {product['title']}")
            print(f"   ID: {product['id']}")
            print(f"   Description: {product['description'][:100]}...")
            print()
    
    # Test queries
    queries = get_test_queries()
    print(f"🔍 Test queries loaded: {len(queries)}")
    
    if queries:
        print(f"\n📋 Sample queries:")
        for i, query in enumerate(queries[:3]):
            print(f"{i+1}. Query: {query['query']}")
            print(f"   Relevant IDs: {query['relevant_ids']}")
            print(f"   Description: {query['description']}")
            print()
    
    # Validate data integrity
    print("🔍 Validating data integrity...")
    
    # Check for duplicate IDs
    product_ids = [p['id'] for p in products]
    if len(product_ids) != len(set(product_ids)):
        print("❌ Duplicate product IDs found!")
        return False
    
    # Check query relevance
    all_product_ids = set(product_ids)
    for query in queries:
        missing_ids = set(query['relevant_ids']) - all_product_ids
        if missing_ids:
            print(f"❌ Query '{query['query']}' references missing IDs: {missing_ids}")
            return False
    
    print("✅ All validation checks passed!")
    print(f"\n📊 Summary:")
    print(f"   Products: {len(products)}")
    print(f"   Queries: {len(queries)}")
    print(f"   Categories: {len(set(p['id'].split('-')[0] for p in products))}")
    
    return True

if __name__ == "__main__":
    success = test_dataset()
    exit(0 if success else 1) 