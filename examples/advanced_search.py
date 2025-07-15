#!/usr/bin/env python3
"""
Advanced Search Example for Semantic Search Core Module

This script demonstrates advanced search features including:
- Custom weight configurations
- Search comparison analysis
- Performance testing
- Batch operations
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the parent directory to the path to import the core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ProductService, Product

# Load environment variables
load_dotenv()

def create_sample_ecommerce_data(service):
    """Create a comprehensive set of e-commerce products for testing."""
    
    products_data = [
        # Electronics
        {
            "id": "elec-001",
            "title": "MacBook Pro 16-inch M2",
            "description": "Professional laptop with M2 chip, 32GB unified memory, 1TB SSD storage, and stunning Liquid Retina XDR display. Perfect for developers, video editors, and creative professionals who need maximum performance."
        },
        {
            "id": "elec-002", 
            "title": "Dell XPS 13 Plus",
            "description": "Ultra-portable Windows laptop with 12th Gen Intel Core i7, 16GB RAM, 512GB SSD. Features a stunning 13.4-inch OLED display and premium build quality for business professionals."
        },
        {
            "id": "elec-003",
            "title": "iPhone 15 Pro Max",
            "description": "Latest flagship iPhone with A17 Pro chip, titanium design, advanced camera system with 5x optical zoom, and USB-C connectivity. Ideal for photography enthusiasts and mobile productivity."
        },
        {
            "id": "elec-004",
            "title": "Samsung Galaxy S24 Ultra",
            "description": "Premium Android smartphone with S Pen, 200MP camera, 6.8-inch Dynamic AMOLED display, and AI-powered features. Perfect for business users and content creators."
        },
        {
            "id": "elec-005",
            "title": "Sony WH-1000XM5 Headphones",
            "description": "Industry-leading wireless noise-canceling headphones with exceptional sound quality, 30-hour battery life, and comfortable design. Great for travel and focused work."
        },
        {
            "id": "elec-006",
            "title": "AirPods Pro 2nd Generation",
            "description": "Apple's premium wireless earbuds with active noise cancellation, spatial audio, and seamless integration with Apple devices. Perfect for calls and music on the go."
        },
        {
            "id": "elec-007",
            "title": "iPad Pro 12.9 M2",
            "description": "Powerful tablet with M2 chip, Liquid Retina XDR display, and Apple Pencil support. Ideal for digital artists, designers, and professionals who need a portable creative workstation."
        },
        {
            "id": "elec-008",
            "title": "Nintendo Switch OLED",
            "description": "Popular gaming console with vibrant OLED screen, enhanced audio, and versatile play modes. Great for gaming enthusiasts and families who enjoy portable and docked gaming."
        },
        
        # Home & Kitchen
        {
            "id": "home-001",
            "title": "Dyson V15 Detect Vacuum",
            "description": "Powerful cordless vacuum cleaner with laser dust detection, HEPA filtration, and intelligent suction adjustment. Perfect for maintaining clean homes with pets and allergies."
        },
        {
            "id": "home-002",
            "title": "Instant Pot Duo 7-in-1",
            "description": "Multi-functional pressure cooker that works as slow cooker, rice cooker, steamer, sauté pan, yogurt maker, and warmer. Essential for busy families and meal prep enthusiasts."
        },
        {
            "id": "home-003",
            "title": "Nespresso Vertuo Plus",
            "description": "Premium coffee machine with centrifusion technology, one-touch brewing, and automatic capsule ejection. Perfect for coffee lovers who want café-quality drinks at home."
        },
        {
            "id": "home-004",
            "title": "KitchenAid Stand Mixer",
            "description": "Professional-grade stand mixer with 5-quart bowl, 10 speeds, and extensive attachment ecosystem. Essential for baking enthusiasts and home chefs who love to cook from scratch."
        },
        
        # Fashion & Accessories
        {
            "id": "fashion-001",
            "title": "Levi's 501 Original Jeans",
            "description": "Classic straight-leg denim jeans with button fly, made from premium cotton. Timeless style that works for casual wear and can be dressed up or down."
        },
        {
            "id": "fashion-002",
            "title": "Nike Air Max 270 Sneakers",
            "description": "Comfortable lifestyle sneakers with Max Air unit, breathable mesh upper, and modern design. Perfect for casual wear, light exercise, and everyday comfort."
        },
        {
            "id": "fashion-003",
            "title": "Ray-Ban Aviator Sunglasses",
            "description": "Iconic sunglasses with gold-tone frame, crystal green lenses, and UV protection. Classic style that complements any outfit and provides excellent eye protection."
        },
        
        # Books & Media
        {
            "id": "book-001",
            "title": "The Psychology of Programming",
            "description": "Comprehensive guide to understanding how programmers think and work. Essential reading for software developers, team leads, and anyone interested in coding psychology."
        },
        {
            "id": "book-002",
            "title": "Atomic Habits by James Clear",
            "description": "Practical guide to building good habits and breaking bad ones. Proven strategies for personal development and achieving long-term success in any area of life."
        }
    ]
    
    print(f"Creating {len(products_data)} sample products...")
    created_products = service.batch_create_products(products_data)
    print(f"✅ Successfully created {len(created_products)} products\n")
    
    return created_products

def test_search_weights(service):
    """Test different weight configurations for hybrid search."""
    
    print("=== Testing Different Search Weight Configurations ===\n")
    
    query = "laptop for programming and development"
    
    weight_configs = [
        (1.0, 0.0, "Keyword Only"),
        (0.0, 1.0, "Semantic Only"), 
        (0.8, 0.2, "Keyword Heavy"),
        (0.4, 0.6, "Default Hybrid"),
        (0.2, 0.8, "Semantic Heavy")
    ]
    
    print(f"🔍 Query: '{query}'\n")
    
    for bm25_weight, vector_weight, description in weight_configs:
        results = service.search_products(
            query=query,
            search_type="hybrid",
            bm25_weight=bm25_weight,
            vector_weight=vector_weight,
            top_k=5
        )
        
        print(f"{description} (BM25:{bm25_weight}, Vector:{vector_weight}):")
        for i, product_id in enumerate(results[:3], 1):
            product = service.get_product_by_id(product_id)
            if product:
                print(f"  {i}. {product.title}")
        print()

def analyze_search_differences(service):
    """Analyze differences between search methods."""
    
    print("=== Search Method Comparison Analysis ===\n")
    
    test_queries = [
        "wireless audio device",
        "portable computer for work", 
        "kitchen appliance for cooking",
        "comfortable shoes for walking",
        "book about habits and productivity"
    ]
    
    for query in test_queries:
        print(f"🔍 Query: '{query}'")
        
        # Get results from all three methods
        hybrid_results = service.search_products(query, search_type="hybrid", top_k=3)
        semantic_results = service.search_products(query, search_type="semantic", top_k=3)
        keyword_results = service.search_products(query, search_type="keyword", top_k=3)
        
        print(f"  Hybrid:   {hybrid_results}")
        print(f"  Semantic: {semantic_results}")
        print(f"  Keyword:  {keyword_results}")
        
        # Find unique results
        all_results = set(hybrid_results + semantic_results + keyword_results)
        common_results = set(hybrid_results) & set(semantic_results) & set(keyword_results)
        
        print(f"  📊 Total unique results: {len(all_results)}")
        print(f"  📊 Common to all methods: {len(common_results)}")
        print()

def performance_test(service):
    """Test search performance with different query types."""
    
    print("=== Performance Testing ===\n")
    
    queries = [
        "laptop",
        "wireless headphones with noise cancellation",
        "kitchen appliance for meal preparation",
        "comfortable footwear for daily activities",
        "educational content about personal development"
    ]
    
    search_types = ["hybrid", "semantic", "keyword"]
    
    for search_type in search_types:
        print(f"Testing {search_type} search performance:")
        
        total_time = 0
        for query in queries:
            start_time = time.time()
            results = service.search_products(query, search_type=search_type, top_k=5)
            end_time = time.time()
            
            query_time = end_time - start_time
            total_time += query_time
            
            print(f"  '{query}': {query_time:.3f}s ({len(results)} results)")
        
        avg_time = total_time / len(queries)
        print(f"  Average time: {avg_time:.3f}s\n")

def semantic_similarity_showcase(service):
    """Showcase semantic understanding capabilities."""
    
    print("=== Semantic Understanding Showcase ===\n")
    
    # Test semantic understanding with synonyms and related concepts
    semantic_tests = [
        ("portable computer", "Should find laptops"),
        ("mobile phone", "Should find smartphones"),
        ("audio equipment", "Should find headphones and speakers"),
        ("kitchen gadget", "Should find cooking appliances"),
        ("footwear", "Should find shoes and sneakers"),
        ("reading material", "Should find books"),
        ("gaming device", "Should find gaming consoles"),
        ("caffeine machine", "Should find coffee makers")
    ]
    
    for query, expectation in semantic_tests:
        print(f"🔍 Query: '{query}' ({expectation})")
        
        # Use semantic search to show understanding
        semantic_results = service.search_products(query, search_type="semantic", top_k=3)
        
        print("  Semantic results:")
        for i, product_id in enumerate(semantic_results, 1):
            product = service.get_product_by_id(product_id)
            if product:
                print(f"    {i}. {product.title}")
        
        # Compare with keyword search
        keyword_results = service.search_products(query, search_type="keyword", top_k=3)
        print(f"  Keyword results: {len(keyword_results)} found")
        print()

def main():
    print("=== Semantic Search Core Module - Advanced Search Examples ===\n")
    
    # Initialize service
    print("1. Initializing ProductService...")
    service = ProductService()
    
    # Clear any existing data for clean testing
    service.clear_all_data()
    
    # Create comprehensive sample data
    print("2. Creating comprehensive sample data...")
    create_sample_ecommerce_data(service)
    
    # Test different weight configurations
    print("3. Testing weight configurations...")
    test_search_weights(service)
    
    # Analyze search method differences
    print("4. Analyzing search method differences...")
    analyze_search_differences(service)
    
    # Performance testing
    print("5. Running performance tests...")
    performance_test(service)
    
    # Semantic similarity showcase
    print("6. Showcasing semantic understanding...")
    semantic_similarity_showcase(service)
    
    # Final statistics
    print("7. Final system statistics...")
    stats = service.get_search_statistics()
    print(f"📊 Final Statistics:")
    print(f"   Total products: {stats['total_products']}")
    print(f"   Vector index size: {stats['vector_index_size']}")
    print(f"   BM25 index size: {stats['bm25_index_size']}")
    print(f"   Vector dimension: {stats['vector_dimension']}")
    
    print("\n=== Advanced Search Examples Complete ===")

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
        import traceback
        traceback.print_exc()
        sys.exit(1) 