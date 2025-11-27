from dataclasses import dataclass
from typing import Optional, Dict, Any
from langchain.schema import Document
from pydantic import BaseModel, validator
import os
import uuid
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import io

def images_dir(project_file: Optional[Path] = None) -> Path:
    """
    Devuelve la carpeta 'Imagenes' en la raíz del proyecto (crea si no existe).
    project_file: Path(__file__) del módulo que llama; si None, infiere desde este archivo.
    """
    if project_file is None:
        # Si se llama desde otro sitio, fallback: resolución relativa a este archivo
        project_root = Path(__file__).resolve().parents[2]
    else:
        project_root = Path(project_file).resolve().parents[2]
    img_dir = project_root / "Imagenes"
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir

def _detect_extension_from_bytes(image_bytes: bytes) -> Optional[str]:
    """
    Detecta el formato usando Pillow. Devuelve extensión con punto, por ejemplo '.jpg' o '.png'.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        fmt = img.format  # 'JPEG', 'PNG', 'WEBP', ...
        if not fmt:
            return None
        fmt = fmt.upper()
        # Mapear formatos conocidos a extensiones
        mapping = {
            "JPEG": ".jpg",
            "JPG": ".jpg",
            "PNG": ".png",
            "WEBP": ".webp",
            "BMP": ".bmp",
            "GIF": ".gif",
            "TIFF": ".tiff",
        }
        return mapping.get(fmt, f".{fmt.lower()}")
    except UnidentifiedImageError:
        return None
    except Exception:
        return None

def save_image_bytes(image_bytes: bytes,
                     filename_hint: Optional[str] = None,
                     project_file: Optional[Path] = None) -> str:
    """
    Guarda image_bytes en la carpeta 'Imagenes' del proyecto y devuelve la ruta relativa:
    'Imagenes/<filename>'.
    - Comprueba que bytes sean una imagen válida.
    - Usa extensión detectada preferentemente, luego filename_hint si tiene extensión.
    - Genera nombre único con uuid para evitar colisiones.
    """
    if not isinstance(image_bytes, (bytes, bytearray)) or len(image_bytes) == 0:
        raise ValueError("image_bytes must be non-empty bytes")

    # validar imagen con Pillow
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # lanza excepción si no es imagen válida
    except UnidentifiedImageError:
        raise ValueError("Uploaded file is not a valid image")
    except Exception as e:
        raise ValueError(f"Error validating image: {e}")

    # detectar extensión preferida por inspección de bytes
    ext = _detect_extension_from_bytes(image_bytes)

    # si no detectó, intentar usar filename_hint extension
    if not ext and filename_hint and "." in filename_hint:
        ext = os.path.splitext(filename_hint)[1].lower()

    # fallback a .jpg
    if not ext:
        ext = ".jpg"

    # generar filename seguro
    filename = f"{uuid.uuid4().hex}{ext}"

    # obtener carpeta Imagenes (respetando la estructura del proyecto)
    img_dir = images_dir(project_file)

    full_path = img_dir / filename

    # escribir de manera atómica: primero archivo temporal, luego rename
    tmp_path = img_dir / (filename + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(image_bytes)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.rename(full_path)

    # devolver ruta relativa normalizada (slash hacia adelante)
    rel = Path("Imagenes") / filename
    return str(rel.as_posix())

@dataclass
class Product:
    """Product data model for semantic search, with optional image URL."""
    id: str
    title: str
    description: str
    image_url: Optional[str] = None

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
            "description": self.description,
            "image_url": self.image_url,
        }

    def set_image(self, image_bytes: bytes, filename_hint: Optional[str] = None, project_file: Optional[Path] = None) -> None:
        """Set image_url by saving image_bytes to disk."""
        self.image_url = save_image_bytes(image_bytes, filename_hint, project_file)
        return self.image_url

    @classmethod
    def from_create(cls, payload: "ProductCreate", image_bytes: Optional[bytes] = None) -> "Product":
        """Create a Product instance from a ProductCreate pydantic object.

        If image_bytes is provided, the image will be saved under the project `Imagenes/`
        folder and the product's `image_url` will point to the saved file.
        """
        prod = cls(id=payload.id, title=payload.title, description=payload.description)
        # Prefer image bytes if provided
        if image_bytes:
            prod.set_image(image_bytes, getattr(payload, "image_filename_hint", None))
        elif getattr(payload, "image_url", None):
            prod.image_url = payload.image_url
        return prod

    def update_with(self, payload: "ProductUpdate", image_bytes: Optional[bytes] = None) -> None:
        """Update this Product instance with values from ProductUpdate.

        If image_bytes is provided, the image will be saved and `image_url` updated.
        If payload contains `image_url` but no image_bytes, the `image_url` will be set
        to the provided value.
        """
        if getattr(payload, "title", None) is not None:
            self.title = payload.title
        if getattr(payload, "description", None) is not None:
            self.description = payload.description
        # Image handling: image bytes take precedence over a raw image_url
        if image_bytes:
            self.set_image(image_bytes, getattr(payload, "image_filename_hint", None))
        elif getattr(payload, "image_url", None) is not None:
            self.image_url = payload.image_url


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
    image_url: Optional[str] = None
    
    @validator('id', 'title', 'description')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class ProductUpdate(BaseModel):
    """Pydantic model for product update validation."""
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    @validator('title', 'description')
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v 