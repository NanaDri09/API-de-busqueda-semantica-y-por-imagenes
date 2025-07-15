from typing import List, Tuple, Optional, Dict
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
from ..models.product import Product, ProductDocument
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class BM25Repository:
    """Repository for managing BM25 keyword search operations."""
    
    def __init__(self):
        """Initialize the BM25 repository."""
        self.retriever: Optional[BM25Retriever] = None
        self.products: Dict[str, Product] = {}  # product_id -> Product
        self.documents: List[ProductDocument] = []
    
    def create_index(self, products: List[Product]) -> None:
        """
        Create BM25 index from a list of products.
        
        Args:
            products: List of products to index
            
        Raises:
            ValueError: If products list is empty
        """
        if not products:
            raise ValueError("Products list cannot be empty")
        
        logger.info(f"Creating BM25 index for {len(products)} products")
        
        # Create documents for BM25
        self.documents = [ProductDocument(product) for product in products]
        self.products = {product.id: product for product in products}
        
        # Create BM25 retriever
        self.retriever = BM25Retriever.from_documents(self.documents)
        self.retriever.k = settings.DEFAULT_TOP_K
        
        logger.info(f"Successfully created BM25 index with {len(products)} products")
    
    def add_product(self, product: Product) -> None:
        """
        Add a single product to the BM25 index.
        
        Args:
            product: Product to add
            
        Raises:
            ValueError: If product already exists
        """
        if product.id in self.products:
            raise ValueError(f"Product with ID {product.id} already exists")
        
        logger.info(f"Adding product {product.id} to BM25 index")
        
        # Add to products and documents
        self.products[product.id] = product
        self.documents.append(ProductDocument(product))
        
        # Rebuild the index
        self.rebuild_index()
        
        logger.info(f"Successfully added product {product.id} to BM25 index")
    
    def update_product(self, product: Product) -> None:
        """
        Update an existing product in the BM25 index.
        
        Args:
            product: Updated product
            
        Raises:
            ValueError: If product doesn't exist
        """
        if product.id not in self.products:
            raise ValueError(f"Product with ID {product.id} does not exist")
        
        logger.info(f"Updating product {product.id} in BM25 index")
        
        # Update the product
        self.products[product.id] = product
        
        # Find and update the document
        for i, doc in enumerate(self.documents):
            if doc.product_id == product.id:
                self.documents[i] = ProductDocument(product)
                break
        
        # Rebuild the index
        self.rebuild_index()
        
        logger.info(f"Successfully updated product {product.id} in BM25 index")
    
    def delete_product(self, product_id: str) -> None:
        """
        Delete a product from the BM25 index.
        
        Args:
            product_id: ID of product to delete
            
        Raises:
            ValueError: If product doesn't exist
        """
        if product_id not in self.products:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        logger.info(f"Deleting product {product_id} from BM25 index")
        
        # Remove from products
        del self.products[product_id]
        
        # Remove from documents
        self.documents = [doc for doc in self.documents if doc.product_id != product_id]
        
        # Rebuild the index
        self.rebuild_index()
        
        logger.info(f"Successfully deleted product {product_id} from BM25 index")
    
    def search_keywords(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for products using BM25 keyword matching.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (product_id, relevance_score) tuples
            
        Raises:
            ValueError: If query is empty or index is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if self.retriever is None or not self.documents:
            logger.warning("BM25 index is empty")
            return []
        
        # Set the number of results to return
        original_k = self.retriever.k
        self.retriever.k = min(k, len(self.documents))
        
        try:
            # Get relevant documents
            docs = self.retriever.invoke(query.strip())
            
            # Convert to product IDs with scores
            results = []
            for doc in docs:
                product_id = doc.metadata.get("product_id")
                if product_id:
                    # BM25 doesn't return explicit scores, so we assign decreasing scores
                    score = 1.0 / (len(results) + 1)
                    results.append((product_id, score))
            
            return results
        
        finally:
            # Restore original k value
            self.retriever.k = original_k
    
    def rebuild_index(self) -> None:
        """Rebuild the BM25 index from current documents."""
        if not self.documents:
            self.retriever = None
            return
        
        logger.info("Rebuilding BM25 index")
        
        # Create new retriever with current documents
        self.retriever = BM25Retriever.from_documents(self.documents)
        self.retriever.k = settings.DEFAULT_TOP_K
        
        logger.info(f"Successfully rebuilt BM25 index with {len(self.documents)} documents")
    
    def get_product_count(self) -> int:
        """Get the number of products in the index."""
        return len(self.products)
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID."""
        return self.products.get(product_id)
    
    def get_all_products(self) -> List[Product]:
        """Get all products in the index."""
        return list(self.products.values())
    
    def clear_index(self) -> None:
        """Clear the entire BM25 index."""
        logger.info("Clearing BM25 index")
        self.retriever = None
        self.products.clear()
        self.documents.clear()
        logger.info("Successfully cleared BM25 index") 