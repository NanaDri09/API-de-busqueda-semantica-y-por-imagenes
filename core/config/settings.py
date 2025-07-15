import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Configuration settings for the semantic search system."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "text-embedding-3-small")
    
    # Search Configuration
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "10"))
    DEFAULT_BM25_WEIGHT: float = float(os.getenv("DEFAULT_BM25_WEIGHT", "0.4"))
    DEFAULT_VECTOR_WEIGHT: float = float(os.getenv("DEFAULT_VECTOR_WEIGHT", "0.6"))
    
    # BM25 Configuration
    BM25_K1: float = float(os.getenv("BM25_K1", "1.2"))
    BM25_B: float = float(os.getenv("BM25_B", "0.75"))
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "data/vector_store")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "1536"))  # OpenAI embedding dimension
    
    # Performance Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate_openai_key(cls) -> bool:
        """Validate that OpenAI API key is configured."""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY.strip())
    
    @classmethod
    def get_search_weights(cls) -> List[float]:
        """Get normalized search weights for BM25 and vector search."""
        total = cls.DEFAULT_BM25_WEIGHT + cls.DEFAULT_VECTOR_WEIGHT
        return [cls.DEFAULT_BM25_WEIGHT / total, cls.DEFAULT_VECTOR_WEIGHT / total]
    
    @classmethod
    def create_vector_store_dir(cls) -> None:
        """Create vector store directory if it doesn't exist."""
        os.makedirs(cls.VECTOR_STORE_PATH, exist_ok=True)


# Global settings instance
settings = Settings() 