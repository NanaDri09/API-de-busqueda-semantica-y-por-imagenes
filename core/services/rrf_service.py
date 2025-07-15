"""
Reciprocal Rank Fusion (RRF) Service

Implements the RRF algorithm for combining multiple ranked search results.
RRF is the industry standard for hybrid search result fusion.
"""

from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RRFService:
    """Service for implementing Reciprocal Rank Fusion algorithm."""
    
    def __init__(self, default_k: int = 60):
        """
        Initialize RRF service.
        
        Args:
            default_k: RRF parameter k (higher values reduce impact of rank differences)
        """
        self.default_k = default_k
    
    def reciprocal_rank_fusion(
        self, 
        ranked_lists: List[List[Tuple[str, float]]], 
        k: int = None
    ) -> List[Tuple[str, float]]:
        """
        Combine multiple ranked lists using Reciprocal Rank Fusion.
        
        The RRF formula for each document is:
        RRF_score(d) = Σ(1 / (k + rank_i(d))) for all lists i where d appears
        
        Args:
            ranked_lists: List of ranked result lists, each containing (doc_id, score) tuples
            k: RRF parameter (default uses instance default)
            
        Returns:
            List of (doc_id, rrf_score) tuples sorted by RRF score descending
        """
        if k is None:
            k = self.default_k
        
        if not ranked_lists:
            return []
        
        # Dictionary to accumulate RRF scores for each document
        rrf_scores: Dict[str, float] = {}
        
        # Process each ranked list
        for list_idx, ranked_list in enumerate(ranked_lists):
            logger.debug(f"Processing ranked list {list_idx + 1} with {len(ranked_list)} items")
            
            for rank, (doc_id, original_score) in enumerate(ranked_list, start=1):
                # Calculate RRF contribution: 1 / (k + rank)
                rrf_contribution = 1.0 / (k + rank)
                
                # Accumulate RRF score
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                rrf_scores[doc_id] += rrf_contribution
        
        # Sort by RRF score (descending) and return
        result = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"RRF fusion complete: combined {len(ranked_lists)} lists into {len(result)} unique results")
        return result
    
    def combine_search_results(
        self,
        bm25_results: List[str],
        vector_results: List[str],
        k: int = None,
        top_k: int = 10
    ) -> List[str]:
        """
        Combine BM25 and vector search results using RRF.
        
        Args:
            bm25_results: List of document IDs from BM25 search (in rank order)
            vector_results: List of document IDs from vector search (in rank order)
            k: RRF parameter
            top_k: Number of final results to return
            
        Returns:
            List of document IDs ranked by RRF score
        """
        if k is None:
            k = self.default_k
        
        # Convert to ranked lists format (doc_id, dummy_score)
        bm25_ranked = [(doc_id, 1.0) for doc_id in bm25_results]
        vector_ranked = [(doc_id, 1.0) for doc_id in vector_results]
        
        # Apply RRF
        rrf_results = self.reciprocal_rank_fusion([bm25_ranked, vector_ranked], k=k)
        
        # Return top_k document IDs
        return [doc_id for doc_id, score in rrf_results[:top_k]]
    
    def combine_multiple_searches(
        self,
        search_results: Dict[str, List[str]],
        k: int = None,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Combine multiple search results from different methods using RRF.
        
        Args:
            search_results: Dictionary mapping search method name to list of doc IDs
            k: RRF parameter
            top_k: Number of final results to return
            
        Returns:
            List of (doc_id, rrf_score) tuples
        """
        if k is None:
            k = self.default_k
        
        # Convert all results to ranked lists format
        ranked_lists = []
        for method_name, doc_ids in search_results.items():
            ranked_list = [(doc_id, 1.0) for doc_id in doc_ids]
            ranked_lists.append(ranked_list)
            logger.debug(f"Added {len(ranked_list)} results from {method_name}")
        
        # Apply RRF
        rrf_results = self.reciprocal_rank_fusion(ranked_lists, k=k)
        
        # Return top_k results
        return rrf_results[:top_k]
    
    def get_rrf_weights(
        self,
        ranked_lists: List[List[Tuple[str, float]]],
        doc_id: str,
        k: int = None
    ) -> Dict[str, float]:
        """
        Get the RRF weight contributions for a specific document from each ranked list.
        Useful for debugging and understanding RRF scoring.
        
        Args:
            ranked_lists: List of ranked result lists
            doc_id: Document ID to analyze
            k: RRF parameter
            
        Returns:
            Dictionary mapping list index to RRF contribution
        """
        if k is None:
            k = self.default_k
        
        contributions = {}
        
        for list_idx, ranked_list in enumerate(ranked_lists):
            for rank, (current_doc_id, score) in enumerate(ranked_list, start=1):
                if current_doc_id == doc_id:
                    contribution = 1.0 / (k + rank)
                    contributions[f"list_{list_idx}"] = {
                        "rank": rank,
                        "contribution": contribution
                    }
                    break
        
        return contributions 