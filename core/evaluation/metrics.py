#!/usr/bin/env python3
"""
Information Retrieval Evaluation Metrics
Implements standard metrics for evaluating search quality
"""

import math
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import statistics


@dataclass
class SearchResult:
    """Single search result with score"""
    product_id: str
    score: float
    rank: int


@dataclass
class QueryEvaluation:
    """Evaluation results for a single query"""
    query: str
    method: str
    relevant_ids: Set[str]
    retrieved_ids: List[str]
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    f1_at_k: Dict[int, float]
    ndcg_at_k: Dict[int, float]
    average_precision: float
    reciprocal_rank: float
    execution_time_ms: float


@dataclass
class OverallMetrics:
    """Aggregated evaluation metrics across all queries"""
    method: str
    num_queries: int
    
    # Precision metrics
    mean_precision_at_1: float
    mean_precision_at_3: float
    mean_precision_at_5: float
    mean_precision_at_10: float
    
    # Recall metrics
    mean_recall_at_1: float
    mean_recall_at_3: float
    mean_recall_at_5: float
    mean_recall_at_10: float
    
    # F1 metrics
    mean_f1_at_1: float
    mean_f1_at_3: float
    mean_f1_at_5: float
    mean_f1_at_10: float
    
    # NDCG metrics
    mean_ndcg_at_1: float
    mean_ndcg_at_3: float
    mean_ndcg_at_5: float
    mean_ndcg_at_10: float
    
    # Other metrics
    mean_average_precision: float  # MAP
    mean_reciprocal_rank: float   # MRR
    
    # Performance
    mean_execution_time_ms: float
    median_execution_time_ms: float
    

