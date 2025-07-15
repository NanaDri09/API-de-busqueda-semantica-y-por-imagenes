#!/usr/bin/env python3
"""
Interactive Demo for Semantic Search Core Module

This script provides an interactive command-line interface to explore
the semantic search functionality with real-time feedback.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ProductService, Product

# Load environment variables
load_dotenv()

class InteractiveDemo:
    def __init__(self):
        self.service = ProductService()
        self.setup_sample_data()
    
    def setup_sample_data(self):
        """Setup sample data for the demo."""
        print("Setting up sample data...")
        
        # Clear existing data
        self.service.clear_all_data()
        
        sample_products = [
            {
                "id": "tech-001",
                "title": "MacBook Pro 16-inch",
                "description": "Professional laptop with M2 chip, 32GB RAM, 1TB SSD. Perfect for developers, video editors, and creative professionals."
            },
            {
                "id": "tech-002",
                "title": "iPhone 15 Pro",
                "description": "Latest iPhone with A17 Pro chip, titanium design, advanced camera system. Great for photography and mobile productivity."
            },
            {
                "id": "tech-003",
                "title": "Sony WH-1000XM5",
                "description": "Premium wireless noise-canceling headphones with exceptional sound quality and 30-hour battery life."
            },
            {
                "id": "tech-004",
                "title": "iPad Pro 12.9",
                "description": "Powerful tablet with M2 chip, Liquid Retina display, Apple Pencil support. Ideal for digital art and productivity."
            },
            {
                "id": "tech-005",
                "title": "Dell XPS 13",
                "description": "Ultra-portable Windows laptop with Intel Core i7, 16GB RAM, 512GB SSD. Perfect for business professionals."
            },
            {
                "id": "home-001",
                "title": "Dyson V15 Detect",
                "description": "Cordless vacuum cleaner with laser dust detection, HEPA filtration, and intelligent suction adjustment."
            },
            {
                "id": "home-002",
                "title": "Instant Pot Duo",
                "description": "7-in-1 pressure cooker: pressure cook, slow cook, rice cooker, steamer, sauté, yogurt maker, and warmer."
            },
            {
                "id": "home-003",
                "title": "Nespresso Vertuo",
                "description": "Coffee machine with centrifusion technology, one-touch brewing, and automatic capsule ejection."
            },
            {
                "id": "fashion-001",
                "title": "Nike Air Max 270",
                "description": "Comfortable lifestyle sneakers with Max Air unit, breathable mesh upper, and modern design."
            },
            {
                "id": "fashion-002",
                "title": "Levi's 501 Jeans",
                "description": "Classic straight-leg denim jeans with button fly, made from premium cotton. Timeless style."
            },
            {
                "id": "book-001",
                "title": "Clean Code",
                "description": "A handbook of agile software craftsmanship. Essential reading for programmers and software developers."
            },
            {
                "id": "book-002",
                "title": "Atomic Habits",
                "description": "Practical guide to building good habits and breaking bad ones. Proven strategies for personal development."
            }
        ]
        
        try:
            self.service.batch_create_products(sample_products)
            print(f"✅ Sample data loaded: {len(sample_products)} products")
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🔍 SEMANTIC SEARCH INTERACTIVE DEMO")
        print("="*60)
        print("1. Search products")
        print("2. Add new product")
        print("3. Update product")
        print("4. Delete product")
        print("5. List all products")
        print("6. Compare search methods")
        print("7. Test custom weights")
        print("8. System statistics")
        print("9. Help")
        print("0. Exit")
        print("="*60)
    
    def search_products(self):
        """Interactive product search."""
        print("\n🔍 PRODUCT SEARCH")
        print("-" * 30)
        
        query = input("Enter search query: ").strip()
        if not query:
            print("❌ Query cannot be empty")
            return
        
        print("\nSearch methods:")
        print("1. Hybrid (default)")
        print("2. Semantic only")
        print("3. Keyword only")
        
        method_choice = input("Choose search method (1-3, default=1): ").strip()
        
        search_type_map = {
            "1": "hybrid",
            "2": "semantic", 
            "3": "keyword",
            "": "hybrid"
        }
        
        search_type = search_type_map.get(method_choice, "hybrid")
        
        try:
            top_k = int(input("Number of results (default=5): ").strip() or "5")
        except ValueError:
            top_k = 5
        
        print(f"\n🔍 Searching for: '{query}' using {search_type} method...")
        
        try:
            results = self.service.search_products(query, search_type=search_type, top_k=top_k)
            
            if results:
                print(f"\n✅ Found {len(results)} results:")
                for i, product_id in enumerate(results, 1):
                    product = self.service.get_product_by_id(product_id)
                    if product:
                        print(f"\n{i}. {product.title} (ID: {product.id})")
                        print(f"   {product.description}")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    def add_product(self):
        """Interactive product addition."""
        print("\n➕ ADD NEW PRODUCT")
        print("-" * 30)
        
        product_id = input("Product ID: ").strip()
        if not product_id:
            print("❌ Product ID cannot be empty")
            return
        
        title = input("Product title: ").strip()
        if not title:
            print("❌ Product title cannot be empty")
            return
        
        description = input("Product description: ").strip()
        if not description:
            print("❌ Product description cannot be empty")
            return
        
        try:
            product = self.service.create_product(product_id, title, description)
            print(f"✅ Product created successfully!")
            print(f"   ID: {product.id}")
            print(f"   Title: {product.title}")
            print(f"   Description: {product.description}")
        except Exception as e:
            print(f"❌ Error creating product: {e}")
    
    def update_product(self):
        """Interactive product update."""
        print("\n✏️ UPDATE PRODUCT")
        print("-" * 30)
        
        product_id = input("Product ID to update: ").strip()
        if not product_id:
            print("❌ Product ID cannot be empty")
            return
        
        # Check if product exists
        existing_product = self.service.get_product_by_id(product_id)
        if not existing_product:
            print(f"❌ Product {product_id} not found")
            return
        
        print(f"\nCurrent product:")
        print(f"  Title: {existing_product.title}")
        print(f"  Description: {existing_product.description}")
        
        print(f"\nEnter new values (press Enter to keep current):")
        
        new_title = input(f"New title [{existing_product.title}]: ").strip()
        new_description = input(f"New description [{existing_product.description}]: ").strip()
        
        if not new_title and not new_description:
            print("❌ No changes provided")
            return
        
        try:
            updated_product = self.service.update_product(
                product_id,
                title=new_title if new_title else None,
                description=new_description if new_description else None
            )
            
            print(f"✅ Product updated successfully!")
            print(f"   Title: {updated_product.title}")
            print(f"   Description: {updated_product.description}")
            
        except Exception as e:
            print(f"❌ Error updating product: {e}")
    
    def delete_product(self):
        """Interactive product deletion."""
        print("\n🗑️ DELETE PRODUCT")
        print("-" * 30)
        
        product_id = input("Product ID to delete: ").strip()
        if not product_id:
            print("❌ Product ID cannot be empty")
            return
        
        # Check if product exists
        existing_product = self.service.get_product_by_id(product_id)
        if not existing_product:
            print(f"❌ Product {product_id} not found")
            return
        
        print(f"\nProduct to delete:")
        print(f"  ID: {existing_product.id}")
        print(f"  Title: {existing_product.title}")
        
        confirm = input("\nAre you sure you want to delete this product? (y/N): ").strip().lower()
        
        if confirm == 'y':
            try:
                self.service.delete_product(product_id)
                print(f"✅ Product {product_id} deleted successfully!")
            except Exception as e:
                print(f"❌ Error deleting product: {e}")
        else:
            print("❌ Deletion cancelled")
    
    def list_products(self):
        """List all products."""
        print("\n📋 ALL PRODUCTS")
        print("-" * 30)
        
        products = self.service.list_all_products()
        
        if products:
            print(f"Total products: {len(products)}\n")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.title} (ID: {product.id})")
                print(f"   {product.description[:100]}{'...' if len(product.description) > 100 else ''}")
                print()
        else:
            print("❌ No products found")
    
    def compare_search_methods(self):
        """Compare different search methods."""
        print("\n🔍 SEARCH METHOD COMPARISON")
        print("-" * 30)
        
        query = input("Enter search query: ").strip()
        if not query:
            print("❌ Query cannot be empty")
            return
        
        try:
            top_k = int(input("Number of results per method (default=3): ").strip() or "3")
        except ValueError:
            top_k = 3
        
        print(f"\n🔍 Comparing search methods for: '{query}'")
        print("-" * 50)
        
        methods = [
            ("Hybrid", "hybrid"),
            ("Semantic", "semantic"),
            ("Keyword", "keyword")
        ]
        
        for method_name, method_type in methods:
            try:
                results = self.service.search_products(query, search_type=method_type, top_k=top_k)
                
                print(f"\n{method_name} Search:")
                if results:
                    for i, product_id in enumerate(results, 1):
                        product = self.service.get_product_by_id(product_id)
                        if product:
                            print(f"  {i}. {product.title}")
                else:
                    print("  No results found")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    def test_custom_weights(self):
        """Test custom weight configurations."""
        print("\n⚖️ CUSTOM WEIGHT TESTING")
        print("-" * 30)
        
        query = input("Enter search query: ").strip()
        if not query:
            print("❌ Query cannot be empty")
            return
        
        try:
            bm25_weight = float(input("BM25 weight (0.0-1.0, default=0.4): ").strip() or "0.4")
            vector_weight = float(input("Vector weight (0.0-1.0, default=0.6): ").strip() or "0.6")
            top_k = int(input("Number of results (default=5): ").strip() or "5")
        except ValueError:
            print("❌ Invalid input. Using default values.")
            bm25_weight, vector_weight, top_k = 0.4, 0.6, 5
        
        print(f"\n🔍 Searching with custom weights:")
        print(f"   Query: '{query}'")
        print(f"   BM25 weight: {bm25_weight}")
        print(f"   Vector weight: {vector_weight}")
        
        try:
            results = self.service.search_products(
                query=query,
                search_type="hybrid",
                bm25_weight=bm25_weight,
                vector_weight=vector_weight,
                top_k=top_k
            )
            
            if results:
                print(f"\n✅ Found {len(results)} results:")
                for i, product_id in enumerate(results, 1):
                    product = self.service.get_product_by_id(product_id)
                    if product:
                        print(f"  {i}. {product.title}")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    def show_statistics(self):
        """Show system statistics."""
        print("\n📊 SYSTEM STATISTICS")
        print("-" * 30)
        
        try:
            stats = self.service.get_search_statistics()
            
            print(f"Total products: {stats['total_products']}")
            print(f"Vector index size: {stats['vector_index_size']}")
            print(f"BM25 index size: {stats['bm25_index_size']}")
            print(f"Vector dimension: {stats['vector_dimension']}")
            print(f"Default BM25 weight: {stats['default_weights']['bm25']}")
            print(f"Default vector weight: {stats['default_weights']['vector']}")
            print(f"Default top-k: {stats['default_top_k']}")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def show_help(self):
        """Show help information."""
        print("\n❓ HELP")
        print("-" * 30)
        print("This interactive demo allows you to explore the semantic search functionality:")
        print()
        print("🔍 SEARCH METHODS:")
        print("  • Hybrid: Combines keyword (BM25) and semantic (vector) search")
        print("  • Semantic: Uses only vector embeddings for meaning-based search")
        print("  • Keyword: Uses only BM25 for exact keyword matching")
        print()
        print("⚖️ SEARCH WEIGHTS:")
        print("  • BM25 weight: Controls keyword matching influence (0.0-1.0)")
        print("  • Vector weight: Controls semantic matching influence (0.0-1.0)")
        print("  • Weights are automatically normalized")
        print()
        print("💡 TIPS:")
        print("  • Try semantic search for conceptual queries like 'portable computer'")
        print("  • Use keyword search for exact phrase matching")
        print("  • Hybrid search usually provides the best overall results")
        print("  • Experiment with different weights to tune search behavior")
    
    def run(self):
        """Run the interactive demo."""
        print("🚀 Starting Semantic Search Interactive Demo...")
        print("Type 'help' or choose option 9 for guidance.")
        
        while True:
            self.display_menu()
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == "0":
                print("\n👋 Thank you for using the Semantic Search Demo!")
                break
            elif choice == "1":
                self.search_products()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.update_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "5":
                self.list_products()
            elif choice == "6":
                self.compare_search_methods()
            elif choice == "7":
                self.test_custom_weights()
            elif choice == "8":
                self.show_statistics()
            elif choice == "9":
                self.show_help()
            else:
                print("❌ Invalid choice. Please select 0-9.")
            
            input("\nPress Enter to continue...")

def main():
    print("=== Semantic Search Core Module - Interactive Demo ===\n")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        demo = InteractiveDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 