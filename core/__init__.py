"""
Semantic Search Core Module

A modular semantic search system combining BM25 keyword matching
and vector embeddings for e-commerce product search.
"""

from .services.product_service import ProductService
from .models.product import Product

__version__ = "1.0.0"
__all__ = ["ProductService", "Product"] 