#!/usr/bin/env python3
"""
Script para regenerar TODOS los captions de productos usando modelo BLIP-base.
Actualiza el campo caption y su embedding correspondiente para todos los productos.
"""

import psycopg2
import os
import sys
import logging
from typing import Optional
from PIL import Image
from dotenv import load_dotenv
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import requests
from io import BytesIO

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


class BlipCaptionGenerator:
    """Clase para regenerar captions usando modelo BLIP-base."""
    
    def __init__(self):
        """Inicializar servicios y modelo BLIP."""
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
        
        # Inicializar modelo BLIP
        self._init_blip_model()
        
        # Conexión a base de datos
        self.conn = None
        self.cursor = None
        self._connect_db()
    
    def _init_blip_model(self):
        """Inicializar modelo BLIP-base."""
        try:
            model_name = "Salesforce/blip-image-captioning-base"
            logger.info(f"Cargando modelo BLIP: {model_name}")
            
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            self.device = torch.device("cpu")
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Modelo BLIP cargado en: {self.device}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo BLIP: {e}")
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
        """Cargar imagen desde URL o ruta local."""
        try:
            # Verificar si es una URL
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                # Es una ruta local
                full_path = os.path.join(os.path.dirname(__file__), image_path)
                if not os.path.exists(full_path):
                    logger.warning(f"Imagen no encontrada: {full_path}")
                    return None
                image = Image.open(full_path)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
            
        except Exception as e:
            logger.warning(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def generate_caption(self, image: Image.Image) -> Optional[str]:
        """Generar caption usando BLIP-base."""
        try:
            inputs = self.processor(image, return_tensors="pt")
            
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=50, num_beams=5)
            
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption.strip()
            
        except Exception as e:
            logger.error(f"Error generando caption: {e}")
            return None
    
    def get_all_products(self):
        """Obtener TODOS los productos con imágenes válidas."""
        try:
            query = """
            SELECT id_producto, image_path 
            FROM producto 
            WHERE image_path IS NOT NULL 
            AND image_path != '' 
            AND (image_path LIKE 'http%' OR image_path NOT LIKE 'http%')
            ORDER BY id_producto
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
    
    def regenerate_all_captions(self):
        """Regenerar TODOS los captions de productos."""
        try:
            # Obtener TODOS los productos
            products = self.get_all_products()
            logger.info(f"Encontrados {len(products)} productos para procesar")
            
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
                    
                    # Generar caption con BLIP
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
            
            logger.info(f"Regeneración completada: {successful_captions} exitosos, {failed_captions} fallidos")
            
        except Exception as e:
            logger.error(f"Error en regeneración de captions: {e}")
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
        logger.info("Iniciando regeneración de TODOS los captions con BLIP-base...")
        
        generator = BlipCaptionGenerator()
        generator.regenerate_all_captions()
        
        logger.info("Regeneración de captions completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en regeneración de captions: {e}")
        sys.exit(1)
        
    finally:
        if generator:
            generator.close_connection()


if __name__ == "__main__":
    main()