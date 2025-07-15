from dataclasses import dataclass
from typing import Optional
from langchain.schema import Document
from pydantic import BaseModel, validator


@dataclass
class Product:
    """Product data model for semantic search."""
    id: str
    title: str
    description: str
    
    def __post_init__(self):
        """Validate product data after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Product ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Product title cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Product description cannot be empty")
    
    def get_combined_text(self) -> str:
        """Combine title and description for embedding generation."""
        return f"{self.title} {self.description}"
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description
        }


class ProductDocument(Document):
    """LangChain Document wrapper for Product."""
    
    def __init__(self, product: Product):
        super().__init__(
            page_content=product.get_combined_text(),
            metadata={"product_id": product.id, "title": product.title}
        )
    
    @property
    def product_id(self) -> str:
        """Get product ID from metadata."""
        return self.metadata["product_id"]
    
    @property
    def product_title(self) -> str:
        """Get product title from metadata."""
        return self.metadata["title"]


class ProductCreate(BaseModel):
    """Pydantic model for product creation validation."""
    id: str
    title: str
    description: str
    
    @validator('id', 'title', 'description')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class ProductUpdate(BaseModel):
    """Pydantic model for product update validation."""
    title: Optional[str] = None
    description: Optional[str] = None
    
    @validator('title', 'description')
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v 