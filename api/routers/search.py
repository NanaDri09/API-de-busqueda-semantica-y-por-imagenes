import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request

from core.services.product_service import ProductService
from ..models.requests import SearchRequest, SearchType, StrategySearchRequest
from ..models.responses import (
    SearchResponse, 
    SearchResult, 
    ProductResponse,
    StatsResponse,
    HealthResponse,
    MessageResponse,
    ErrorResponse,
    StrategySearchResponse
)
from ..dependencies import get_product_service, get_request_id, get_service_uptime, check_service_health, verify_api_key
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


def product_to_response(product) -> ProductResponse:
    """Convert Product model to ProductResponse."""
    return ProductResponse(
        id=product.id,
        title=product.title,
        description=product.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@router.post("/",
    response_model=SearchResponse,
    summary="Search products",
    description="Search for products using hybrid, semantic, or keyword search methods.")
async def search_products(
    search_request: SearchRequest,
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """Search for products using the specified search method."""
    request_id = get_request_id(request)
    start_time = time.time()
    
    try:
        logger.info(f"Searching products: query='{search_request.query}', type={search_request.search_type} [Request: {request_id}]")
        
        # Perform search
        product_ids = service.search_products(
            query=search_request.query,
            search_type=search_request.search_type.value,
            bm25_weight=search_request.bm25_weight,
            vector_weight=search_request.vector_weight,
            top_k=search_request.top_k
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Build results
        results = []
        for i, product_id in enumerate(product_ids):
            # Calculate a mock score (in real implementation, this would come from the search service)
            score = 1.0 - (i * 0.1)  # Decreasing score based on rank
            
            search_result = SearchResult(
                product_id=product_id,
                score=score
            )
            
            # Include product details if requested
            if search_request.include_product_details:
                product = service.get_product_by_id(product_id)
                if product:
                    search_result.product = product_to_response(product)
            
            results.append(search_result)
        
        # Prepare weights for response (if hybrid search)
        weights = None
        if search_request.search_type == SearchType.HYBRID:
            bm25_w = search_request.bm25_weight or 0.4
            vector_w = search_request.vector_weight or 0.6
            total = bm25_w + vector_w
            weights = {
                "bm25": bm25_w / total,
                "vector": vector_w / total
            }
        
        logger.info(f"Search completed: {len(results)} results in {execution_time:.2f}ms [Request: {request_id}]")
        
        return SearchResponse(
            results=results,
            query=search_request.query,
            search_type=search_request.search_type,
            total_results=len(results),
            execution_time_ms=execution_time,
            weights=weights
        )
        
    except Exception as e:
        logger.error(f"Search error: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.post("/hybrid",
    response_model=SearchResponse,
    summary="Hybrid search",
    description="Search using both BM25 and vector embeddings with custom weights.")
async def hybrid_search(
    query: str,
    request: Request,
    top_k: int = 10,
    bm25_weight: float = 0.4,
    vector_weight: float = 0.6,
    include_product_details: bool = False,
    service: ProductService = Depends(get_product_service)
):
    """Perform hybrid search with custom weights."""
    search_request = SearchRequest(
        query=query,
        search_type=SearchType.HYBRID,
        top_k=top_k,
        bm25_weight=bm25_weight,
        vector_weight=vector_weight,
        include_product_details=include_product_details
    )
    
    return await search_products(search_request, request, service)


@router.post("/semantic",
    response_model=SearchResponse,
    summary="Semantic search",
    description="Search using only vector embeddings for semantic similarity.")
async def semantic_search(
    query: str,
    request: Request,
    top_k: int = 10,
    include_product_details: bool = False,
    service: ProductService = Depends(get_product_service)
):
    """Perform semantic search only."""
    search_request = SearchRequest(
        query=query,
        search_type=SearchType.SEMANTIC,
        top_k=top_k,
        include_product_details=include_product_details
    )
    
    return await search_products(search_request, request, service)


@router.post("/keyword",
    response_model=SearchResponse,
    summary="Keyword search",
    description="Search using only BM25 for exact keyword matching.")
async def keyword_search(
    query: str,
    request: Request,
    top_k: int = 10,
    include_product_details: bool = False,
    service: ProductService = Depends(get_product_service)
):
    """Perform keyword search only."""
    search_request = SearchRequest(
        query=query,
        search_type=SearchType.KEYWORD,
        top_k=top_k,
        include_product_details=include_product_details
    )
    
    return await search_products(search_request, request, service)


@router.get("/stats",
    response_model=StatsResponse,
    summary="Search statistics",
    description="Get statistics about the search system and indexes.")
async def get_search_stats(
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """Get search system statistics."""
    request_id = get_request_id(request)
    
    try:
        logger.info(f"Getting search statistics [Request: {request_id}]")
        
        stats = service.get_search_statistics()
        
        return StatsResponse(
            total_products=stats["total_products"],
            vector_index_size=stats["vector_index_size"],
            bm25_index_size=stats["bm25_index_size"],
            vector_dimension=stats["vector_dimension"],
            default_weights=stats["default_weights"],
            default_top_k=stats["default_top_k"]
        )
        
    except Exception as e:
        logger.error(f"Error getting search statistics: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve search statistics"
        )


# System endpoints (could be moved to a separate router)
@router.get("/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the search service and its dependencies.")
async def health_check(request: Request):
    """Health check endpoint."""
    request_id = get_request_id(request)
    
    try:
        logger.info(f"Health check requested [Request: {request_id}]")
        
        # Check service health
        dependencies = check_service_health()
        
        # Determine overall status
        status_value = "healthy"
        if any(status == "error" for status in dependencies.values()):
            status_value = "unhealthy"
        elif any(status in ["unknown", "not_configured"] for status in dependencies.values()):
            status_value = "degraded"
        
        return HealthResponse(
            status=status_value,
            version="1.0.0",
            uptime_seconds=get_service_uptime(),
            timestamp=datetime.now(timezone.utc),
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e} [Request: {request_id}]")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            uptime_seconds=get_service_uptime(),
            timestamp=datetime.now(timezone.utc),
            dependencies={"error": str(e)}
        )


@router.post("/rebuild",
    response_model=MessageResponse,
    summary="Rebuild indexes",
    description="Rebuild search indexes from scratch. This may take some time for large datasets.")
async def rebuild_indexes(
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Rebuild search indexes."""
    request_id = get_request_id(request)
    
    try:
        logger.info(f"Rebuilding search indexes [Request: {request_id}]")
        
        start_time = time.time()
        service.rebuild_indexes()
        execution_time = time.time() - start_time
        
        logger.info(f"Search indexes rebuilt in {execution_time:.2f}s [Request: {request_id}]")
        
        return MessageResponse(
            message=f"Search indexes rebuilt successfully in {execution_time:.2f} seconds",
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error rebuilding indexes: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rebuild search indexes"
        )


@router.delete("/clear",
    response_model=MessageResponse,
    summary="Clear all data",
    description="Clear all products and search indexes. WARNING: This action cannot be undone!")
async def clear_all_data(
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Clear all data from the system."""
    request_id = get_request_id(request)
    
    try:
        logger.warning(f"Clearing all data [Request: {request_id}]")
        
        service.clear_all_data()
        
        logger.warning(f"All data cleared [Request: {request_id}]")
        
        return MessageResponse(
            message="All data cleared successfully",
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error clearing data: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear data"
        )


@router.post("/rrf",
    response_model=SearchResponse,
    summary="RRF search",
    description="Search using Reciprocal Rank Fusion to combine BM25 and vector results.")
async def rrf_search(
    query: str,
    request: Request,
    top_k: int = 10,
    rrf_k: int = 20,
    include_product_details: bool = False,
    service: ProductService = Depends(get_product_service)
):
    """Search using Reciprocal Rank Fusion algorithm."""
    try:
        request_id = get_request_id(request)
        start_time = time.time()
        
        logger.info(f"[{request_id}] RRF search request: query='{query}', top_k={top_k}, rrf_k={rrf_k}")
        
        # Perform RRF search
        product_ids = service.search_products(
            query=query, 
            search_type="rrf",
            bm25_weight=float(rrf_k),  # Pass rrf_k via bm25_weight parameter
            top_k=top_k
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Build response
        results = []
        for i, product_id in enumerate(product_ids):
            result = SearchResult(
                product_id=product_id,
                score=1.0 / (i + 1)  # Simple ranking score
            )
            
            if include_product_details:
                product = service.get_product_by_id(product_id)
                if product:
                    result.product = product_to_response(product)
            
            results.append(result)
        
        logger.info(f"[{request_id}] RRF search completed: {len(results)} results in {execution_time:.1f}ms")
        
        return SearchResponse(
            results=results,
            query=query,
            search_type=SearchType.RRF,
            total_results=len(results),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error in RRF search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RRF search failed: {str(e)}"
        )


@router.post("/strategy",
    response_model=StrategySearchResponse,
    summary="Strategy-based search",
    description="Search using multi-stage strategies for optimized performance and quality.")
async def strategy_search(
    search_request: StrategySearchRequest,
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """Search using predefined multi-stage strategies."""
    try:
        request_id = get_request_id(request)
        start_time = time.time()
        
        logger.info(f"[{request_id}] Strategy search request: query='{search_request.query}', strategy={search_request.strategy}")
        
        # Perform strategy-based search
        result_dict = service.search_with_strategy(
            query=search_request.query,
            strategy=search_request.strategy.value,
            top_k=search_request.top_k
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Build response
        results = []
        product_ids = result_dict.get("results", [])
        
        for i, product_id in enumerate(product_ids):
            result = SearchResult(
                product_id=product_id,
                score=1.0 / (i + 1)  # Simple ranking score
            )
            
            if search_request.include_product_details:
                product = service.get_product_by_id(product_id)
                if product:
                    result.product = product_to_response(product)
            
            results.append(result)
        
        logger.info(f"[{request_id}] Strategy search completed: {len(results)} results in {execution_time:.1f}ms")
        
        return StrategySearchResponse(
            results=results,
            query=search_request.query,
            strategy=search_request.strategy,
            total_results=len(results),
            execution_time_ms=execution_time,
            stage_details=result_dict.get("stage_details", []),
            stages_executed=result_dict.get("stages_executed", 1)
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error in strategy search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy search failed: {str(e)}"
        )


@router.get("/strategies",
    response_model=Dict[str, Any],
    summary="Available strategies",
    description="Get list of available search strategies and their configurations.")
async def get_available_strategies(
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """Get list of available search strategies."""
    try:
        request_id = get_request_id(request)
        logger.info(f"[{request_id}] Get available strategies request")
        
        strategies = service.get_available_strategies()
        
        return {
            "strategies": strategies,
            "total_strategies": len(strategies),
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] Error getting strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategies: {str(e)}"
        ) 