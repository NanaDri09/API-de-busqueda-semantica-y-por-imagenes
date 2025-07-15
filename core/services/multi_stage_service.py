"""
Multi-Stage Search Service

Orchestrates multi-stage search pipelines with progressive filtering and reranking.
"""

from typing import List, Dict, Any, Optional
import logging
import time

from ..models.search_config import (
    MultiStageConfig, SearchStage, SearchMethod, SearchStrategy,
    get_strategy_config, list_available_strategies
)
from .rrf_service import RRFService

logger = logging.getLogger(__name__)


class MultiStageService:
    """Service for orchestrating multi-stage search pipelines."""
    
    def __init__(self, rrf_service: RRFService):
        """
        Initialize multi-stage service.
        
        Args:
            rrf_service: RRF service instance for fusion operations
        """
        self.rrf_service = rrf_service
    
    def execute_strategy(
        self,
        query: str,
        strategy: SearchStrategy,
        search_methods: Dict[str, Any],
        custom_config: Optional[MultiStageConfig] = None
    ) -> Dict[str, Any]:
        """
        Execute a predefined search strategy.
        
        Args:
            query: Search query
            strategy: Predefined strategy to use
            search_methods: Dictionary with search method implementations
            custom_config: Optional custom configuration (overrides predefined)
            
        Returns:
            Dictionary with search results and metadata
        """
        start_time = time.time()
        
        # Get strategy configuration
        if custom_config:
            config = custom_config
            logger.info(f"Using custom multi-stage configuration with {len(config.stages)} stages")
        else:
            strategy_config = get_strategy_config(strategy)
            config = strategy_config.config
            logger.info(f"Executing strategy: {strategy_config.name}")
        
        # Execute multi-stage pipeline
        result = self.execute_multi_stage(query, config, search_methods)
        
        # Add strategy metadata
        execution_time = (time.time() - start_time) * 1000
        result.update({
            "strategy": strategy.value if not custom_config else "custom",
            "execution_time_ms": execution_time,
            "stages_executed": len(config.stages)
        })
        
        return result
    
    def execute_multi_stage(
        self,
        query: str,
        config: MultiStageConfig,
        search_methods: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute multi-stage search pipeline.
        
        Args:
            query: Search query
            config: Multi-stage configuration
            search_methods: Dictionary with search method implementations
                Expected keys: 'bm25_search', 'vector_search', 'hybrid_search'
                
        Returns:
            Dictionary with final results and stage information
        """
        logger.info(f"Starting multi-stage search with {len(config.stages)} stages")
        
        current_candidates = None
        stage_results = []
        
        for stage_idx, stage in enumerate(config.stages):
            stage_start = time.time()
            
            logger.debug(f"Executing stage {stage_idx + 1}: {stage.method.value} (limit: {stage.limit})")
            
            # Execute stage
            stage_result = self._execute_stage(
                query=query,
                stage=stage,
                search_methods=search_methods,
                previous_candidates=current_candidates
            )
            
            # Update candidates for next stage
            current_candidates = stage_result["candidates"]
            
            # Record stage metadata
            stage_time = (time.time() - stage_start) * 1000
            stage_info = {
                "stage": stage_idx + 1,
                "method": stage.method.value,
                "limit": stage.limit,
                "results_count": len(current_candidates),
                "execution_time_ms": stage_time,
                "description": stage.description
            }
            stage_results.append(stage_info)
            
            logger.debug(f"Stage {stage_idx + 1} completed: {len(current_candidates)} results in {stage_time:.1f}ms")
        
        # Apply final limit
        final_results = current_candidates[:config.final_limit]
        
        return {
            "results": final_results,
            "total_results": len(final_results),
            "stage_details": stage_results,
            "final_limit": config.final_limit,
            "description": config.description
        }
    
    def _execute_stage(
        self,
        query: str,
        stage: SearchStage,
        search_methods: Dict[str, Any],
        previous_candidates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single search stage.
        
        Args:
            query: Search query
            stage: Stage configuration
            search_methods: Available search method implementations
            previous_candidates: Results from previous stage (for reranking)
            
        Returns:
            Dictionary with stage results
        """
        if stage.method == SearchMethod.BM25:
            return self._execute_bm25_stage(query, stage, search_methods, previous_candidates)
        elif stage.method == SearchMethod.VECTOR:
            return self._execute_vector_stage(query, stage, search_methods, previous_candidates)
        elif stage.method == SearchMethod.HYBRID:
            return self._execute_hybrid_stage(query, stage, search_methods, previous_candidates)
        elif stage.method == SearchMethod.RRF:
            return self._execute_rrf_stage(query, stage, search_methods, previous_candidates)
        else:
            raise ValueError(f"Unknown search method: {stage.method}")
    
    def _execute_bm25_stage(
        self,
        query: str,
        stage: SearchStage,
        search_methods: Dict[str, Any],
        previous_candidates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute BM25 search stage."""
        bm25_search = search_methods.get("bm25_search")
        if not bm25_search:
            raise ValueError("BM25 search method not available")
        
        if previous_candidates is not None:
            # Rerank previous candidates using BM25
            logger.debug(f"Reranking {len(previous_candidates)} candidates with BM25")
            # For reranking, we would need a different method that scores specific candidates
            # For now, just return top candidates from previous stage
            candidates = previous_candidates[:stage.limit]
        else:
            # Initial BM25 search
            candidates = bm25_search(query, top_k=stage.limit)
        
        return {"candidates": candidates, "method": "bm25"}
    
    def _execute_vector_stage(
        self,
        query: str,
        stage: SearchStage,
        search_methods: Dict[str, Any],
        previous_candidates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute vector search stage."""
        vector_search = search_methods.get("vector_search")
        if not vector_search:
            raise ValueError("Vector search method not available")
        
        if previous_candidates is not None:
            # Rerank previous candidates using vector similarity
            logger.debug(f"Reranking {len(previous_candidates)} candidates with vector search")
            # For reranking, we would need a different method that scores specific candidates
            # For now, just return top candidates from previous stage
            candidates = previous_candidates[:stage.limit]
        else:
            # Initial vector search
            candidates = vector_search(query, top_k=stage.limit)
        
        return {"candidates": candidates, "method": "vector"}
    
    def _execute_hybrid_stage(
        self,
        query: str,
        stage: SearchStage,
        search_methods: Dict[str, Any],
        previous_candidates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute hybrid search stage."""
        hybrid_search = search_methods.get("hybrid_search")
        if not hybrid_search:
            raise ValueError("Hybrid search method not available")
        
        # Use stage-specific weights if provided
        bm25_weight = stage.bm25_weight or 0.4
        vector_weight = stage.vector_weight or 0.6
        
        if previous_candidates is not None:
            # For reranking, we would apply hybrid scoring to previous candidates
            logger.debug(f"Reranking {len(previous_candidates)} candidates with hybrid search")
            candidates = previous_candidates[:stage.limit]
        else:
            # Initial hybrid search
            candidates = hybrid_search(
                query, 
                top_k=stage.limit,
                bm25_weight=bm25_weight,
                vector_weight=vector_weight
            )
        
        return {"candidates": candidates, "method": "hybrid"}
    
    def _execute_rrf_stage(
        self,
        query: str,
        stage: SearchStage,
        search_methods: Dict[str, Any],
        previous_candidates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute RRF fusion stage."""
        bm25_search = search_methods.get("bm25_search")
        vector_search = search_methods.get("vector_search")
        
        if not bm25_search or not vector_search:
            raise ValueError("Both BM25 and vector search methods required for RRF")
        
        rrf_k = stage.rrf_k or 20  # Use optimized default
        
        if previous_candidates is not None:
            # Apply RRF to previous candidates
            logger.debug(f"Applying RRF to {len(previous_candidates)} candidates")
            # For now, just return top candidates
            candidates = previous_candidates[:stage.limit]
        else:
            # Get separate results and apply RRF
            # Use a larger limit for initial retrieval to give RRF more options
            retrieval_limit = max(stage.limit * 3, 50)
            
            bm25_results = bm25_search(query, top_k=retrieval_limit)
            vector_results = vector_search(query, top_k=retrieval_limit)
            
            # Apply RRF fusion
            candidates = self.rrf_service.combine_search_results(
                bm25_results=bm25_results,
                vector_results=vector_results,
                k=rrf_k,
                top_k=stage.limit
            )
        
        return {"candidates": candidates, "method": "rrf"}
    
    def two_stage_search(
        self,
        query: str,
        stage1_method: SearchMethod,
        stage2_method: SearchMethod,
        stage1_limit: int = 50,
        stage2_limit: int = 10,
        search_methods: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Simple two-stage search implementation.
        
        Args:
            query: Search query
            stage1_method: First stage search method
            stage2_method: Second stage search method  
            stage1_limit: Number of candidates from stage 1
            stage2_limit: Final number of results
            search_methods: Available search method implementations
            
        Returns:
            Dictionary with search results and metadata
        """
        from ..models.search_config import SearchStage, MultiStageConfig
        
        # Create simple two-stage configuration
        stages = [
            SearchStage(method=stage1_method, limit=stage1_limit),
            SearchStage(method=stage2_method, limit=stage2_limit)
        ]
        
        config = MultiStageConfig(
            stages=stages,
            final_limit=stage2_limit,
            description=f"Two-stage: {stage1_method.value} → {stage2_method.value}"
        )
        
        return self.execute_multi_stage(query, config, search_methods)
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of available predefined strategies.
        
        Returns:
            List of strategy information dictionaries
        """
        strategies = list_available_strategies()
        return [
            {
                "name": strategy.name,
                "type": strategy.strategy_type.value,
                "description": strategy.description,
                "expected_latency_ms": strategy.expected_latency_ms,
                "memory_usage": strategy.memory_usage,
                "quality_score": strategy.quality_score,
                "stages": len(strategy.config.stages)
            }
            for strategy in strategies
        ] 