from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .requests import SearchType, SearchStrategy
from datetime import datetime, timezone


class ProductResponse(BaseModel):
    """Response model for product data."""
    id: str = Field(..., description="Product identifier")
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Product description")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "laptop-001",
                "title": "MacBook Pro 16-inch",
                "description": "Professional laptop with M2 chip, 32GB RAM, and 1TB SSD.",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ProductListResponse(BaseModel):
    """Response model for paginated product list."""
    products: List[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "id": "laptop-001",
                        "title": "MacBook Pro 16-inch",
                        "description": "Professional laptop with M2 chip",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 50,
                "page": 1,
                "size": 20,
                "total_pages": 3
            }
        }


class SearchResult(BaseModel):
    """Individual search result."""
    product_id: str = Field(..., description="Product identifier")
    score: float = Field(..., description="Relevance score")
    product: Optional[ProductResponse] = Field(None, description="Full product details (if requested)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "laptop-001",
                "score": 0.95,
                "product": {
                    "id": "laptop-001",
                    "title": "MacBook Pro 16-inch",
                    "description": "Professional laptop with M2 chip"
                }
            }
        }


class SearchResponse(BaseModel):
    """Response model for search operations."""
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original search query")
    search_type: SearchType = Field(..., description="Type of search performed")
    total_results: int = Field(..., description="Number of results returned")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    weights: Optional[Dict[str, float]] = Field(None, description="Search weights used (for hybrid search)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "product_id": "laptop-001",
                        "score": 0.95,
                        "product": {
                            "id": "laptop-001",
                            "title": "MacBook Pro 16-inch",
                            "description": "Professional laptop with M2 chip"
                        }
                    }
                ],
                "query": "professional laptop",
                "search_type": "hybrid",
                "total_results": 1,
                "execution_time_ms": 45.2,
                "weights": {"bm25": 0.4, "vector": 0.6}
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(..., description="Current timestamp")
    dependencies: Dict[str, str] = Field(..., description="Status of dependencies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime_seconds": 3600.5,
                "timestamp": "2024-01-15T10:30:00Z",
                "dependencies": {
                    "openai": "connected",
                    "vector_store": "ready",
                    "bm25_index": "ready"
                }
            }
        }


class StatsResponse(BaseModel):
    """Response model for system statistics."""
    total_products: int = Field(..., description="Total number of products")
    vector_index_size: int = Field(..., description="Number of items in vector index")
    bm25_index_size: int = Field(..., description="Number of items in BM25 index")
    vector_dimension: int = Field(..., description="Vector embedding dimension")
    default_weights: Dict[str, float] = Field(..., description="Default search weights")
    default_top_k: int = Field(..., description="Default number of results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_products": 1250,
                "vector_index_size": 1250,
                "bm25_index_size": 1250,
                "vector_dimension": 1536,
                "default_weights": {"bm25": 0.4, "vector": 0.6},
                "default_top_k": 10
            }
        }


class BatchResponse(BaseModel):
    """Response model for batch operations."""
    successful: List[str] = Field(..., description="Successfully processed item IDs")
    failed: List[Dict[str, str]] = Field(..., description="Failed items with error messages")
    total_processed: int = Field(..., description="Total number of items processed")
    success_count: int = Field(..., description="Number of successful operations")
    failure_count: int = Field(..., description="Number of failed operations")
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the batch operation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "successful": ["laptop-001", "phone-001"],
                "failed": [
                    {"id": "tablet-001", "error": "Product already exists"}
                ],
                "total_processed": 3,
                "success_count": 2,
                "failure_count": 1,
                "execution_time_ms": 150.5,
                "timestamp": "2024-07-14T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Product ID cannot be empty",
                "details": {
                    "field": "id",
                    "input_value": ""
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_123456789"
            }
        }


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class StrategySearchResponse(BaseModel):
    """Response model for strategy-based search operations."""
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original search query")
    strategy: SearchStrategy = Field(..., description="Search strategy used")
    total_results: int = Field(..., description="Number of results returned")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    stage_details: List[Dict[str, Any]] = Field(..., description="Details about each search stage")
    stages_executed: int = Field(..., description="Number of stages executed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "product_id": "laptop-001",
                        "score": 0.95,
                        "product": {
                            "id": "laptop-001",
                            "title": "MacBook Pro 16-inch",
                            "description": "Professional laptop for video editing"
                        }
                    }
                ],
                "query": "equipo portátil para edición de video",
                "strategy": "quality_first",
                "total_results": 5,
                "execution_time_ms": 245.7,
                "stage_details": [
                    {
                        "stage": 1,
                        "method": "vector",
                        "limit": 50,
                        "results_count": 15,
                        "execution_time_ms": 220.3,
                        "description": "Semantic similarity initial retrieval"
                    },
                    {
                        "stage": 2,
                        "method": "bm25",
                        "limit": 10,
                        "results_count": 5,
                        "execution_time_ms": 25.4,
                        "description": "Keyword-based refinement"
                    }
                ],
                "stages_executed": 2
            }
        } 