import os
import pickle
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import faiss
from ..config.settings import settings
from ..services.image_service import ImageService
from ..services.embedding_service import EmbeddingService
from ..models.product import Product
import logging

logger = logging.getLogger(__name__)


class CaptionRepository:
    """Repository for managing FAISS caption vector store operations."""

    def __init__(self, image_service: ImageService, embedding_service: EmbeddingService):
        """Initialize the image repository.
        """
        self.image_service = image_service
        self.embedding_service = embedding_service
        self.index: Optional[faiss.Index] = None
        self.product_id_map: Dict[int, str] = {}  # FAISS index -> product_id
        self.id_to_index_map: Dict[str, int] = {}  # product_id -> FAISS index
        self.products: Dict[str, Product] = {}  # product_id -> Product
        self._next_index = 0
        self.dimension: Optional[int] = None

        # Ensure vector store directory exists
        settings.create_vector_store_dir_img()

    def _initialize_index(self) -> None:
        """Initialize FAISS index if not already created."""
        if self.index is None:
            # Use L2 distance
            self.index = faiss.IndexFlatL2(settings.VECTOR_DIMENSION)
            logger.info(f"Initialized FAISS image index with dimension {settings.VECTOR_DIMENSION}")

    def create_index(self, products: List[Product]) -> None:
        """
        Create FAISS index from a list of captions records.

        """

        if not products:
            raise ValueError("Captions list cannot be empty")

        logger.info(f"Creating FAISS caption index for {len(products)} images")

        images = [p.image_url for p in products if p.image_url]
        ids = [p.id for p in products if p.id]

        # Prepare embeddings
        captions = self.image_service.generar_descripciones_simple(images, ids)
        embeddings = self.embedding_service.generate_embeddings_batch(texts)
        embeddings_array = np.array(embeddings, dtype=np.float32)


        # Initialize index and add
        self._initialize_index()
        self.index.add(embeddings_array)


        # Update mappings and store metadata
        for i, product in enumerate(products):
            faiss_index = self._next_index + i
            self.product_id_map[faiss_index] = product.id
            self.id_to_index_map[product.id] = faiss_index
            self.products[product.id] = product

        self._next_index += len(images)
        logger.info(f"Successfully created FAISS caption index with {len(images)} images")


    def add_caption(self, product: Product, caption: str = None) -> None:
        """
        Add a single caption embedding to the FAISS index.

        """
        if product.id in self.products:
            raise ValueError(f"Caption with ID {product.id} already exists")

        logger.info(f"Adding caption {product.id} to FAISS index")

        if caption is None:
            caption = self.image_service.generar_descripcion_imagen(product.image_url)
        
        if not caption:
            logger.warning(f"No caption generated for product {product.id}")
            return
            
        embeddings = self.embedding_service.generate_embedding(caption)
        embedding_array = np.array([embeddings], dtype=np.float32)    
        
        self._initialize_index()

        self.index.add(embedding_array)

        faiss_index = self._next_index
        self.product_id_map[faiss_index] = product.id
        self.id_to_index_map[product.id] = faiss_index
        self.products[product.id] = product
        self._next_index += 1

        logger.info(f"Successfully added caption {product.id} to FAISS index")

    def update_caption(self, product: Product) -> None:
        """
        Update an existing caption's embedding/metadata. For FAISS we rebuild the index.
        """
        if product.id not in self.products:
            raise ValueError(f"Caption with ID {product.id} does not exist")

        logger.info(f"Updating caption {product.id} in FAISS index")

        self.products[product.id] = product

        self._rebuild_index()

        logger.info(f"Successfully updated caption {product.id} in FAISS index")

    def delete_caption(self, caption_id: str) -> None:
        """
        Delete an caption from the index and rebuild.
        """
        if caption_id not in self.products:
            raise ValueError(f"Caption with ID {caption_id} does not exist")

        logger.info(f"Deleting caption {caption_id} from FAISS index")

        # Remove from mappings
        faiss_index = self.id_to_index_map[caption_id]
        del self.product_id_map[faiss_index]
        del self.id_to_index_map[caption_id]
        del self.products[caption_id]

        self._rebuild_index()

        logger.info(f"Successfully deleted caption {caption_id} from FAISS index")

    def search_by_embedding(self, embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        if embedding is None:
            raise ValueError("Embedding cannot be None")

        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS caption index is empty")
            return []

        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(embedding, k)

        results = []
        for i, (distance, faiss_index) in enumerate(zip(distances[0], indices[0])):
            if faiss_index in self.product_id_map:
                product_id = self.product_id_map[faiss_index]
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                similarity_score = 1.0 / (1.0 + distance)
                results.append((product_id, similarity_score))
        
        return results

    def _rebuild_index(self) -> None:
        """Rebuild the FAISS index from current images.
        """
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
        Save FAISS caption index and mappings to disk.
        """
        if path is None:
            path = settings.VECTOR_STORE_PATH_IMG

        os.makedirs(path, exist_ok=True)
        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, os.path.join(path, "scenexplain_index.faiss"))

            # Save mappings and products
            metadata = {
                "product_id_map": self.product_id_map,
                "id_to_index_map": self.id_to_index_map,
                "products": self.products,
                "next_index": self._next_index,
                "dimension": self.dimension
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
            path = settings.VECTOR_STORE_PATH_IMG
        
        index_path = os.path.join(path, "scenexplain_index.faiss")
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
            self.dimension = metadata["dimension"]
            
            logger.info(f"Loaded FAISS index from {path}")
        else:
            logger.info("No existing index found, starting fresh")

    def get_product_count(self) -> int:
        """Get the number of products in the index."""
        return len(self.products)
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID."""
        return self.products.get(product_id) 