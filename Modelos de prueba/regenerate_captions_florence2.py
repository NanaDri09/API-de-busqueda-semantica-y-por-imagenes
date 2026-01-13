#!/usr/bin/env python3
"""
Script para regenerar captions usando Florence-2 y eliminar productos con imágenes inválidas.
"""

import psycopg2
import os
import sys
import logging
from typing import Optional
from PIL import Image
from dotenv import load_dotenv
from transformers import AutoProcessor, AutoModelForCausalLM
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


class Florence2CaptionGenerator:
    """Clase para regenerar captions usando Florence-2."""
    
    def __init__(self):
        """Inicializar servicios y modelo Florence-2."""
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
        
        # Inicializar modelo Florence-2
        self._init_florence2_model()
        
        # Conexión a base de datos
        self.conn = None
        self.cursor = None
        self._connect_db()
        
        # Lista de productos eliminados
        self.deleted_products = []
    
    def _init_florence2_model(self):
        """Inicializar modelo Florence-2."""
        try:
            model_name = "microsoft/Florence-2-base"
            logger.info(f"Cargando modelo Florence-2: {model_name}")
            
            self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
            
            self.device = torch.device("cpu")
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Modelo Florence-2 cargado en: {self.device}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo Florence-2: {e}")
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
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                full_path = os.path.join(os.path.dirname(__file__), image_path)
                if not os.path.exists(full_path):
                    return None
                image = Image.open(full_path)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
            
        except Exception as e:
            return None
    
    def generate_caption(self, image: Image.Image) -> Optional[str]:
        """Generar caption detallado usando Florence-2."""
        try:
            # Usar prompt para descripción detallada (más completa)
            prompt = "<MORE_DETAILED_CAPTION>"
            inputs = self.processor(text=prompt, images=image, return_tensors="pt")
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=150,  # Más tokens para descripciones completas
                    num_beams=3
                )
            
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = self.processor.post_process_generation(
                generated_text, 
                task="<MORE_DETAILED_CAPTION>", 
                image_size=(image.width, image.height)
            )
            
            caption = parsed_answer.get('<MORE_DETAILED_CAPTION>', '')
            return caption.strip() if caption else None
            
        except Exception as e:
            logger.error(f"Error generando caption: {e}")
            return None
    
    def get_all_products(self):
        """Obtener TODOS los productos."""
        try:
            query = """
            SELECT id_producto, image_path 
            FROM producto 
            WHERE image_path IS NOT NULL AND image_path != ''
            ORDER BY id_producto
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    def delete_product(self, product_id: str) -> bool:
        """Eliminar producto de la base de datos."""
        try:
            delete_embedding_sql = "DELETE FROM embeddings WHERE id_producto = %s"
            self.cursor.execute(delete_embedding_sql, (product_id,))
            
            delete_product_sql = "DELETE FROM producto WHERE id_producto = %s"
            self.cursor.execute(delete_product_sql, (product_id,))
            
            self.deleted_products.append(product_id)
            logger.info(f"Producto {product_id} eliminado de la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando producto {product_id}: {e}")
            return False
    
    def update_product_caption(self, product_id: str, caption: str) -> bool:
        """Actualizar caption del producto."""
        try:
            update_sql = "UPDATE producto SET caption = %s WHERE id_producto = %s"
            self.cursor.execute(update_sql, (caption, product_id))
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando caption para {product_id}: {e}")
            return False
    
    def update_caption_embedding(self, product_id: str, caption: str) -> bool:
        """Generar y actualizar embedding del caption."""
        try:
            caption_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(caption)
            
            update_sql = "UPDATE embeddings SET embedding_caption = %s WHERE id_producto = %s"
            self.cursor.execute(update_sql, (caption_embedding, product_id))
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando embedding caption para {product_id}: {e}")
            return False
    
    def process_all_products(self):
        """Procesar todos los productos con Florence-2."""
        try:
            products = self.get_all_products()
            logger.info(f"Encontrados {len(products)} productos para procesar")
            
            if not products:
                logger.info("No hay productos para procesar")
                return
            
            successful_captions = 0
            deleted_count = 0
            
            for i, (product_id, image_path) in enumerate(products, 1):
                logger.info(f"Procesando producto {i}/{len(products)}: {product_id}")
                
                try:
                    image = self.load_image_from_path(image_path)
                    if not image:
                        if self.delete_product(product_id):
                            deleted_count += 1
                        self.conn.commit()
                        continue
                    
                    caption = self.generate_caption(image)
                    if not caption:
                        logger.warning(f"No se pudo generar caption para {product_id}")
                        continue
                    
                    logger.info(f"Caption generado para {product_id}: {caption}")
                    
                    if self.update_product_caption(product_id, caption):
                        if self.update_caption_embedding(product_id, caption):
                            successful_captions += 1
                            logger.info(f"Caption y embedding actualizados para {product_id}")
                    
                    self.conn.commit()
                    
                except Exception as e:
                    logger.error(f"Error procesando producto {product_id}: {e}")
                    self.conn.rollback()
            
            logger.info(f"Procesamiento completado:")
            logger.info(f"- Captions generados: {successful_captions}")
            logger.info(f"- Productos eliminados: {deleted_count}")
            
            if self.deleted_products:
                logger.info("IDs de productos eliminados:")
                for product_id in self.deleted_products:
                    logger.info(f"  - {product_id}")
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {e}")
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
        logger.info("Iniciando regeneración de captions con Florence-2...")
        
        generator = Florence2CaptionGenerator()
        generator.process_all_products()
        
        logger.info("Procesamiento completado exitosamente")
        
        if generator.deleted_products:
            print("\n" + "="*60)
            print("PRODUCTOS ELIMINADOS DE LA BASE DE DATOS:")
            print("="*60)
            for product_id in generator.deleted_products:
                print(f"ID: {product_id}")
            print("="*60)
        
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}")
        sys.exit(1)
        
    finally:
        if generator:
            generator.close_connection()


if __name__ == "__main__":
    main()