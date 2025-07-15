"""
Search Configuration Models

Defines configuration structures for multi-stage search and search strategies.
"""

from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass
from enum import Enum


class SearchMethod(str, Enum):
    """Available search methods."""
    BM25 = "bm25"
    VECTOR = "vector"
    HYBRID = "hybrid"
    RRF = "rrf"


class SearchStrategy(str, Enum):
    """Predefined search strategies."""
    SPEED_FIRST = "speed_first"      # BM25 → Vector reranking
    QUALITY_FIRST = "quality_first"  # Vector → BM25 reranking
    BALANCED = "balanced"            # Parallel → RRF combination
    RRF_ONLY = "rrf_only"           # Pure RRF approach


@dataclass
class SearchStage:
    """Configuration for a single search stage."""
    method: SearchMethod
    limit: int
    description: Optional[str] = None
    
    # Method-specific parameters
    bm25_weight: Optional[float] = None
    vector_weight: Optional[float] = None
    rrf_k: Optional[int] = None
    
    def __post_init__(self):
        """Validate stage configuration."""
        if self.limit <= 0:
            raise ValueError("Stage limit must be positive")
        
        if self.method == SearchMethod.HYBRID:
            if self.bm25_weight is None or self.vector_weight is None:
                # Use defaults
                self.bm25_weight = 0.4
                self.vector_weight = 0.6
        
        if self.method == SearchMethod.RRF:
            if self.rrf_k is None:
                self.rrf_k = 60


@dataclass
class MultiStageConfig:
    """Configuration for multi-stage search pipeline."""
    stages: List[SearchStage]
    final_limit: int = 10
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate multi-stage configuration."""
        if not self.stages:
            raise ValueError("At least one stage is required")
        
        if self.final_limit <= 0:
            raise ValueError("Final limit must be positive")
        
        # Validate that stages have decreasing limits (generally recommended)
        for i in range(1, len(self.stages)):
            if self.stages[i].limit > self.stages[i-1].limit:
                # This is just a warning, not an error
                pass


@dataclass
class SearchStrategyConfig:
    """Complete search strategy configuration."""
    name: str
    strategy_type: SearchStrategy
    config: MultiStageConfig
    description: Optional[str] = None
    
    # Performance hints
    expected_latency_ms: Optional[int] = None
    memory_usage: Optional[str] = None  # "low", "medium", "high"
    quality_score: Optional[float] = None  # 0.0 to 1.0


# Predefined strategy configurations
def get_speed_first_strategy() -> SearchStrategyConfig:
    """
    Speed-first strategy: Fast BM25 initial retrieval, then vector reranking.
    Best for: Real-time applications, large datasets, when speed is priority.
    """
    stages = [
        SearchStage(
            method=SearchMethod.BM25,
            limit=50,
            description="Fast keyword-based initial retrieval"
        ),
        SearchStage(
            method=SearchMethod.VECTOR,
            limit=10,
            description="Semantic reranking of top candidates"
        )
    ]
    
    config = MultiStageConfig(
        stages=stages,
        final_limit=10,
        description="Speed-optimized search with semantic reranking"
    )
    
    return SearchStrategyConfig(
        name="Speed First",
        strategy_type=SearchStrategy.SPEED_FIRST,
        config=config,
        description="Fast BM25 initial retrieval with vector reranking",
        expected_latency_ms=100,
        memory_usage="low",
        quality_score=0.7
    )


def get_quality_first_strategy() -> SearchStrategyConfig:
    """
    Quality-first strategy: Semantic search first, then keyword refinement.
    Best for: High-quality results, exploratory search, when accuracy is priority.
    """
    stages = [
        SearchStage(
            method=SearchMethod.VECTOR,
            limit=50,
            description="Semantic similarity initial retrieval"
        ),
        SearchStage(
            method=SearchMethod.BM25,
            limit=10,
            description="Keyword-based refinement"
        )
    ]
    
    config = MultiStageConfig(
        stages=stages,
        final_limit=10,
        description="Quality-optimized search with keyword refinement"
    )
    
    return SearchStrategyConfig(
        name="Quality First",
        strategy_type=SearchStrategy.QUALITY_FIRST,
        config=config,
        description="Semantic search first with keyword refinement",
        expected_latency_ms=200,
        memory_usage="medium",
        quality_score=0.9
    )


def get_balanced_strategy() -> SearchStrategyConfig:
    """
    Balanced strategy: Two-stage search with BM25 initial retrieval and vector reranking.
    Best for: General purpose, balanced speed/quality requirements.
    """
    stages = [
        SearchStage(
            method=SearchMethod.BM25,
            limit=30,
            description="Fast keyword-based initial retrieval"
        ),
        SearchStage(
            method=SearchMethod.VECTOR,
            limit=10,
            description="Semantic reranking of candidates"
        )
    ]
    
    config = MultiStageConfig(
        stages=stages,
        final_limit=10,
        description="Balanced search with BM25 initial retrieval and vector reranking"
    )
    
    return SearchStrategyConfig(
        name="Balanced",
        strategy_type=SearchStrategy.BALANCED,
        config=config,
        description="Two-stage balanced search with BM25 and vector methods",
        expected_latency_ms=150,
        memory_usage="medium",
        quality_score=0.8
    )


def get_rrf_only_strategy() -> SearchStrategyConfig:
    """
    RRF-only strategy: Pure Reciprocal Rank Fusion approach with optimized parameters.
    Best for: When you want the proven RRF algorithm without complexity.
    """
    stages = [
        SearchStage(
            method=SearchMethod.RRF,
            limit=10,
            description="Optimized RRF combination of all search methods",
            rrf_k=20  # Optimized value for better fusion
        )
    ]
    
    config = MultiStageConfig(
        stages=stages,
        final_limit=10,
        description="Pure RRF approach with optimized parameters"
    )
    
    return SearchStrategyConfig(
        name="RRF Only",
        strategy_type=SearchStrategy.RRF_ONLY,
        config=config,
        description="Pure Reciprocal Rank Fusion with optimized parameters",
        expected_latency_ms=120,
        memory_usage="low",
        quality_score=0.85
    )


# Strategy registry
PREDEFINED_STRATEGIES = {
    SearchStrategy.SPEED_FIRST: get_speed_first_strategy,
    SearchStrategy.QUALITY_FIRST: get_quality_first_strategy,
    SearchStrategy.BALANCED: get_balanced_strategy,
    SearchStrategy.RRF_ONLY: get_rrf_only_strategy,
}


def get_strategy_config(strategy: SearchStrategy) -> SearchStrategyConfig:
    """Get configuration for a predefined strategy."""
    if strategy not in PREDEFINED_STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return PREDEFINED_STRATEGIES[strategy]()


def list_available_strategies() -> List[SearchStrategyConfig]:
    """Get list of all available predefined strategies."""
    return [factory() for factory in PREDEFINED_STRATEGIES.values()] 