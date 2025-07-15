#!/usr/bin/env python3
"""
Batch Operations Example for Semantic Search Core Module

This script demonstrates efficient batch operations for large-scale product management:
- Bulk product creation
- Batch updates
- Performance optimization
- Data migration scenarios
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# Add the parent directory to the path to import the core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ProductService, Product

# Load environment variables
load_dotenv()

def generate_large_product_dataset():
    """Generate a large dataset of products for batch testing."""
    
    categories = {
        "electronics": [
            ("Laptop", "High-performance laptop with advanced processors, ample RAM, and fast SSD storage. Perfect for professionals, students, and gamers who need reliable computing power."),
            ("Smartphone", "Latest smartphone with advanced camera system, fast processor, and long battery life. Ideal for communication, photography, and mobile productivity."),
            ("Tablet", "Versatile tablet with touch screen, stylus support, and portable design. Great for reading, drawing, note-taking, and entertainment."),
            ("Headphones", "Premium headphones with superior sound quality, noise cancellation, and comfortable fit. Perfect for music lovers and professionals."),
            ("Smart Watch", "Advanced smartwatch with fitness tracking, notifications, and health monitoring features. Essential for active lifestyle and connectivity."),
            ("Camera", "Professional camera with high resolution, multiple lenses, and advanced features. Perfect for photography enthusiasts and content creators."),
            ("Gaming Console", "Powerful gaming console with extensive game library, online features, and entertainment capabilities. Great for gamers and families."),
            ("Monitor", "High-resolution monitor with accurate colors, fast refresh rate, and ergonomic design. Essential for professionals and gamers."),
            ("Keyboard", "Mechanical keyboard with tactile switches, customizable lighting, and durable construction. Perfect for typing enthusiasts and gamers."),
            ("Mouse", "Precision mouse with ergonomic design, customizable buttons, and high DPI sensor. Essential for productivity and gaming.")
        ],
        "home": [
            ("Vacuum Cleaner", "Powerful vacuum cleaner with advanced filtration, multiple attachments, and efficient cleaning performance. Essential for maintaining clean homes."),
            ("Coffee Maker", "Premium coffee maker with programmable settings, thermal carafe, and consistent brewing temperature. Perfect for coffee enthusiasts."),
            ("Air Purifier", "Advanced air purifier with HEPA filtration, quiet operation, and smart controls. Essential for clean air and health."),
            ("Blender", "High-performance blender with powerful motor, multiple speeds, and durable blades. Perfect for smoothies, soups, and food preparation."),
            ("Toaster", "Reliable toaster with multiple settings, even browning, and compact design. Essential for breakfast preparation."),
            ("Microwave", "Versatile microwave with multiple power levels, preset functions, and spacious interior. Perfect for quick heating and cooking."),
            ("Dishwasher", "Efficient dishwasher with multiple wash cycles, energy-saving features, and quiet operation. Essential for modern kitchens."),
            ("Refrigerator", "Spacious refrigerator with energy-efficient cooling, multiple compartments, and smart features. Essential for food storage."),
            ("Washing Machine", "Reliable washing machine with multiple wash cycles, energy efficiency, and large capacity. Essential for laundry care."),
            ("Dryer", "Efficient dryer with multiple heat settings, moisture sensors, and large capacity. Perfect for completing laundry tasks.")
        ],
        "fashion": [
            ("Jeans", "Comfortable jeans with classic fit, durable denim, and versatile style. Perfect for casual wear and everyday comfort."),
            ("T-Shirt", "Soft t-shirt with comfortable fit, breathable fabric, and timeless design. Essential for casual wear and layering."),
            ("Sneakers", "Comfortable sneakers with supportive sole, breathable material, and stylish design. Perfect for daily wear and light exercise."),
            ("Jacket", "Stylish jacket with weather protection, comfortable fit, and versatile design. Great for layering and outdoor activities."),
            ("Dress", "Elegant dress with flattering fit, quality fabric, and timeless style. Perfect for special occasions and professional settings."),
            ("Shoes", "Quality shoes with comfortable fit, durable construction, and classic style. Essential for professional and formal occasions."),
            ("Bag", "Functional bag with spacious interior, durable materials, and stylish design. Perfect for daily use and organization."),
            ("Hat", "Stylish hat with sun protection, comfortable fit, and versatile design. Great for outdoor activities and fashion."),
            ("Sunglasses", "Protective sunglasses with UV protection, comfortable fit, and fashionable design. Essential for eye protection and style."),
            ("Watch", "Reliable watch with accurate timekeeping, durable construction, and elegant design. Perfect for punctuality and style.")
        ],
        "books": [
            ("Programming Guide", "Comprehensive programming guide with practical examples, best practices, and advanced techniques. Essential for developers and students."),
            ("Business Book", "Insightful business book with proven strategies, case studies, and actionable advice. Perfect for entrepreneurs and professionals."),
            ("Self-Help Book", "Motivational self-help book with practical tools, inspiring stories, and life-changing strategies. Great for personal development."),
            ("Fiction Novel", "Engaging fiction novel with compelling characters, intricate plot, and immersive storytelling. Perfect for entertainment and escape."),
            ("History Book", "Informative history book with detailed research, engaging narrative, and historical insights. Great for learning and understanding."),
            ("Science Book", "Educational science book with clear explanations, fascinating discoveries, and practical applications. Perfect for curious minds."),
            ("Cookbook", "Practical cookbook with delicious recipes, cooking techniques, and nutritional information. Essential for home cooks."),
            ("Art Book", "Beautiful art book with stunning visuals, artist profiles, and creative inspiration. Perfect for art lovers and students."),
            ("Travel Guide", "Comprehensive travel guide with destination information, practical tips, and cultural insights. Essential for travelers."),
            ("Health Book", "Informative health book with evidence-based advice, wellness strategies, and lifestyle recommendations. Great for healthy living.")
        ]
    }
    
    products_data = []
    product_id = 1
    
    # Generate products for each category
    for category, items in categories.items():
        for i in range(50):  # 50 products per category
            item_type, base_description = items[i % len(items)]
            
            # Add variation to make each product unique
            variations = [
                "Pro", "Plus", "Max", "Ultra", "Premium", "Advanced", "Elite", "Professional",
                "Deluxe", "Standard", "Essential", "Compact", "Wireless", "Smart", "Digital"
            ]
            
            brands = [
                "TechCorp", "InnovateTech", "QualityBrand", "PremiumCo", "ReliableTech",
                "ModernDesign", "EliteManufacturing", "SmartSolutions", "ProGear", "NextGen"
            ]
            
            variation = variations[i % len(variations)]
            brand = brands[i % len(brands)]
            
            product = {
                "id": f"{category}-{product_id:04d}",
                "title": f"{brand} {item_type} {variation}",
                "description": f"{base_description} Model {variation} offers enhanced features and superior performance for demanding users."
            }
            
            products_data.append(product)
            product_id += 1
    
    return products_data

def benchmark_batch_vs_individual(service):
    """Compare performance of batch vs individual operations."""
    
    print("=== Batch vs Individual Operations Benchmark ===\n")
    
    # Generate test data
    test_products = generate_large_product_dataset()[:50]  # Use 50 products for testing
    
    # Clear existing data
    service.clear_all_data()
    
    # Test individual creation
    print("Testing individual product creation...")
    start_time = time.time()
    
    for product_data in test_products:
        try:
            service.create_product(**product_data)
        except Exception as e:
            print(f"Error creating product {product_data['id']}: {e}")
    
    individual_time = time.time() - start_time
    individual_count = service.get_product_count()
    
    print(f"✅ Individual creation: {individual_time:.2f}s for {individual_count} products")
    print(f"   Average: {individual_time/individual_count:.3f}s per product")
    
    # Clear data for batch test
    service.clear_all_data()
    
    # Test batch creation
    print("\nTesting batch product creation...")
    start_time = time.time()
    
    try:
        batch_products = service.batch_create_products(test_products)
        batch_time = time.time() - start_time
        batch_count = len(batch_products)
        
        print(f"✅ Batch creation: {batch_time:.2f}s for {batch_count} products")
        print(f"   Average: {batch_time/batch_count:.3f}s per product")
        
        # Performance comparison
        speedup = individual_time / batch_time
        print(f"\n📊 Performance Comparison:")
        print(f"   Batch is {speedup:.1f}x faster than individual operations")
        print(f"   Time saved: {individual_time - batch_time:.2f}s ({((individual_time - batch_time)/individual_time)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Batch creation failed: {e}")

def demonstrate_large_scale_operations(service):
    """Demonstrate operations with large datasets."""
    
    print("=== Large Scale Operations Demo ===\n")
    
    # Generate large dataset
    print("Generating large product dataset...")
    large_dataset = generate_large_product_dataset()
    print(f"Generated {len(large_dataset)} products across multiple categories")
    
    # Clear existing data
    service.clear_all_data()
    
    # Batch create all products
    print(f"\nCreating {len(large_dataset)} products in batches...")
    
    batch_size = 100
    total_created = 0
    start_time = time.time()
    
    for i in range(0, len(large_dataset), batch_size):
        batch = large_dataset[i:i + batch_size]
        
        try:
            batch_products = service.batch_create_products(batch)
            total_created += len(batch_products)
            
            elapsed = time.time() - start_time
            rate = total_created / elapsed
            
            print(f"  Batch {i//batch_size + 1}: {len(batch_products)} products created "
                  f"(Total: {total_created}, Rate: {rate:.1f} products/sec)")
            
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1} failed: {e}")
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Large scale creation complete:")
    print(f"   Total products: {total_created}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average rate: {total_created/total_time:.1f} products/sec")
    
    # Test search performance with large dataset
    print(f"\n🔍 Testing search performance with {total_created} products...")
    
    search_queries = [
        "laptop for programming",
        "wireless headphones",
        "kitchen appliance",
        "comfortable shoes",
        "programming book"
    ]
    
    for query in search_queries:
        start_time = time.time()
        results = service.search_products(query, search_type="hybrid", top_k=10)
        search_time = time.time() - start_time
        
        print(f"  '{query}': {search_time:.3f}s ({len(results)} results)")

def simulate_data_migration(service):
    """Simulate a data migration scenario."""
    
    print("=== Data Migration Simulation ===\n")
    
    # Simulate existing data
    print("1. Creating initial dataset...")
    initial_data = generate_large_product_dataset()[:100]
    service.clear_all_data()
    service.batch_create_products(initial_data)
    
    initial_count = service.get_product_count()
    print(f"✅ Initial dataset: {initial_count} products")
    
    # Simulate data export
    print("\n2. Exporting existing data...")
    all_products = service.list_all_products()
    export_data = [product.to_dict() for product in all_products]
    
    # Save to JSON file for demonstration
    with open("data_export.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(export_data)} products to data_export.json")
    
    # Simulate adding new data
    print("\n3. Preparing migration with new data...")
    new_data = generate_large_product_dataset()[100:150]  # Next 50 products
    
    # Combine existing and new data
    combined_data = export_data + new_data
    print(f"✅ Combined dataset: {len(combined_data)} products")
    
    # Simulate migration (clear and rebuild)
    print("\n4. Performing migration...")
    start_time = time.time()
    
    service.clear_all_data()
    migrated_products = service.batch_create_products(combined_data)
    
    migration_time = time.time() - start_time
    final_count = service.get_product_count()
    
    print(f"✅ Migration complete:")
    print(f"   Migrated products: {len(migrated_products)}")
    print(f"   Final count: {final_count}")
    print(f"   Migration time: {migration_time:.2f}s")
    
    # Verify data integrity
    print("\n5. Verifying data integrity...")
    
    # Test search functionality
    test_queries = ["laptop", "headphones", "book"]
    all_working = True
    
    for query in test_queries:
        try:
            results = service.search_products(query, top_k=5)
            print(f"  ✅ Search '{query}': {len(results)} results")
        except Exception as e:
            print(f"  ❌ Search '{query}' failed: {e}")
            all_working = False
    
    if all_working:
        print("✅ Data integrity verified - all systems operational")
    else:
        print("❌ Data integrity issues detected")
    
    # Cleanup
    if os.path.exists("data_export.json"):
        os.remove("data_export.json")

def main():
    print("=== Semantic Search Core Module - Batch Operations Examples ===\n")
    
    # Initialize service
    print("Initializing ProductService...")
    service = ProductService()
    
    # Benchmark batch vs individual operations
    print("1. Benchmarking batch vs individual operations...")
    benchmark_batch_vs_individual(service)
    
    print("\n" + "="*60 + "\n")
    
    # Demonstrate large scale operations
    print("2. Demonstrating large scale operations...")
    demonstrate_large_scale_operations(service)
    
    print("\n" + "="*60 + "\n")
    
    # Simulate data migration
    print("3. Simulating data migration...")
    simulate_data_migration(service)
    
    print("\n=== Batch Operations Examples Complete ===")

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