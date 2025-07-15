#!/usr/bin/env python3
"""
Comprehensive Search Methods Evaluation
Evaluates all search methods using Spanish tech product database with standard IR metrics
"""

import os
import sys
import time
from typing import List, Dict, Set
import asyncio
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.spanish_tech_products import get_all_products, get_test_queries
from core.services.product_service import ProductService
from core.evaluation.metrics import SearchEvaluator, OverallMetrics, format_metrics_table, explain_metrics
from core.config.settings import Settings
from core.models.product import Product


class SearchMethodsEvaluator:
    """
    Comprehensive evaluator for all search methods
    """
    
    def __init__(self):
        """Initialize evaluator with all necessary services"""
        print("🚀 Initializing Search Methods Evaluator...")
        
        # Initialize settings and services
        self.settings = Settings()
        self.product_service = ProductService()
        self.evaluator = SearchEvaluator()
        
        # Search methods to evaluate
        self.search_methods = [
            "semantic",      # Pure vector search
            "keyword",       # Pure BM25 search  
            "hybrid",        # Traditional weighted hybrid
            "rrf",          # Reciprocal Rank Fusion
            "balanced",     # Multi-stage balanced strategy
            "speed_first",  # Multi-stage speed-optimized
            "quality_first", # Multi-stage quality-optimized
            "rrf_only"      # Pure optimized RRF
        ]
        
        print(f"✅ Evaluator initialized with {len(self.search_methods)} search methods")
    
    def load_spanish_dataset(self):
        """Load the comprehensive Spanish tech product dataset"""
        print("\n📚 Loading Spanish Tech Product Dataset...")
        
        # Clear existing data
        self.product_service.clear_all_data()
        
        # Load products
        spanish_products = get_all_products()
        
        print(f"📦 Adding {len(spanish_products)} Spanish tech products...")
        
        for i, product_data in enumerate(spanish_products):
            self.product_service.create_product(
                id=product_data["id"],
                title=product_data["title"],
                description=product_data["description"]
            )
            
            if (i + 1) % 20 == 0:
                print(f"   ✅ Added {i + 1} products...")
        
        print(f"🎉 Successfully loaded {len(spanish_products)} products!")
        return len(spanish_products)
    
    def evaluate_single_query(self, query_data: Dict, method: str) -> tuple:
        """
        Evaluate a single query with a specific search method
        
        Returns: (retrieved_ids, execution_time_ms)
        """
        query = query_data["query"]
        
        # Measure execution time
        start_time = time.time()
        
        try:
            if method in ["semantic", "keyword", "hybrid", "rrf"]:
                # Use standard search_products method
                retrieved_ids = self.product_service.search_products(
                    query=query,
                    search_type=method,
                    top_k=10
                )
            else:
                # Use strategy-based search for multi-stage methods
                result_dict = self.product_service.search_with_strategy(
                    query=query,
                    strategy=method,
                    top_k=10
                )
                # Extract product IDs from the result dictionary
                retrieved_ids = result_dict.get("results", [])
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            return retrieved_ids, execution_time_ms
            
        except Exception as e:
            print(f"❌ Error evaluating query '{query}' with method '{method}': {e}")
            return [], 0.0
    
    def evaluate_all_methods(self):
        """
        Evaluate all search methods across all test queries
        """
        print("\n🔍 Starting Comprehensive Evaluation...")
        
        # Get test queries with ground truth
        test_queries = get_test_queries()
        print(f"📋 Evaluating {len(test_queries)} queries with {len(self.search_methods)} methods")
        print(f"📊 Query difficulty breakdown:")
        
        # Show query difficulty distribution
        difficulty_counts = {}
        for query_data in test_queries:
            diff = query_data.get("difficulty", "unknown")
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        for diff, count in sorted(difficulty_counts.items()):
            print(f"   {diff}: {count} queries")
        
        # Store results for each method
        all_method_results = {}
        all_evaluations = {}  # Store individual query evaluations for analysis
        
        for method in self.search_methods:
            print(f"\n🧪 Evaluating method: {method.upper()}")
            method_evaluations = []
            
            for i, query_data in enumerate(test_queries):
                query = query_data["query"]
                relevant_ids = set(query_data["relevant_ids"])
                
                # Evaluate this query with current method
                retrieved_ids, execution_time = self.evaluate_single_query(query_data, method)
                
                # Calculate metrics for this query
                query_eval = self.evaluator.evaluate_query(
                    query=query,
                    method=method,
                    retrieved_ids=retrieved_ids,
                    relevant_ids=relevant_ids,
                    execution_time_ms=execution_time
                )
                
                method_evaluations.append(query_eval)
                
                # Progress indicator
                if (i + 1) % 8 == 0:  # Updated for more queries
                    print(f"   ✅ Evaluated {i + 1}/{len(test_queries)} queries")
            
            # Store individual evaluations for difficulty analysis
            all_evaluations[method] = method_evaluations
            
            # Aggregate results for this method
            overall_metrics = self.evaluator.aggregate_results(method_evaluations)
            all_method_results[method] = overall_metrics
            
            print(f"   📊 {method}: NDCG@5={overall_metrics.mean_ndcg_at_5:.3f}, "
                  f"MAP={overall_metrics.mean_average_precision:.3f}, "
                  f"Time={overall_metrics.mean_execution_time_ms:.1f}ms")
        
        return all_method_results, all_evaluations
    
    def analyze_query_difficulty(self, all_evaluations: Dict[str, List]):
        """
        Analyze method performance by query difficulty
        """
        from data.spanish_tech_products import get_test_queries
        
        test_queries = get_test_queries()
        
        # Group queries by difficulty
        difficulty_groups = {}
        for i, query_data in enumerate(test_queries):
            difficulty = query_data.get("difficulty", "unknown")
            if difficulty not in difficulty_groups:
                difficulty_groups[difficulty] = []
            difficulty_groups[difficulty].append(i)
        
        print("\n📈 QUERY DIFFICULTY ANALYSIS")
        print("-" * 60)
        
        # Analyze performance by difficulty
        for difficulty, query_indices in difficulty_groups.items():
            if len(query_indices) < 2:  # Skip if too few queries
                continue
                
            print(f"\n🎯 {difficulty.upper()} queries ({len(query_indices)} queries):")
            
            # Calculate average NDCG@5 for each method on this difficulty
            method_scores = {}
            for method, evaluations in all_evaluations.items():
                scores = [evaluations[i].ndcg_at_k[5] for i in query_indices]
                avg_score = sum(scores) / len(scores)
                method_scores[method] = avg_score
            
            # Sort by performance
            sorted_methods = sorted(method_scores.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (method, score) in enumerate(sorted_methods[:3], 1):
                print(f"   {rank}. {method}: {score:.3f} NDCG@5")
    
    def generate_detailed_report(self, results: Dict[str, OverallMetrics], all_evaluations: Dict[str, List] = None):
        """
        Generate a comprehensive evaluation report
        """
        print("\n📊 GENERATING DETAILED EVALUATION REPORT")
        print("=" * 80)
        
        # Convert to list for formatting
        metrics_list = list(results.values())
        
        # Display comprehensive table
        table = format_metrics_table(metrics_list)
        print(table)
        
        # Query difficulty analysis
        if all_evaluations:
            self.analyze_query_difficulty(all_evaluations)
        
        # Performance analysis
        print("\n🏃‍♂️ PERFORMANCE ANALYSIS")
        print("-" * 40)
        
        fastest_method = min(results.values(), key=lambda m: m.mean_execution_time_ms)
        slowest_method = max(results.values(), key=lambda m: m.mean_execution_time_ms)
        
        print(f"⚡ Fastest method: {fastest_method.method} ({fastest_method.mean_execution_time_ms:.1f}ms)")
        print(f"🐌 Slowest method: {slowest_method.method} ({slowest_method.mean_execution_time_ms:.1f}ms)")
        
        # Quality analysis
        print("\n🎯 QUALITY ANALYSIS")
        print("-" * 40)
        
        best_ndcg = max(results.values(), key=lambda m: m.mean_ndcg_at_5)
        best_map = max(results.values(), key=lambda m: m.mean_average_precision)
        best_mrr = max(results.values(), key=lambda m: m.mean_reciprocal_rank)
        
        print(f"🏆 Best NDCG@5: {best_ndcg.method} ({best_ndcg.mean_ndcg_at_5:.4f})")
        print(f"🎯 Best MAP: {best_map.method} ({best_map.mean_average_precision:.4f})")
        print(f"⚡ Best MRR: {best_mrr.method} ({best_mrr.mean_reciprocal_rank:.4f})")
        
        # Performance spread analysis
        print("\n📊 PERFORMANCE VARIABILITY")
        print("-" * 40)
        
        ndcg_scores = [m.mean_ndcg_at_5 for m in results.values()]
        map_scores = [m.mean_average_precision for m in results.values()]
        
        print(f"NDCG@5 spread: {min(ndcg_scores):.3f} - {max(ndcg_scores):.3f} (range: {max(ndcg_scores) - min(ndcg_scores):.3f})")
        print(f"MAP spread: {min(map_scores):.3f} - {max(map_scores):.3f} (range: {max(map_scores) - min(map_scores):.3f})")
        
        # Method recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        
        # Find best overall method (balanced score)
        def overall_score(m):
            return (m.mean_ndcg_at_5 * 0.4 + 
                   m.mean_average_precision * 0.3 + 
                   m.mean_reciprocal_rank * 0.2 + 
                   (1 - min(m.mean_execution_time_ms / 1000, 1)) * 0.1)
        
        best_overall = max(results.values(), key=overall_score)
        
        print(f"🌟 Best Overall Method: {best_overall.method}")
        print(f"   Quality Score: {best_overall.mean_ndcg_at_5:.3f} NDCG@5")
        print(f"   Speed: {best_overall.mean_execution_time_ms:.1f}ms")
        print(f"   Use Case: Balanced performance for production")
        
        # Speed-focused recommendation
        fast_methods = [m for m in results.values() if m.mean_execution_time_ms < 200]
        if fast_methods:
            best_fast = max(fast_methods, key=lambda m: m.mean_ndcg_at_5)
            print(f"\n⚡ Best Fast Method: {best_fast.method}")
            print(f"   Quality Score: {best_fast.mean_ndcg_at_5:.3f} NDCG@5")
            print(f"   Speed: {best_fast.mean_execution_time_ms:.1f}ms")
            print(f"   Use Case: Real-time search with speed constraints")
        
        # Quality-focused recommendation
        quality_methods = [m for m in results.values() if m.mean_ndcg_at_5 > 0.6]
        if quality_methods:
            best_quality = max(quality_methods, key=lambda m: m.mean_ndcg_at_5)
            print(f"\n🎯 Best Quality Method: {best_quality.method}")
            print(f"   Quality Score: {best_quality.mean_ndcg_at_5:.3f} NDCG@5")
            print(f"   Speed: {best_quality.mean_execution_time_ms:.1f}ms")
            print(f"   Use Case: High-quality search for critical applications")
    
    def save_results_to_file(self, results: Dict[str, OverallMetrics]):
        """
        Save evaluation results to a timestamped file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("SEMANTIC SEARCH EVALUATION RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Dataset: Spanish Tech Products ({len(get_all_products())} items)\n")
            f.write(f"Queries: {len(get_test_queries())} test queries\n")
            f.write(f"Methods: {len(self.search_methods)} search methods\n\n")
            
            # Write metrics table
            metrics_list = list(results.values())
            f.write(format_metrics_table(metrics_list))
            
            # Write detailed metrics for each method
            f.write("\n\nDETAILED METRICS BY METHOD\n")
            f.write("=" * 50 + "\n")
            
            for method, metrics in results.items():
                f.write(f"\n{method.upper()}\n")
                f.write("-" * 20 + "\n")
                f.write(f"Precision@1:  {metrics.mean_precision_at_1:.4f}\n")
                f.write(f"Precision@3:  {metrics.mean_precision_at_3:.4f}\n")
                f.write(f"Precision@5:  {metrics.mean_precision_at_5:.4f}\n")
                f.write(f"Precision@10: {metrics.mean_precision_at_10:.4f}\n")
                f.write(f"NDCG@1:       {metrics.mean_ndcg_at_1:.4f}\n")
                f.write(f"NDCG@3:       {metrics.mean_ndcg_at_3:.4f}\n")
                f.write(f"NDCG@5:       {metrics.mean_ndcg_at_5:.4f}\n")
                f.write(f"NDCG@10:      {metrics.mean_ndcg_at_10:.4f}\n")
                f.write(f"MAP:          {metrics.mean_average_precision:.4f}\n")
                f.write(f"MRR:          {metrics.mean_reciprocal_rank:.4f}\n")
                f.write(f"Avg Time:     {metrics.mean_execution_time_ms:.1f}ms\n")
                f.write(f"Median Time:  {metrics.median_execution_time_ms:.1f}ms\n")
            
            # Metrics explanation
            f.write("\n\n" + explain_metrics())
        
        print(f"\n💾 Results saved to: {filename}")
        return filename


def main():
    """
    Main evaluation function
    """
    print("🚀 COMPREHENSIVE SEARCH METHODS EVALUATION")
    print("=" * 60)
    print("📊 Evaluating semantic search with Spanish tech products")
    print("🔍 Testing all search methods with standard IR metrics")
    print()
    
    try:
        # Initialize evaluator
        evaluator = SearchMethodsEvaluator()
        
        # Load dataset
        dataset_size = evaluator.load_spanish_dataset()
        
        # Run evaluation
        results, all_evaluations = evaluator.evaluate_all_methods()
        
        # Generate report
        evaluator.generate_detailed_report(results, all_evaluations)
        
        # Save results
        results_file = evaluator.save_results_to_file(results)
        
        # Display metrics explanation
        print("\n" + explain_metrics())
        
        print(f"\n🎉 EVALUATION COMPLETED SUCCESSFULLY!")
        print(f"📊 Evaluated {len(evaluator.search_methods)} methods")
        print(f"📚 Dataset: {dataset_size} Spanish tech products")
        print(f"📋 Queries: {len(get_test_queries())} test queries")
        print(f"💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 