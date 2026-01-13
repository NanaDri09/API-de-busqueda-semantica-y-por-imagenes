from typing import List, Optional, Dict, Any
from ..models.product import Product, ProductCreate, ProductUpdate
from ..repositories.vector_repository import VectorRepository
from ..repositories.bm25_repository import BM25Repository
from ..repositories.image_repository import ImageRepository
from ..repositories.caption_repository import CaptionRepository
from ..services.search_service import SearchService
from ..services.rrf_service import RRFService
from ..services.image_service import ImageService
from ..services.multi_stage_service import MultiStageService
from ..models.search_config import SearchStrategy
from ..config.settings import settings
import logging
from PIL import Image
import io



logger = logging.getLogger(__name__)


class ProductService:
    """High-level service for product operations and search."""
    
    def __init__(self):
        """Initialize the product service with repositories and search service."""
        self.image_service = ImageService()
        self.vector_repo = VectorRepository()
        self.bm25_repo = BM25Repository()
        self.image_repo = ImageRepository(self.image_service)
        self.caption_repo = CaptionRepository(self.image_service, self.vector_repo.embedding_service)
        self.rrf_service = RRFService()
        self.search_service = SearchService(self.vector_repo, self.bm25_repo, self.image_repo, self.caption_repo, self.image_service, self.rrf_service)
        self.multi_stage_service = MultiStageService(self.rrf_service)
        
        # Try to load existing indexes
        try:
            self.vector_repo.load_index()
            logger.info("Loaded existing vector index")
        except Exception as e:
            logger.info(f"No existing vector index found: {e}")
        try:
            self.image_repo.load_index()
            logger.info("Loaded existing image index")
        except Exception as e:
            logger.info(f"No existing image index found: {e}")
        try:
            self.caption_repo.load_index()
            logger.info("Loaded existing caption index")
        except Exception as e:
            logger.info(f"No existing caption index found: {e}")

        
        # Sync BM25 index with vector repo products if any exist
        if self.vector_repo.get_product_count() > 0:
            products = list(self.vector_repo.products.values())
            self.bm25_repo.create_index(products)
            logger.info(f"Synced BM25 index with {len(products)} products")
    
        # Agregar logging para verificar el estado de los índices
        logger.info(f"Vector index count: {self.vector_repo.get_product_count()}")
        logger.info(f"Image index count: {self.image_repo.get_product_count()}")
        logger.info(f"Caption index count: {self.caption_repo.get_product_count()}")
        logger.info(f"BM25 index count: {self.bm25_repo.get_product_count()}")

    def create_product(self, id: str, title: str, description: str, image: Image.Image) -> Product:
        """
        Create a new product and add it to both indexes.
        
        Args:
            id: Unique product identifier
            title: Product title
            description: Product description
            
        Returns:
            Created Product object
            
        Raises:
            ValueError: If validation fails or product already exists
            Exception: If embedding generation fails
        """
        # Tomas y conviertes la imagen a bytes
        img_byte_arr = io.BytesIO()
        fmt = image.format if image.format else 'PNG'
        img_to_save = image
        # Si guardamos como JPEG y la imagen tiene alpha, convertir a RGB
        try:
            if fmt.upper() in ('JPG', 'JPEG') and hasattr(image, 'mode') and ('A' in image.mode):
                img_to_save = image.convert('RGB')
        except Exception:
            # En caso de cualquier problema, convertir a RGB como fallback
            if fmt.upper() in ('JPG', 'JPEG'):
                img_to_save = image.convert('RGB')

        img_to_save.save(img_byte_arr, format=fmt)
        image_bytes = img_byte_arr.getvalue()

        # Url de la imagen
        image_url = Product.set_image(self, image_bytes, filename_hint=id)

        # Validate input using Pydantic
        product_data = ProductCreate(id=id, title=title, description=description, image_url=image_url)
        
        # Create Product object
        product = Product(
            id=product_data.id,
            title=product_data.title,
            description=product_data.description,
            image_url=product_data.image_url
        )
        
        logger.info(f"Creating product: {product.id}")
        
        # Add to both repositories
        self.vector_repo.add_product(product)
        self.bm25_repo.add_product(product)
        self.image_repo.add_image(product)
        self.caption_repo.add_caption(product)
        
        # Save vector index
        self.vector_repo.save_index()
        self.caption_repo.save_index()
        self.image_repo.save_index()
        
        logger.info(f"Successfully created product: {product.id}")
        return product
    
    def update_product(self, id: str, title: str = None, description: str = None, image: Image.Image = None) -> Product:

        # Check if product exists
        existing_product = self.vector_repo.get_product_by_id(id)
        if not existing_product:
            raise ValueError(f"Product with ID {id} does not exist")
        
        if image is not None:
            # Tomas y conviertes la imagen a bytes
            img_byte_arr = io.BytesIO()
            fmt = image.format if image.format else 'PNG'
            img_to_save = image
            try:
                if fmt.upper() in ('JPG', 'JPEG') and hasattr(image, 'mode') and ('A' in image.mode):
                    img_to_save = image.convert('RGB')
            except Exception:
                if fmt.upper() in ('JPG', 'JPEG'):
                    img_to_save = image.convert('RGB')

            img_to_save.save(img_byte_arr, format=fmt)
            image_bytes = img_byte_arr.getvalue()

            # Url de la imagen
            url = Product.set_image(self, image_bytes, filename_hint=id)


        # Validate update data
        update_data = ProductUpdate(title=title, description=description, image_url=url)
        
        # Create updated product
        updated_product = Product(
            id=id,
            title=update_data.title if update_data.title is not None else existing_product.title,
            description=update_data.description if update_data.description is not None else existing_product.description,
            image_url = url if image is not None else existing_product.image_url
        )
        
        logger.info(f"Updating product: {id}")
        
        # Update in both repositories
        self.vector_repo.update_product(updated_product)
        self.bm25_repo.update_product(updated_product)
        self.image_repo.update_image(updated_product)
        self.caption_repo.update_caption(updated_product)
        
        # Save vector index
        self.vector_repo.save_index()
        self.caption_repo.save_index()
        self.image_repo.save_index()
        
        logger.info(f"Successfully updated product: {id}")
        return updated_product
    
    def delete_product(self, id: str) -> bool:
        """
        Delete a product from both indexes.
        
        Args:
            id: Product identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValueError: If product doesn't exist
        """
        logger.info(f"Deleting product: {id}")
        
        # Delete from both repositories
        self.vector_repo.delete_product(id)
        self.bm25_repo.delete_product(id)
        self.image_repo.delete_image(id)
        self.caption_repo.delete_caption(id)
        
        # Save vector index
        self.vector_repo.save_index()
        self.caption_repo.save_index()
        self.image_repo.save_index()
        
        logger.info(f"Successfully deleted product: {id}")
        return True
    
    def search_products(
        self,
        query: str,
        search_type: str = "hybrid",
        bm25_weight: float = None,
        vector_weight: float = None,
        top_k: int = None
    ) -> List[str]:
        """
        Search for products using specified search method.
        
        Args:
            query: Search query
            search_type: Type of search ('hybrid', 'semantic', 'keyword')
            bm25_weight: Weight for BM25 results (hybrid only)
            vector_weight: Weight for vector results (hybrid only)
            top_k: Number of results to return
            
        Returns:
            List of product IDs ranked by relevance
            
        Raises:
            ValueError: If query is empty or search_type is invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        valid_search_types = ["hybrid", "semantic", "keyword", "rrf"]
        if search_type not in valid_search_types:
            raise ValueError(f"Invalid search_type. Must be one of: {valid_search_types}")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Searching products: query='{query}', type={search_type}, top_k={top_k}")
        
        if search_type == "hybrid":
            return self.search_service.hybrid_search(
                query=query,
                bm25_weight=bm25_weight,
                vector_weight=vector_weight,
                top_k=top_k
            )
        elif search_type == "semantic":
            return self.search_service.semantic_search(query=query, top_k=top_k)
        elif search_type == "keyword":
            return self.search_service.keyword_search(query=query, top_k=top_k)
        elif search_type == "rrf":
            # Extract rrf_k from vector_weight parameter for backward compatibility
            rrf_k = int(bm25_weight) if bm25_weight and bm25_weight > 1 else 60
            return self.search_service.rrf_search(query=query, k=rrf_k, top_k=top_k)
    
    def get_product_by_id(self, id: str) -> Optional[Product]:
        """
        Get a product by its ID.
        
        Args:
            id: Product identifier
            
        Returns:
            Product object if found, None otherwise
        """
        return self.vector_repo.get_product_by_id(id)
    
    def list_all_products(self) -> List[Product]:
        """
        Get all products in the system.
        
        Returns:
            List of all Product objects
        """
        return list(self.vector_repo.products.values())
    
    def get_product_count(self) -> int:
        """
        Get the total number of products.
        
        Returns:
            Number of products in the system
        """
        return self.vector_repo.get_product_count()
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the search system.
        
        Returns:
            Dictionary with system statistics
        """
        stats = self.search_service.get_search_statistics()
        stats.update({
            "default_weights": {
                "bm25": settings.DEFAULT_BM25_WEIGHT,
                "vector": settings.DEFAULT_VECTOR_WEIGHT
            },
            "default_top_k": settings.DEFAULT_TOP_K,
            "vector_dimension": settings.VECTOR_DIMENSION,
            # Agregar estadísticas de imágenes y captions
            "image_index_size": self.image_repo.get_product_count(),
            "caption_index_size": self.caption_repo.get_product_count()
        })
        return stats
    
    def rebuild_indexes(self) -> None:
        """
        Rebuild both search indexes from scratch.
        
        This can be useful for maintenance or after configuration changes.
        """
        logger.info("Rebuilding search indexes")
        
        if self.vector_repo.get_product_count() == 0:
            logger.info("No products to rebuild indexes for")
            return
        
        # Get all products
        products = list(self.vector_repo.products.values())
        
        # Rebuild BM25 index
        self.bm25_repo.create_index(products)
        
        # Vector index rebuilds automatically when needed

        
        # Save vector index
        self.vector_repo.save_index()
        self.caption_repo.save_index()
        self.image_repo.save_index()
        
        logger.info(f"Successfully rebuilt indexes for {len(products)} products")
    
    def clear_all_data(self) -> None:
        """
        Clear all products and indexes.
        
        WARNING: This will permanently delete all data.
        """
        logger.warning("Clearing all product data")
        
        # Clear repositories
        self.vector_repo.products.clear()
        self.vector_repo.index = None
        self.vector_repo.product_id_map.clear()
        self.vector_repo.id_to_index_map.clear()
        self.vector_repo._next_index = 0
        
        self.image_repo.products.clear()
        self.image_repo.index = None
        self.image_repo.product_id_map.clear()
        self.image_repo.id_to_index_map.clear()
        self.image_repo._next_index = 0

        self.caption_repo.products.clear()
        self.caption_repo.index = None
        self.caption_repo.product_id_map.clear()
        self.caption_repo.id_to_index_map.clear()
        self.caption_repo._next_index = 0

        self.bm25_repo.clear_index()
        
        # Save empty state
        self.vector_repo.save_index()
        self.caption_repo.save_index()
        self.image_repo.save_index()
        
        logger.info("Successfully cleared all product data")
    
    def batch_create_products(self, products_data: List[Dict[str, str]]) -> List[Product]:
        """
        Create multiple products in batch for better performance.
        
        Args:
            products_data: List of dictionaries with 'id', 'title', 'description'
            
        Returns:
            List of created Product objects
            
        Raises:
            ValueError: If any product data is invalid
        """
        logger.info(f"Creating {len(products_data)} products in batch")
        
        # Validate all products first
        products = []
        for data in products_data:
            product_data = ProductCreate(**data)
            product = Product(
                id=product_data.id,
                title=product_data.title,
                description=product_data.description
            )
            products.append(product)
        
        # Create indexes with all products
        self.vector_repo.create_index(products)
        self.bm25_repo.create_index(products)
        
        # Save vector index
        self.vector_repo.save_index()
        
        logger.info(f"Successfully created {len(products)} products in batch")
        return products
    
    def search_with_strategy(
        self,
        query: str,
        strategy: str = "balanced",
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Search using predefined multi-stage strategies.
        
        Args:
            query: Search query
            strategy: Strategy name ('speed_first', 'quality_first', 'balanced', 'rrf_only')
            top_k: Number of final results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            strategy_enum = SearchStrategy(strategy)
        except ValueError:
            raise ValueError(f"Unknown strategy: {strategy}. Available: speed_first, quality_first, balanced, rrf_only")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        # Prepare search methods for multi-stage service
        search_methods = {
            "bm25_search": lambda q, top_k: self.search_service.keyword_search(q, top_k),
            "vector_search": lambda q, top_k: self.search_service.semantic_search(q, top_k),
            "hybrid_search": lambda q, top_k, **kwargs: self.search_service.hybrid_search(q, top_k=top_k, **kwargs)
        }
        
        # Execute strategy
        result = self.multi_stage_service.execute_strategy(
            query=query,
            strategy=strategy_enum,
            search_methods=search_methods
        )
        
        # Limit final results
        if result["results"] and len(result["results"]) > top_k:
            result["results"] = result["results"][:top_k]
            result["total_results"] = len(result["results"])
        
        return result
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of available search strategies.
        
        Returns:
            List of strategy information
        """
        return self.multi_stage_service.get_available_strategies() 