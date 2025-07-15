import os
import pickle
from typing import List, Tuple, Optional, Dict
import numpy as np
import faiss
from ..models.product import Product
from ..services.embedding_service import EmbeddingService
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class VectorRepository:
    """Repository for managing FAISS vector store operations."""
    
    def __init__(self):
        """Initialize the vector repository."""
        self.embedding_service = EmbeddingService()
        self.index: Optional[faiss.Index] = None
        self.product_id_map: Dict[int, str] = {}  # FAISS index -> product_id
        self.id_to_index_map: Dict[str, int] = {}  # product_id -> FAISS index
        self.products: Dict[str, Product] = {}  # product_id -> Product
        self._next_index = 0
        
        # Create vector store directory
        settings.create_vector_store_dir()
    
    def _initialize_index(self) -> None:
        """Initialize FAISS index if not already created."""
        if self.index is None:
            # Use L2 distance for similarity search
            self.index = faiss.IndexFlatL2(settings.VECTOR_DIMENSION)
            logger.info(f"Initialized FAISS index with dimension {settings.VECTOR_DIMENSION}")
    
    def create_index(self, products: List[Product]) -> None:
        """
        Create FAISS index from a list of products.
        
        Args:
            products: List of products to index
            
        Raises:
            ValueError: If products list is empty
            Exception: If embedding generation fails
        """
        if not products:
            raise ValueError("Products list cannot be empty")
        
        logger.info(f"Creating FAISS index for {len(products)} products")
        
        # Generate embeddings for all products
        texts = [product.get_combined_text() for product in products]
        embeddings = self.embedding_service.generate_embeddings_batch(texts)
        
        # Initialize index
        self._initialize_index()
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add embeddings to FAISS index
        self.index.add(embeddings_array)
        
        # Update mappings
        for i, product in enumerate(products):
            faiss_index = self._next_index + i
            self.product_id_map[faiss_index] = product.id
            self.id_to_index_map[product.id] = faiss_index
            self.products[product.id] = product
        
        self._next_index += len(products)
        logger.info(f"Successfully created FAISS index with {len(products)} products")
    
    def add_product(self, product: Product) -> None:
        """
        Add a single product to the FAISS index.
        
        Args:
            product: Product to add
            
        Raises:
            ValueError: If product already exists
            Exception: If embedding generation fails
        """
        if product.id in self.products:
            raise ValueError(f"Product with ID {product.id} already exists")
        
        logger.info(f"Adding product {product.id} to FAISS index")
        
        # Initialize index if needed
        self._initialize_index()
        
        # Generate embedding
        embedding = self.embedding_service.generate_embedding(product.get_combined_text())
        
        # Convert to numpy array
        embedding_array = np.array([embedding], dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embedding_array)
        
        # Update mappings
        faiss_index = self._next_index
        self.product_id_map[faiss_index] = product.id
        self.id_to_index_map[product.id] = faiss_index
        self.products[product.id] = product
        self._next_index += 1
        
        logger.info(f"Successfully added product {product.id} to FAISS index")
    
    def update_product(self, product: Product) -> None:
        """
        Update an existing product in the FAISS index.
        
        Args:
            product: Updated product
            
        Raises:
            ValueError: If product doesn't exist
            Exception: If embedding generation fails
        """
        if product.id not in self.products:
            raise ValueError(f"Product with ID {product.id} does not exist")
        
        logger.info(f"Updating product {product.id} in FAISS index")
        
        # For FAISS, we need to rebuild the index for updates
        # Store the updated product
        self.products[product.id] = product
        
        # Rebuild the entire index
        self._rebuild_index()
        
        logger.info(f"Successfully updated product {product.id} in FAISS index")
    
    def delete_product(self, product_id: str) -> None:
        """
        Delete a product from the FAISS index.
        
        Args:
            product_id: ID of product to delete
            
        Raises:
            ValueError: If product doesn't exist
        """
        if product_id not in self.products:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        logger.info(f"Deleting product {product_id} from FAISS index")
        
        # Remove from mappings
        faiss_index = self.id_to_index_map[product_id]
        del self.product_id_map[faiss_index]
        del self.id_to_index_map[product_id]
        del self.products[product_id]
        
        # Rebuild the index without the deleted product
        self._rebuild_index()
        
        logger.info(f"Successfully deleted product {product_id} from FAISS index")
    
    def search_similar(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar products using vector similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (product_id, similarity_score) tuples
            
        Raises:
            ValueError: If query is empty or index is empty
            Exception: If embedding generation fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query.strip())
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search in FAISS index
        k = min(k, self.index.ntotal)  # Don't search for more than available
        distances, indices = self.index.search(query_array, k)
        
        # Convert results to product IDs and scores
        results = []
        for i, (distance, faiss_index) in enumerate(zip(distances[0], indices[0])):
            if faiss_index in self.product_id_map:
                product_id = self.product_id_map[faiss_index]
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                similarity_score = 1.0 / (1.0 + distance)
                results.append((product_id, similarity_score))
        
        return results
    
    def _rebuild_index(self) -> None:
        """Rebuild the FAISS index from current products."""
        if not self.products:
            self.index = None
            self.product_id_map.clear()
            self.id_to_index_map.clear()
            self._next_index = 0
            return
        
        # Clear mappings
        self.product_id_map.clear()
        self.id_to_index_map.clear()
        self._next_index = 0
        
        # Rebuild index
        products_list = list(self.products.values())
        self.create_index(products_list)
    
    def save_index(self, path: str = None) -> None:
        """
        Save FAISS index and mappings to disk.
        
        Args:
            path: Directory path to save index (defaults to settings path)
        """
        if path is None:
            path = settings.VECTOR_STORE_PATH
        
        os.makedirs(path, exist_ok=True)
        
        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, os.path.join(path, "faiss_index.bin"))
            
            # Save mappings and products
            metadata = {
                "product_id_map": self.product_id_map,
                "id_to_index_map": self.id_to_index_map,
                "products": self.products,
                "next_index": self._next_index
            }
            
            with open(os.path.join(path, "metadata.pkl"), "wb") as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved FAISS index to {path}")
        else:
            logger.warning("No index to save")
    
    def load_index(self, path: str = None) -> None:
        """
        Load FAISS index and mappings from disk.
        
        Args:
            path: Directory path to load index from (defaults to settings path)
        """
        if path is None:
            path = settings.VECTOR_STORE_PATH
        
        index_path = os.path.join(path, "faiss_index.bin")
        metadata_path = os.path.join(path, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load mappings and products
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            
            self.product_id_map = metadata["product_id_map"]
            self.id_to_index_map = metadata["id_to_index_map"]
            self.products = metadata["products"]
            self._next_index = metadata["next_index"]
            
            logger.info(f"Loaded FAISS index from {path}")
        else:
            logger.info("No existing index found, starting fresh")
    
    def get_product_count(self) -> int:
        """Get the number of products in the index."""
        return len(self.products)
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID."""
        return self.products.get(product_id) 