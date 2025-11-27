from typing import List, Tuple, Dict, Optional, Union
from ..repositories.vector_repository import VectorRepository
from ..repositories.bm25_repository import BM25Repository
from ..repositories.image_repository import ImageRepository
from ..repositories.caption_repository import CaptionRepository
from ..config.settings import settings
from .rrf_service import RRFService
import logging
from ..services.image_service import ImageService
import os
from PIL import Image
import faiss
from typing import List, Tuple, Dict, Optional, Union
from ..repositories.vector_repository import VectorRepository
from ..repositories.bm25_repository import BM25Repository
from ..repositories.image_repository import ImageRepository
from ..repositories.caption_repository import CaptionRepository
from ..config.settings import settings
from .rrf_service import RRFService
import logging
from ..services.image_service import ImageService
import os
from PIL import Image
import faiss
import numpy as np
import time


logger = logging.getLogger(__name__)


class SearchService:
    """Service for orchestrating hybrid search operations."""
    
    def __init__(self, vector_repo: VectorRepository, bm25_repo: BM25Repository, image_repo : ImageRepository, caption_repo: CaptionRepository, image_service: ImageService, rrf_service: Optional[RRFService] = None):
        """
        Initialize the search service.
        
        Args:
            vector_repo: Vector repository for semantic search
            bm25_repo: BM25 repository for keyword search
            rrf_service: RRF service for advanced fusion (optional)
        """
        self.vector_repo = vector_repo
        self.bm25_repo = bm25_repo
        self.image_repo = image_repo
        self.caption_repo = caption_repo
        self.image_service = image_service
        self.rrf_service = rrf_service or RRFService()
    
    def hybrid_search(
        self,
        query: str,
        bm25_weight: float = None,
        vector_weight: float = None,
        top_k: int = None
    ) -> List[str]:
        """
        Perform hybrid search combining BM25 and vector search.
        
        Args:
            query: Search query
            bm25_weight: Weight for BM25 results (defaults to settings)
            vector_weight: Weight for vector results (defaults to settings)
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by combined score
            
        Raises:
            ValueError: If query is empty or weights are invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Use default values if not provided
        if bm25_weight is None:
            bm25_weight = settings.DEFAULT_BM25_WEIGHT
        if vector_weight is None:
            vector_weight = settings.DEFAULT_VECTOR_WEIGHT
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        # Validate weights
        if bm25_weight < 0 or vector_weight < 0:
            raise ValueError("Weights must be non-negative")
        
        total_weight = bm25_weight + vector_weight
        if total_weight == 0:
            raise ValueError("At least one weight must be positive")
        
        # Normalize weights
        bm25_weight = bm25_weight / total_weight
        vector_weight = vector_weight / total_weight
        
        logger.info(f"Performing hybrid search for query: '{query}' with weights BM25={bm25_weight:.2f}, Vector={vector_weight:.2f}")
        
        # Get results from both search methods
        # Request more results from each method to ensure good coverage
        search_k = min(top_k * 2, 50)  # Get more results for better ranking
        
        bm25_results = self.bm25_repo.search_keywords(query, k=search_k)
        vector_results = self.vector_repo.search_similar(query, k=search_k)
        
        # Combine scores
        combined_results = self.combine_scores(
            bm25_results, vector_results, [bm25_weight, vector_weight]
        )
        
        # Return top-k results
        return [product_id for product_id, _ in combined_results[:top_k]]
    
    def keyword_search(self, query: str, top_k: int = None) -> List[str]:
        """
        Perform keyword-only search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by BM25 score
            
        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing keyword search for query: '{query}'")
        
        results = self.bm25_repo.search_keywords(query, k=top_k)
        return [product_id for product_id, _ in results]
    
    def semantic_search(self, query: str, top_k: int = None) -> List[str]:
        """
        Perform semantic-only search using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of product IDs ranked by semantic similarity
            
        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing semantic search for query: '{query}'")
        
        results = self.vector_repo.search_similar(query, k=top_k)
        return [product_id for product_id, _ in results]
    
    def combine_scores(
        self,
        bm25_results: List[Tuple[str, float]],
        vector_results: List[Tuple[str, float]],
        weights: List[float]
    ) -> List[Tuple[str, float]]:
        """
        Combine scores from BM25 and vector search results.
        
        Args:
            bm25_results: List of (product_id, score) from BM25 search
            vector_results: List of (product_id, score) from vector search
            weights: [bm25_weight, vector_weight] normalized weights
            
        Returns:
            List of (product_id, combined_score) sorted by score descending
        """
        bm25_weight, vector_weight = weights
        
        # Normalize scores within each result set
        bm25_scores = self._normalize_scores(bm25_results)
        vector_scores = self._normalize_scores(vector_results)
        
        # Combine scores
        combined_scores: Dict[str, float] = {}
        
        # Add BM25 scores
        for product_id, score in bm25_scores.items():
            combined_scores[product_id] = combined_scores.get(product_id, 0) + (score * bm25_weight)
        
        # Add vector scores
        for product_id, score in vector_scores.items():
            combined_scores[product_id] = combined_scores.get(product_id, 0) + (score * vector_weight)
        
        # Sort by combined score (descending)
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results
    
    def _normalize_scores(self, results: List[Tuple[str, float]]) -> Dict[str, float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        
        Args:
            results: List of (product_id, score) tuples
            
        Returns:
            Dictionary of product_id -> normalized_score
        """
        if not results:
            return {}
        
        scores = [score for _, score in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        if max_score == min_score:
            return {product_id: 1.0 for product_id, _ in results}
        
        # Min-max normalization
        normalized = {}
        for product_id, score in results:
            normalized_score = (score - min_score) / (max_score - min_score)
            normalized[product_id] = normalized_score
        
        return normalized
    
    def rrf_search(
        self,
        query: str,
        k: int = None,
        top_k: int = None
    ) -> List[str]:
        """
        Perform search using Reciprocal Rank Fusion (RRF).
        
        Args: 
            query: Search query
            k: RRF parameter (higher values reduce impact of rank differences)
            top_k: Number of results to return
            
        Returns:
            List of product IDs ranked by RRF score
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Use optimized RRF k value (lower = more aggressive fusion)
        if k is None:
            k = 20  # Optimized value: more aggressive than standard 60
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"Performing RRF search for query: '{query}' with k={k}")
        
        # Use larger and more balanced retrieval for better fusion
        retrieval_limit = max(top_k * 5, 100)  # Increased from 3x to 5x
        
        # Get BM25 results
        bm25_results = self.keyword_search(query, top_k=retrieval_limit)
        logger.debug(f"BM25 search returned {len(bm25_results)} results")
        
        # Get vector results
        vector_results = self.semantic_search(query, top_k=retrieval_limit)
        logger.debug(f"Vector search returned {len(vector_results)} results")
        
        # Apply RRF fusion with optimized parameters
        final_results = self.rrf_service.combine_search_results(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=k,
            top_k=top_k
        )
        
        logger.info(f"RRF search completed: {len(final_results)} final results")
        return final_results

#----------------------------------------------------------------------------------------------------------------------------

    def search_by_image_A(self, query_image: Union[str, Image.Image], k = 10):

        if not query_image:
            raise ValueError("Query cannot be empty")

        if k is None:
            k = 10

        logger.info(f"Performing image search for query image with k={k}")

        # Calcular embedding de la consulta
        q_emb = self.image_service._compute_image_embedding(query_image)
        logger.info(f"Embedding shape: {q_emb.shape}")
        logger.info(f"Embedding type: {type(q_emb)}")
        logger.info(f"Embedding dtype: {q_emb.dtype}") 

        results = self.image_repo.search_by_embedding(embedding=q_emb, k=k)
        return results


    def search_by_caption_A(self, query_image: Union[str, Image.Image], k = 10):
        if not query_image:
            raise ValueError("Query cannot be empty")

        if k is None:
            k = 10

        logger.info(f"Performing caption search for query image with k={k}")

        start = time.perf_counter()
        try:
            if isinstance(query_image, Image.Image):
                # Generar caption
                caption = self.image_service.generar_descripcion_imagen(query_image)
            else:
                caption = query_image

            if not caption or not isinstance(caption, str) or not caption.strip():
                raise RuntimeError("No caption generated from image")

            # Obtener embedding (puede lanzar excepción si falla la API)
            embeddings = self.vector_repo.embedding_service.generate_embedding(caption.strip())

            # Asegurar formato correcto para FAISS: array 2D float32
            embedding_array = np.array([embeddings], dtype=np.float32)
            if embedding_array.ndim != 2:
                raise RuntimeError(f"Embedding has unexpected ndim={embedding_array.ndim}")

            # Verificar que el índice de captions exista
            if getattr(self.caption_repo, 'index', None) is None or getattr(self.caption_repo.index, 'ntotal', 0) == 0:
                # No hay índice de captions: devolver lista vacía (mejor que 500) y loggear
                logger.warning("Caption index empty - returning no results")
                elapsed = time.perf_counter() - start
                logger.info(f"search_by_caption_A elapsed (no index): {elapsed:.3f}s")
                return []

            # Ejecutar búsqueda en FAISS
            results = self.caption_repo.search_by_embedding(embedding_array, k=k)
            elapsed = time.perf_counter() - start
            logger.info(f"search_by_caption_A elapsed: {elapsed:.3f}s")
            return results

        except Exception as e:
            # Log detallado para diagnóstico (incluye stacktrace)
            logger.exception(f"Error during caption search: {e}")
            # Re-raise for API layer to return 500 (keeps behavior) but with clearer message
            raise



    def search_by_description_A(self, image: Union[str, Image.Image], k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for products based on an image by generating a caption and using it for semantic search.
        
        Args:
            image: Input image (file path or PIL Image)
            k: Number of results to return
        """
        if not image:
            raise ValueError("Image cannot be empty")

        if k is None:
            k = 10

        logger.info(f"Performing description-based search for input image with k={k}")

        if isinstance(query_image, Image.Image):
            # Generar caption
            caption = self.image_service.generar_descripcion_imagen(query_image)
        else:
            caption = query_image

        if not caption:
            raise ValueError("Failed to generate caption from image")

        logger.debug(f"Generated caption: {caption}")

        # Search in vector repository using the caption embedding
        results = self.vector_repo.search_similar(caption, k=k)
        return results

    def hydrid_search_image_A(self, query_image: Union[str, Image.Image], k: int = 10, peso_imagen: float = 0.4, peso_caption: float = 0.2, peso_description= 0.2, umbral: float = 0.0) -> List[Tuple[str, float]]:

        if not query_image:
            raise ValueError("Query cannot be empty")

        if k is None:
            k = 10


        if not (peso_imagen >= 0 and peso_caption >= 0 and peso_description >= 0):
            raise ValueError("Los pesos deben ser no negativos")
        
        total = peso_imagen + peso_caption + peso_description

        if not (total == 1):
            raise ValueError("Los pesos deben sumar 1")
        
        caption = self.image_service.generar_descripcion_imagen(query_image)

        # Buscar en ambos índices
        images = self.search_by_image_A(query_image, k*2)
        captions = self.search_by_caption_A(caption, k*2)
        descriptions = self.search_by_description_A(caption, k*2)

        # Construir diccionarios (tomar la mejor similitud por pid)
        sim_img = {}
        for pid, sim in images:
            sim_img[pid] = max(sim_img.get(pid, 0.0), float(sim))

        sim_cap = {}
        for pid, sim in captions:
            sim_cap[pid] = max(sim_cap.get(pid, 0.0), float(sim))

        sim_des = {}
        for pid, sim in descriptions:
            sim_des[pid] = max(sim_des.get(pid, 0.0), float(sim))

        # Combinar scores ponderados
        all_ids = set(sim_img) | set(sim_cap) | set(sim_des)
        combined = []
        for pid in all_ids:
            s_i = float(sim_img.get(pid, 0.0))
            s_c = float(sim_cap.get(pid, 0.0))
            s_d = float(sim_des.get(pid, 0.0))
            score = s_i * peso_imagen + s_c * peso_caption + s_d * peso_description
            if score >= float(umbral):
                combined.append((pid, s_i, s_c, s_d, score))

        # Ordenar por score y retornar top-k
        combined.sort(key=lambda x: x[4], reverse=True)
        return combined[:k]

    def hybrid_search_image_description_A(
        self,
        query_image: Union[str, Image.Image],
        query: str,
        k: int = 5,
        peso_imagen: float = 0.4,
        peso_caption: float = 0.2,
        peso_description: float = 0.4,
        umbral: float = 0.0,
        tol: float = 1e-6
    ) -> List[Tuple[str, float, float, float, float]]:

        if not query_image:
            raise ValueError("Query cannot be empty")

        if k is None:
            k = 10

        # Validación de pesos con tolerancia
        if not (peso_imagen >= 0 and peso_caption >= 0 and peso_description >= 0):
            raise ValueError("Los pesos deben ser no negativos")
        total = peso_imagen + peso_caption + peso_description
        if abs(total - 1.0) > tol:
            raise ValueError(f"Los pesos deben sumar 1 (suma actual = {total})")

        # Ejecutar búsquedas (estas funciones deben devolver [(pid, sim), ...], sim en (0,1])
        images = self.search_by_image_A(query_image, k * 2)     # [(pid, sim), ...]
        captions = self.search_by_caption_A(query_image, k * 2) # [(pid, sim), ...]
        descriptions = self.vector_repo.search_similar(query, k * 2)    # [(pid, sim), ...]

        # Construir diccionarios (tomar la mejor similitud por pid)
        sim_img = {}
        for pid, sim in images:
            sim_img[pid] = max(sim_img.get(pid, 0.0), float(sim))

        sim_cap = {}
        for pid, sim in captions:
            sim_cap[pid] = max(sim_cap.get(pid, 0.0), float(sim))

        sim_des = {}
        for pid, sim in descriptions:
            sim_des[pid] = max(sim_des.get(pid, 0.0), float(sim))

        # Combinar scores ponderados
        all_ids = set(sim_img) | set(sim_cap) | set(sim_des)
        combined = []
        for pid in all_ids:
            s_i = float(sim_img.get(pid, 0.0))
            s_c = float(sim_cap.get(pid, 0.0))
            s_d = float(sim_des.get(pid, 0.0))
            score = s_i * peso_imagen + s_c * peso_caption + s_d * peso_description
            if score >= float(umbral):
                combined.append((pid, s_i, s_c, s_d, score))

        # Ordenar por score y retornar top-k
        combined.sort(key=lambda x: x[4], reverse=True)
        return combined[:k]

#-------------------------------------------------------------------------------------------------------------------

    def get_search_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the search indexes.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "vector_index_size": self.vector_repo.get_product_count(),
            "bm25_index_size": self.bm25_repo.get_product_count(),
            "total_products": max(
                self.vector_repo.get_product_count(),
                self.bm25_repo.get_product_count()
            )
        } 
