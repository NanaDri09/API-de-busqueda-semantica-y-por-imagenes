#!/usr/bin/env python3
"""
Script para generar captions de productos existentes usando modelo local ViT-GPT2.
Actualiza el campo caption y su embedding correspondiente.
"""

import psycopg2
import os
import sys
import logging
from typing import Optional
from PIL import Image
from dotenv import load_dotenv
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar servicios
from core.services.product_service import ProductService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Clase para generar captions usando modelo local ViT-GPT2."""
    
    def __init__(self):
        """Inicializar servicios y modelo local."""
        self.db_config = {
            'dbname': 'Tesis',
            'user': 'postgres', 
            'password': '1234',
            'host': 'localhost',
            'port': '5433'
        }
        
        # Inicializar servicios
        try:
            self.product_service = ProductService()
            logger.info("Servicios inicializados correctamente")
        except Exception as e:
            logger.error(f"Error inicializando servicios: {e}")
            raise
        
        # Inicializar modelo local
        self._init_local_model()
        
        # Conexión a base de datos
        self.conn = None
        self.cursor = None
        self._connect_db()
    
    def _init_local_model(self):
        """Inicializar modelo ViT-GPT2 local."""
        try:
            model_name = "nlpconnect/vit-gpt2-image-captioning"
            logger.info(f"Cargando modelo local: {model_name}")
            
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Configurar device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Modelo cargado en: {self.device}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo local: {e}")
            raise
    
    def _connect_db(self):
        """Conectar a la base de datos PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("Conexión a base de datos establecida")
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            raise
    
    def load_image_from_path(self, image_path: str) -> Optional[Image.Image]:
        """Cargar imagen desde ruta local."""
        try:
            full_path = os.path.join(os.path.dirname(__file__), image_path)
            
            if not os.path.exists(full_path):
                logger.warning(f"Imagen no encontrada: {full_path}")
                return None
            
            image = Image.open(full_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
            
        except Exception as e:
            logger.warning(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def generate_caption(self, image: Image.Image) -> Optional[str]:
        """Generar caption usando modelo local."""
        try:
            # Procesar imagen
            pixel_values = self.feature_extractor(images=image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generar caption
            with torch.no_grad():
                output_ids = self.model.generate(pixel_values, max_length=50, num_beams=4)
            
            # Decodificar
            caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            return caption.strip()
            
        except Exception as e:
            logger.error(f"Error generando caption: {e}")
            return None
    
    def get_products_without_captions(self):
        """Obtener productos sin captions."""
        try:
            query = """
            SELECT id_producto, image_path 
            FROM producto 
            WHERE caption IS NULL OR caption = ''
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    def update_product_caption(self, product_id: str, caption: str) -> bool:
        """Actualizar caption del producto."""
        try:
            update_sql = """
            UPDATE producto 
            SET caption = %s 
            WHERE id_producto = %s
            """
            self.cursor.execute(update_sql, (caption, product_id))
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando caption para {product_id}: {e}")
            return False
    
    def update_caption_embedding(self, product_id: str, caption: str) -> bool:
        """Generar y actualizar embedding del caption."""
        try:
            # Generar embedding del caption
            caption_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(caption)
            
            # Actualizar en base de datos
            update_sql = """
            UPDATE embeddings 
            SET embedding_caption = %s 
            WHERE id_producto = %s
            """
            self.cursor.execute(update_sql, (caption_embedding, product_id))
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando embedding caption para {product_id}: {e}")
            return False
    
    def process_captions(self):
        """Procesar todos los productos sin captions."""
        try:
            # Obtener productos sin captions
            products = self.get_products_without_captions()
            logger.info(f"Encontrados {len(products)} productos sin captions")
            
            if not products:
                logger.info("No hay productos para procesar")
                return
            
            successful_captions = 0
            failed_captions = 0
            
            for i, (product_id, image_path) in enumerate(products, 1):
                logger.info(f"Procesando producto {i}/{len(products)}: {product_id}")
                
                try:
                    # Cargar imagen
                    image = self.load_image_from_path(image_path)
                    if not image:
                        logger.warning(f"No se pudo cargar imagen para {product_id}")
                        failed_captions += 1
                        continue
                    
                    # Generar caption
                    caption = self.generate_caption(image)
                    if not caption:
                        logger.warning(f"No se pudo generar caption para {product_id}")
                        failed_captions += 1
                        continue
                    
                    logger.info(f"Caption generado para {product_id}: {caption}")
                    
                    # Actualizar caption en producto
                    if self.update_product_caption(product_id, caption):
                        # Actualizar embedding del caption
                        if self.update_caption_embedding(product_id, caption):
                            successful_captions += 1
                            logger.info(f"Caption y embedding actualizados para {product_id}")
                        else:
                            failed_captions += 1
                            logger.error(f"Error actualizando embedding para {product_id}")
                    else:
                        failed_captions += 1
                        logger.error(f"Error actualizando caption para {product_id}")
                    
                    # Commit después de cada producto
                    self.conn.commit()
                    
                except Exception as e:
                    logger.error(f"Error procesando producto {product_id}: {e}")
                    failed_captions += 1
                    self.conn.rollback()
            
            logger.info(f"Procesamiento completado: {successful_captions} exitosos, {failed_captions} fallidos")
            
        except Exception as e:
            logger.error(f"Error en procesamiento de captions: {e}")
            raise
    
    def close_connection(self):
        """Cerrar conexión a base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Conexión a base de datos cerrada")


def main():
    """Función principal del script."""
    generator = None
    
    try:
        logger.info("Iniciando generación de captions...")
        
        generator = CaptionGenerator()
        generator.process_captions()
        
        logger.info("Generación de captions completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en generación de captions: {e}")
        sys.exit(1)
        
    finally:
        if generator:
            generator.close_connection()


if __name__ == "__main__":
    main()