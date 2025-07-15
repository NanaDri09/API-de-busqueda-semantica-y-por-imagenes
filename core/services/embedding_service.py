import time
from typing import List, Optional
from openai import OpenAI
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""
    
    def __init__(self):
        """Initialize the embedding service."""
        if not settings.validate_openai_key():
            raise ValueError("OpenAI API key is not configured")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_retries = settings.MAX_RETRIES
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            ValueError: If text is empty
            Exception: If OpenAI API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text.strip()
                )
                return response.data[0].embedding
            
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to generate embedding after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If texts list is empty
            Exception: If OpenAI API call fails after retries
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValueError("No valid texts provided")
        
        # Process in batches to avoid API limits
        batch_size = min(settings.BATCH_SIZE, len(valid_texts))
        embeddings = []
        
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]
            
            for attempt in range(self.max_retries):
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    break
                
                except Exception as e:
                    logger.warning(f"Batch embedding attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Failed to generate batch embeddings after {self.max_retries} attempts: {e}")
                    time.sleep(2 ** attempt)
        
        return embeddings
    
    def combine_title_description(self, title: str, description: str) -> str:
        """
        Combine title and description for embedding generation.
        
        Args:
            title: Product title
            description: Product description
            
        Returns:
            Combined text optimized for embedding
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        
        # Combine with title having more weight
        return f"{title.strip()} {description.strip()}"
    
    def validate_embedding_dimension(self, embedding: List[float]) -> bool:
        """
        Validate that embedding has the expected dimension.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if dimension is correct
        """
        return len(embedding) == settings.VECTOR_DIMENSION 