class SearchEvaluator:
    """
    Evaluates search methods using standard Information Retrieval metrics
    """
    
    def __init__(self, k_values: List[int] = None):
        """
        Initialize evaluator
        
        Args:
            k_values: List of k values for Precision@k, Recall@k, etc.
        """
        self.k_values = k_values or [1, 3, 5, 10]
    
    def precision_at_k(self, retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate Precision@k
        
        Precision@k = (# relevant items in top k) / k
        """
        if k == 0 or len(retrieved) == 0:
            return 0.0
        
        top_k = retrieved[:k]
        relevant_in_k = len([item for item in top_k if item in relevant])
        return relevant_in_k / min(k, len(top_k))
    
    def recall_at_k(self, retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate Recall@k
        
        Recall@k = (# relevant items in top k) / (total # relevant items)
        """
        if len(relevant) == 0:
            return 0.0
        
        top_k = retrieved[:k]
        relevant_in_k = len([item for item in top_k if item in relevant])
        return relevant_in_k / len(relevant)
    
    def f1_at_k(self, precision_k: float, recall_k: float) -> float:
        """
        Calculate F1@k score
        
        F1@k = 2 * (Precision@k * Recall@k) / (Precision@k + Recall@k)
        """
        if precision_k + recall_k == 0:
            return 0.0
        return 2 * (precision_k * recall_k) / (precision_k + recall_k)
    
    def dcg_at_k(self, retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate Discounted Cumulative Gain@k
        
        DCG@k = sum(rel_i / log2(i + 1)) for i in 1..k
        For binary relevance: rel_i = 1 if relevant, 0 otherwise
        """
        dcg = 0.0
        for i, item in enumerate(retrieved[:k]):
            if item in relevant:
                # Binary relevance: relevant = 1, not relevant = 0
                dcg += 1.0 / math.log2(i + 2)  # i+2 because i is 0-indexed
        return dcg
    
    def idcg_at_k(self, relevant: Set[str], k: int) -> float:
        """
        Calculate Ideal Discounted Cumulative Gain@k
        
        IDCG@k = DCG if we had perfect ranking (all relevant items first)
        """
        num_relevant = min(len(relevant), k)
        idcg = 0.0
        for i in range(num_relevant):
            idcg += 1.0 / math.log2(i + 2)
        return idcg
    
    def ndcg_at_k(self, retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain@k
        
        NDCG@k = DCG@k / IDCG@k
        """
        dcg = self.dcg_at_k(retrieved, relevant, k)
        idcg = self.idcg_at_k(relevant, k)
        
        if idcg == 0:
            return 0.0
        return dcg / idcg
    
    def average_precision(self, retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate Average Precision (AP)
        
        AP = (1/|relevant|) * sum(Precision@k * rel_k) for k in 1..n
        where rel_k = 1 if item at rank k is relevant, 0 otherwise
        """
        if len(relevant) == 0:
            return 0.0
        
        precision_sum = 0.0
        relevant_count = 0
        
        for k, item in enumerate(retrieved, 1):
            if item in relevant:
                relevant_count += 1
                precision_at_this_k = relevant_count / k
                precision_sum += precision_at_this_k
        
        return precision_sum / len(relevant)
    
    def reciprocal_rank(self, retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate Reciprocal Rank (RR)
        
        RR = 1 / rank_of_first_relevant_item
        Returns 0 if no relevant items found
        """
        for rank, item in enumerate(retrieved, 1):
            if item in relevant:
                return 1.0 / rank
        return 0.0
    
    def evaluate_query(
        self, 
        query: str,
        method: str,
        retrieved_ids: List[str],
        relevant_ids: Set[str],
        execution_time_ms: float
    ) -> QueryEvaluation:
        """
        Evaluate a single query with comprehensive metrics
        """
        # Calculate all metrics
        precision_at_k = {}
        recall_at_k = {}
        f1_at_k = {}
        ndcg_at_k = {}
        
        for k in self.k_values:
            prec_k = self.precision_at_k(retrieved_ids, relevant_ids, k)
            rec_k = self.recall_at_k(retrieved_ids, relevant_ids, k)
            
            precision_at_k[k] = prec_k
            recall_at_k[k] = rec_k
            f1_at_k[k] = self.f1_at_k(prec_k, rec_k)
            ndcg_at_k[k] = self.ndcg_at_k(retrieved_ids, relevant_ids, k)
        
        avg_precision = self.average_precision(retrieved_ids, relevant_ids)
        rr = self.reciprocal_rank(retrieved_ids, relevant_ids)
        
        return QueryEvaluation(
            query=query,
            method=method,
            relevant_ids=relevant_ids,
            retrieved_ids=retrieved_ids,
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            f1_at_k=f1_at_k,
            ndcg_at_k=ndcg_at_k,
            average_precision=avg_precision,
            reciprocal_rank=rr,
            execution_time_ms=execution_time_ms
        )
    
    def aggregate_results(self, evaluations: List[QueryEvaluation]) -> OverallMetrics:
        """
        Aggregate evaluation results across multiple queries
        """
        if not evaluations:
            raise ValueError("No evaluations provided")
        
        method = evaluations[0].method
        num_queries = len(evaluations)
        
        # Aggregate precision metrics
        mean_prec_1 = statistics.mean([e.precision_at_k[1] for e in evaluations])
        mean_prec_3 = statistics.mean([e.precision_at_k[3] for e in evaluations])
        mean_prec_5 = statistics.mean([e.precision_at_k[5] for e in evaluations])
        mean_prec_10 = statistics.mean([e.precision_at_k[10] for e in evaluations])
        
        # Aggregate recall metrics
        mean_rec_1 = statistics.mean([e.recall_at_k[1] for e in evaluations])
        mean_rec_3 = statistics.mean([e.recall_at_k[3] for e in evaluations])
        mean_rec_5 = statistics.mean([e.recall_at_k[5] for e in evaluations])
        mean_rec_10 = statistics.mean([e.recall_at_k[10] for e in evaluations])
        
        # Aggregate F1 metrics
        mean_f1_1 = statistics.mean([e.f1_at_k[1] for e in evaluations])
        mean_f1_3 = statistics.mean([e.f1_at_k[3] for e in evaluations])
        mean_f1_5 = statistics.mean([e.f1_at_k[5] for e in evaluations])
        mean_f1_10 = statistics.mean([e.f1_at_k[10] for e in evaluations])
        
        # Aggregate NDCG metrics
        mean_ndcg_1 = statistics.mean([e.ndcg_at_k[1] for e in evaluations])
        mean_ndcg_3 = statistics.mean([e.ndcg_at_k[3] for e in evaluations])
        mean_ndcg_5 = statistics.mean([e.ndcg_at_k[5] for e in evaluations])
        mean_ndcg_10 = statistics.mean([e.ndcg_at_k[10] for e in evaluations])
        
        # Aggregate other metrics
        map_score = statistics.mean([e.average_precision for e in evaluations])
        mrr_score = statistics.mean([e.reciprocal_rank for e in evaluations])
        
        # Performance metrics
        execution_times = [e.execution_time_ms for e in evaluations]
        mean_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        
        return OverallMetrics(
            method=method,
            num_queries=num_queries,
            mean_precision_at_1=mean_prec_1,
            mean_precision_at_3=mean_prec_3,
            mean_precision_at_5=mean_prec_5,
            mean_precision_at_10=mean_prec_10,
            mean_recall_at_1=mean_rec_1,
            mean_recall_at_3=mean_rec_3,
            mean_recall_at_5=mean_rec_5,
            mean_recall_at_10=mean_rec_10,
            mean_f1_at_1=mean_f1_1,
            mean_f1_at_3=mean_f1_3,
            mean_f1_at_5=mean_f1_5,
            mean_f1_at_10=mean_f1_10,
            mean_ndcg_at_1=mean_ndcg_1,
            mean_ndcg_at_3=mean_ndcg_3,
            mean_ndcg_at_5=mean_ndcg_5,
            mean_ndcg_at_10=mean_ndcg_10,
            mean_average_precision=map_score,
            mean_reciprocal_rank=mrr_score,
            mean_execution_time_ms=mean_time,
            median_execution_time_ms=median_time
        )


def format_metrics_table(metrics: List[OverallMetrics]) -> str:
    """
    Format multiple OverallMetrics objects into a readable table
    """
    if not metrics:
        return "No metrics to display"
    
    # Header
    table = "\n📊 COMPREHENSIVE EVALUATION RESULTS\n"
    table += "=" * 80 + "\n\n"
    
    # Method comparison table
    table += f"{'Method':<15} {'P@1':<6} {'P@3':<6} {'P@5':<6} {'NDCG@5':<8} {'MAP':<7} {'MRR':<7} {'Time(ms)':<10}\n"
    table += "-" * 80 + "\n"
    
    for metric in metrics:
        table += f"{metric.method:<15} "
        table += f"{metric.mean_precision_at_1:.3f}  "
        table += f"{metric.mean_precision_at_3:.3f}  "
        table += f"{metric.mean_precision_at_5:.3f}  "
        table += f"{metric.mean_ndcg_at_5:.3f}    "
        table += f"{metric.mean_average_precision:.3f}   "
        table += f"{metric.mean_reciprocal_rank:.3f}   "
        table += f"{metric.mean_execution_time_ms:.1f}\n"
    
    # Detailed metrics for best method
    best_method = max(metrics, key=lambda m: m.mean_ndcg_at_5)
    table += "\n🏆 BEST METHOD DETAILED METRICS\n"
    table += f"Method: {best_method.method}\n"
    table += f"Queries evaluated: {best_method.num_queries}\n\n"
    
    table += "Precision Metrics:\n"
    table += f"  P@1:  {best_method.mean_precision_at_1:.4f}\n"
    table += f"  P@3:  {best_method.mean_precision_at_3:.4f}\n"
    table += f"  P@5:  {best_method.mean_precision_at_5:.4f}\n"
    table += f"  P@10: {best_method.mean_precision_at_10:.4f}\n\n"
    
    table += "Recall Metrics:\n"
    table += f"  R@1:  {best_method.mean_recall_at_1:.4f}\n"
    table += f"  R@3:  {best_method.mean_recall_at_3:.4f}\n"
    table += f"  R@5:  {best_method.mean_recall_at_5:.4f}\n"
    table += f"  R@10: {best_method.mean_recall_at_10:.4f}\n\n"
    
    table += "NDCG Metrics:\n"
    table += f"  NDCG@1:  {best_method.mean_ndcg_at_1:.4f}\n"
    table += f"  NDCG@3:  {best_method.mean_ndcg_at_3:.4f}\n"
    table += f"  NDCG@5:  {best_method.mean_ndcg_at_5:.4f}\n"
    table += f"  NDCG@10: {best_method.mean_ndcg_at_10:.4f}\n\n"
    
    table += "Overall Quality:\n"
    table += f"  MAP (Mean Average Precision): {best_method.mean_average_precision:.4f}\n"
    table += f"  MRR (Mean Reciprocal Rank):   {best_method.mean_reciprocal_rank:.4f}\n\n"
    
    table += "Performance:\n"
    table += f"  Mean execution time:   {best_method.mean_execution_time_ms:.1f}ms\n"
    table += f"  Median execution time: {best_method.median_execution_time_ms:.1f}ms\n"
    
    return table


def explain_metrics() -> str:
    """
    Return explanation of all metrics used
    """
    explanation = """
📚 METRICS EXPLANATION

🎯 PRECISION@K
- Measures accuracy of top K results
- P@5 = (relevant items in top 5) / 5
- Higher = better, Range: 0.0-1.0

📈 RECALL@K  
- Measures coverage of relevant items in top K
- R@5 = (relevant items in top 5) / (total relevant items)
- Higher = better, Range: 0.0-1.0

⚖️ F1@K
- Harmonic mean of Precision@K and Recall@K
- Balances precision and recall
- Higher = better, Range: 0.0-1.0

🏆 NDCG@K (Normalized Discounted Cumulative Gain)
- Considers ranking quality with position-based discounting
- Higher-ranked relevant items contribute more to the score
- Most important metric for ranking quality
- Higher = better, Range: 0.0-1.0

📊 MAP (Mean Average Precision)
- Average of precision values at each relevant item
- Single-number summary of precision across all ranks
- Higher = better, Range: 0.0-1.0

⚡ MRR (Mean Reciprocal Rank)  
- Average of reciprocal ranks of first relevant items
- MRR = 1/rank_of_first_relevant_item
- Emphasizes finding relevant items quickly
- Higher = better, Range: 0.0-1.0

🕒 EXECUTION TIME
- Time taken to execute search
- Lower = better (faster search)
- Measured in milliseconds

🎖️ INTERPRETATION GUIDE:
- NDCG@5 > 0.8: Excellent ranking quality
- NDCG@5 > 0.6: Good ranking quality  
- NDCG@5 > 0.4: Fair ranking quality
- NDCG@5 < 0.4: Poor ranking quality

- MAP > 0.7: Excellent precision
- MAP > 0.5: Good precision
- MAP > 0.3: Fair precision
- MAP < 0.3: Poor precision
"""
    return explanation 