from typing import List, Tuple, Dict, Optional
from ..repositories.vector_repository import VectorRepository
from ..repositories.bm25_repository import BM25Repository
from ..config.settings import settings
from .rrf_service import RRFService
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for orchestrating hybrid search operations."""
    
    def __init__(self, vector_repo: VectorRepository, bm25_repo: BM25Repository, rrf_service: Optional[RRFService] = None):
        """
        Initialize the search service.
        
        Args:
            vector_repo: Vector repository for semantic search
            bm25_repo: BM25 repository for keyword search
            rrf_service: RRF service for advanced fusion (optional)
        """
        self.vector_repo = vector_repo
        self.bm25_repo = bm25_repo
        self.rrf_service = rrf_service or RRFService()
    
    def hybrid_search(
        self,
        query: str,
        bm25_weight: float = None,
        vector_weight: float = None,
        top_k: int = None
    ) -> List[str]:
        """
        Perform hybrid search combining BM25 and vector search.
        
        Args:
            query: Search query
            bm25_weight: Weight for BM25 results (defaults to settings)
            vector_weight: Weight for vector results (defaults to settings)
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by combined score
            
        Raises:
            ValueError: If query is empty or weights are invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Use default values if not provided
        if bm25_weight is None:
            bm25_weight = settings.DEFAULT_BM25_WEIGHT
        if vector_weight is None:
            vector_weight = settings.DEFAULT_VECTOR_WEIGHT
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        # Validate weights
        if bm25_weight < 0 or vector_weight < 0:
            raise ValueError("Weights must be non-negative")
        
        total_weight = bm25_weight + vector_weight
        if total_weight == 0:
            raise ValueError("At least one weight must be positive")
        
        # Normalize weights
        bm25_weight = bm25_weight / total_weight
        vector_weight = vector_weight / total_weight
        
        logger.info(f"Performing hybrid search for query: '{query}' with weights BM25={bm25_weight:.2f}, Vector={vector_weight:.2f}")
        
        # Get results from both search methods
        # Request more results from each method to ensure good coverage
        search_k = min(top_k * 2, 50)  # Get more results for better ranking
        
        bm25_results = self.bm25_repo.search_keywords(query, k=search_k)
        vector_results = self.vector_repo.search_similar(query, k=search_k)
        
        # Combine scores
        combined_results = self.combine_scores(
            bm25_results, vector_results, [bm25_weight, vector_weight]
        )
        
        # Return top-k results
        return [product_id for product_id, _ in combined_results[:top_k]]
    
    def keyword_search(self, query: str, top_k: int = None) -> List[str]:
        """
        Perform keyword-only search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by BM25 score
            
        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing keyword search for query: '{query}'")
        
        results = self.bm25_repo.search_keywords(query, k=top_k)
        return [product_id for product_id, _ in results]
    
    def semantic_search(self, query: str, top_k: int = None) -> List[str]:
        """
        Perform semantic-only search using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by semantic similarity
            
        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing semantic search for query: '{query}'")
        
        results = self.vector_repo.search_similar(query, k=top_k)
        return [product_id for product_id, _ in results]
    
    def combine_scores(
        self,
        bm25_results: List[Tuple[str, float]],
        vector_results: List[Tuple[str, float]],
        weights: List[float]
    ) -> List[Tuple[str, float]]:
        """
        Combine scores from BM25 and vector search results.
        
        Args:
            bm25_results: List of (product_id, score) from BM25 search
            vector_results: List of (product_id, score) from vector search
            weights: [bm25_weight, vector_weight] normalized weights
            
        Returns:
            List of (product_id, combined_score) sorted by score descending
        """
        bm25_weight, vector_weight = weights
        
        # Normalize scores within each result set
        bm25_scores = self._normalize_scores(bm25_results)
        vector_scores = self._normalize_scores(vector_results)
        
        # Combine scores
        combined_scores: Dict[str, float] = {}
        
        # Add BM25 scores
        for product_id, score in bm25_scores.items():
            combined_scores[product_id] = combined_scores.get(product_id, 0) + (score * bm25_weight)
        
        # Add vector scores
        for product_id, score in vector_scores.items():
            combined_scores[product_id] = combined_scores.get(product_id, 0) + (score * vector_weight)
        
        # Sort by combined score (descending)
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results
    
    def _normalize_scores(self, results: List[Tuple[str, float]]) -> Dict[str, float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        
        Args:
            results: List of (product_id, score) tuples
            
        Returns:
            Dictionary of product_id -> normalized_score
        """
        if not results:
            return {}
        
        scores = [score for _, score in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        if max_score == min_score:
            return {product_id: 1.0 for product_id, _ in results}
        
        # Min-max normalization
        normalized = {}
        for product_id, score in results:
            normalized_score = (score - min_score) / (max_score - min_score)
            normalized[product_id] = normalized_score
        
        return normalized
    
    def rrf_search(
        self,
        query: str,
        k: int = None,
        top_k: int = None
    ) -> List[str]:
        """
        Perform search using Reciprocal Rank Fusion (RRF).
        
        Args:
            query: Search query
            k: RRF parameter (higher values reduce impact of rank differences)
            top_k: Number of results to return
            
        Returns:
            List of product IDs ranked by RRF score
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Use optimized RRF k value (lower = more aggressive fusion)
        if k is None:
            k = 20  # Optimized value: more aggressive than standard 60
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing RRF search for query: '{query}' with k={k}")
        
        # Use larger and more balanced retrieval for better fusion
        retrieval_limit = max(top_k * 5, 100)  # Increased from 3x to 5x
        
        # Get BM25 results
        bm25_results = self.keyword_search(query, top_k=retrieval_limit)
        logger.debug(f"BM25 search returned {len(bm25_results)} results")
        
        # Get vector results
        vector_results = self.semantic_search(query, top_k=retrieval_limit)
        logger.debug(f"Vector search returned {len(vector_results)} results")
        
        # Apply RRF fusion with optimized parameters
        final_results = self.rrf_service.combine_search_results(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=k,
            top_k=top_k
        )
        
        logger.info(f"RRF search completed: {len(final_results)} final results")
        return final_results

    def get_search_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the search indexes.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "vector_index_size": self.vector_repo.get_product_count(),
            "bm25_index_size": self.bm25_repo.get_product_count(),
            "total_products": max(
                self.vector_repo.get_product_count(),
                self.bm25_repo.get_product_count()
            )
        } 