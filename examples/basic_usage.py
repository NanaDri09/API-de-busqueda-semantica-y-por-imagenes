#!/usr/bin/env python3
"""
Basic Usage Example for Semantic Search Core Module

This script demonstrates the fundamental CRUD operations and search functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ProductService, Product

# Load environment variables
load_dotenv()

def main():
    print("=== Semantic Search Core Module - Basic Usage ===\n")
    
    # Initialize the service
    print("1. Initializing ProductService...")
    service = ProductService()
    print("✅ ProductService initialized successfully\n")
    
    # Create some sample products
    print("2. Creating sample products...")
    
    products_data = [
        {
            "id": "laptop-001",
            "title": "MacBook Pro 16-inch",
            "description": "Professional laptop with M2 chip, 32GB RAM, and 1TB SSD. Perfect for developers and creative professionals."
        },
        {
            "id": "phone-001",
            "title": "iPhone 15 Pro",
            "description": "Latest iPhone with advanced camera system, A17 Pro chip, and titanium design. Great for photography and mobile productivity."
        },
        {
            "id": "headphones-001",
            "title": "Sony WH-1000XM5",
            "description": "Premium wireless noise-canceling headphones with exceptional sound quality and long battery life."
        },
        {
            "id": "tablet-001",
            "title": "iPad Pro 12.9",
            "description": "Powerful tablet with M2 chip, Liquid Retina display, and Apple Pencil support. Ideal for digital art and productivity."
        }
    ]
    
    for product_data in products_data:
        try:
            product = service.create_product(**product_data)
            print(f"✅ Created: {product.title}")
        except Exception as e:
            print(f"❌ Error creating product {product_data['id']}: {e}")
    
    print(f"\n📊 Total products created: {service.get_product_count()}\n")
    
    # Demonstrate different search types
    print("3. Testing different search methods...")
    
    search_queries = [
        "professional laptop for work",
        "wireless audio device",
        "mobile phone with camera",
        "tablet for drawing"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Hybrid search (default)
        hybrid_results = service.search_products(query, search_type="hybrid", top_k=3)
        print(f"  Hybrid: {hybrid_results}")
        
        # Semantic search
        semantic_results = service.search_products(query, search_type="semantic", top_k=3)
        print(f"  Semantic: {semantic_results}")
        
        # Keyword search
        keyword_results = service.search_products(query, search_type="keyword", top_k=3)
        print(f"  Keyword: {keyword_results}")
    
    # Demonstrate product retrieval
    print("\n4. Retrieving product details...")
    
    product_id = "laptop-001"
    product = service.get_product_by_id(product_id)
    if product:
        print(f"✅ Found product: {product.title}")
        print(f"   Description: {product.description}")
    else:
        print(f"❌ Product {product_id} not found")
    
    # Demonstrate product update
    print("\n5. Updating a product...")
    
    try:
        updated_product = service.update_product(
            id="laptop-001",
            description="Professional laptop with M2 chip, 32GB RAM, 1TB SSD, and stunning Retina display. Perfect for developers, designers, and creative professionals."
        )
        print(f"✅ Updated product: {updated_product.title}")
        print(f"   New description: {updated_product.description}")
    except Exception as e:
        print(f"❌ Error updating product: {e}")
    
    # Test search after update
    print("\n6. Testing search after update...")
    results = service.search_products("retina display laptop", search_type="hybrid", top_k=2)
    print(f"🔍 Search for 'retina display laptop': {results}")
    
    # Show system statistics
    print("\n7. System statistics...")
    stats = service.get_search_statistics()
    print(f"📊 Statistics:")
    print(f"   Total products: {stats['total_products']}")
    print(f"   Vector index size: {stats['vector_index_size']}")
    print(f"   BM25 index size: {stats['bm25_index_size']}")
    print(f"   Default weights: BM25={stats['default_weights']['bm25']}, Vector={stats['default_weights']['vector']}")
    
    # List all products
    print("\n8. All products in the system:")
    all_products = service.list_all_products()
    for product in all_products:
        print(f"   - {product.id}: {product.title}")
    
    print("\n=== Basic Usage Example Complete ===")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 