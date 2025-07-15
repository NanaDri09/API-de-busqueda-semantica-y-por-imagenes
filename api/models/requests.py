from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class SearchType(str, Enum):
    """Enum for search types."""
    HYBRID = "hybrid"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    RRF = "rrf"


class SearchStrategy(str, Enum):
    """Enum for multi-stage search strategies."""
    BALANCED = "balanced"
    SPEED_FIRST = "speed_first"
    QUALITY_FIRST = "quality_first"
    RRF_ONLY = "rrf_only"


class ProductCreateRequest(BaseModel):
    """Request model for creating a new product."""
    id: str = Field(..., min_length=1, max_length=100, description="Unique product identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Product title")
    description: str = Field(..., min_length=1, max_length=5000, description="Product description")
    
    @validator('id', 'title', 'description')
    def validate_not_empty_or_whitespace(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip()
    
    @validator('id')
    def validate_id_format(cls, v):
        # Allow alphanumeric, hyphens, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Product ID can only contain letters, numbers, hyphens, and underscores')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "laptop-001",
                "title": "MacBook Pro 16-inch",
                "description": "Professional laptop with M2 chip, 32GB RAM, and 1TB SSD. Perfect for developers and creative professionals."
            }
        }


class ProductUpdateRequest(BaseModel):
    """Request model for updating an existing product."""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated product title")
    description: Optional[str] = Field(None, min_length=1, max_length=5000, description="Updated product description")
    
    @validator('title', 'description')
    def validate_not_empty_if_provided(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or only whitespace if provided')
        return v.strip() if v else v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "MacBook Pro 16-inch M3",
                "description": "Latest professional laptop with M3 chip, 32GB RAM, and 1TB SSD. Perfect for developers and creative professionals."
            }
        }


class SearchRequest(BaseModel):
    """Request model for product search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    search_type: SearchType = Field(SearchType.HYBRID, description="Type of search to perform")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    bm25_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for BM25 results (hybrid only)")
    vector_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for vector results (hybrid only)")
    include_product_details: bool = Field(False, description="Include full product details in results")
    
    @validator('query')
    def validate_query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty or only whitespace')
        return v.strip()
    
    @validator('vector_weight')
    def validate_weights_sum(cls, v, values):
        if 'bm25_weight' in values and values['bm25_weight'] is not None and v is not None:
            if values['bm25_weight'] + v == 0:
                raise ValueError('At least one weight must be greater than 0')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "professional laptop for development",
                "search_type": "hybrid",
                "top_k": 5,
                "bm25_weight": 0.4,
                "vector_weight": 0.6,
                "include_product_details": True
            }
        }


class StrategySearchRequest(BaseModel):
    """Request model for strategy-based search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    strategy: SearchStrategy = Field(SearchStrategy.BALANCED, description="Search strategy to use")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    include_product_details: bool = Field(False, description="Include full product details in results")
    
    @validator('query')
    def validate_query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty or only whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "equipo portátil para edición de video",
                "strategy": "quality_first",
                "top_k": 10,
                "include_product_details": True
            }
        }


class BatchProductCreateRequest(BaseModel):
    """Request model for batch product creation."""
    products: List[ProductCreateRequest] = Field(..., min_items=1, max_items=100, description="List of products to create")
    
    @validator('products')
    def validate_unique_ids(cls, v):
        ids = [product.id for product in v]
        if len(ids) != len(set(ids)):
            raise ValueError('Product IDs must be unique within the batch')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "id": "laptop-001",
                        "title": "MacBook Pro 16-inch",
                        "description": "Professional laptop with M2 chip"
                    },
                    {
                        "id": "phone-001", 
                        "title": "iPhone 15 Pro",
                        "description": "Latest iPhone with advanced camera"
                    }
                ]
            }
        }


class BatchDeleteRequest(BaseModel):
    """Request model for batch product deletion."""
    product_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of product IDs to delete")
    
    @validator('product_ids')
    def validate_unique_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Product IDs must be unique')
        return v
    
    @validator('product_ids')
    def validate_ids_not_empty(cls, v):
        for product_id in v:
            if not product_id or not product_id.strip():
                raise ValueError('Product IDs cannot be empty or only whitespace')
        return [product_id.strip() for product_id in v]
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_ids": ["laptop-001", "phone-001", "tablet-001"]
            }
        }


class PaginationRequest(BaseModel):
    """Request model for pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Number of items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20
            }
        } 