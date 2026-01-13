#!/usr/bin/env python3
"""
Script para importar productos del JSON local y procesarlos con embeddings.
Solo guarda productos con imágenes válidas y embeddings generados exitosamente.
"""

import psycopg2
import os
import sys
import logging
from typing import List, Dict
from PIL import Image
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar servicios y datos
from core.services.product_service import ProductService
from data.productos_del_json_copy import PRODUCTS_JSON

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONProductImporter:
    """Clase para importar productos del JSON local."""
    
    def __init__(self):
        """Inicializar servicios y conexión a base de datos."""
        self.db_config = {
            'dbname': 'Tesis',
            'user': 'postgres', 
            'password': '1234',
            'host': 'localhost',
            'port': '5433'
        }
        
        try:
            self.product_service = ProductService()
            logger.info("Servicios inicializados correctamente")
        except Exception as e:
            logger.error(f"Error inicializando servicios: {e}")
            raise
        
        self.conn = None
        self.cursor = None
        self._connect_db()
        self._create_tables()
    
    def _connect_db(self):
        """Conectar a la base de datos PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("Conexión a base de datos establecida")
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            raise
    
    def _create_tables(self):
        """Crear las tablas necesarias si no existen."""
        try:
            create_tienda_sql = """
            CREATE TABLE IF NOT EXISTS tienda (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT
            );
            """
            
            create_producto_sql = """
            CREATE TABLE IF NOT EXISTS producto (
                id_producto VARCHAR(50) PRIMARY KEY,
                tienda_id INTEGER REFERENCES tienda(id),
                titulo VARCHAR(500) NOT NULL,
                descripcion TEXT,
                caption TEXT,
                image_path VARCHAR(500)
            );
            """
            
            create_embeddings_sql = """
            CREATE TABLE IF NOT EXISTS embeddings (
                id SERIAL PRIMARY KEY,
                id_producto VARCHAR(50) UNIQUE REFERENCES producto(id_producto),
                embedding_descripcion FLOAT8[],
                embedding_caption FLOAT8[],
                embedding_titulo FLOAT8[],
                embedding_imagen FLOAT8[]
            );
            """
            
            self.cursor.execute(create_tienda_sql)
            self.cursor.execute(create_producto_sql)
            self.cursor.execute(create_embeddings_sql)
            self.conn.commit()
            
            logger.info("Tablas creadas/verificadas correctamente")
            
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            self.conn.rollback()
            raise
    
    def load_image_from_path(self, image_path: str) -> Image.Image:
        """Cargar imagen desde ruta local."""
        try:
            # Construir ruta completa
            full_path = os.path.join(os.path.dirname(__file__), image_path)
            
            if not os.path.exists(full_path):
                logger.warning(f"Imagen no encontrada: {full_path}")
                return None
            
            image = Image.open(full_path)
            return image
            
        except Exception as e:
            logger.warning(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def create_store(self) -> int:
        """Obtener ID de la tienda existente."""
        try:
            self.cursor.execute("SELECT id FROM tienda LIMIT 1")
            result = self.cursor.fetchone()
            
            if result:
                store_id = result[0]
                logger.info(f"Usando tienda existente con ID: {store_id}")
                return store_id
            else:
                raise Exception("No se encontró ninguna tienda existente")
            
        except Exception as e:
            logger.error(f"Error obteniendo tienda: {e}")
            raise
    
    def save_product(self, product: Dict, store_id: int) -> bool:
        """Guardar producto en base de datos."""
        try:
            insert_product_sql = """
            INSERT INTO producto (id_producto, tienda_id, titulo, descripcion, caption, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_producto) DO UPDATE SET
                titulo = EXCLUDED.titulo,
                descripcion = EXCLUDED.descripcion,
                image_path = EXCLUDED.image_path
            """
            
            self.cursor.execute(insert_product_sql, (
                product['id'],
                store_id,
                product['title'],
                product['description'],
                None,
                product['image_url']
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando producto {product['id']}: {e}")
            return False
    
    def generate_and_save_embeddings(self, product: Dict) -> bool:
        """Generar y guardar embeddings para un producto."""
        try:
            # Generar embeddings de texto
            title_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(product['title'])
            desc_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(product['description'])
            
            # Generar embedding de imagen
            image_embedding = None
            try:
                image = self.load_image_from_path(product['image_url'])
                if image:
                    image_emb_array = self.product_service.image_service._compute_image_embedding(image)
                    image_embedding = image_emb_array.flatten().tolist()
                    logger.info(f"Embedding de imagen generado para producto {product['id']}")
                else:
                    logger.warning(f"No se pudo cargar imagen para producto {product['id']}")
                    return False
            except Exception as e:
                logger.warning(f"Error generando embedding de imagen para producto {product['id']}: {e}")
                return False
            
            # Guardar embeddings en base de datos
            insert_embeddings_sql = """
            INSERT INTO embeddings (id_producto, embedding_titulo, embedding_descripcion, embedding_caption, embedding_imagen)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id_producto) DO UPDATE SET
                embedding_titulo = EXCLUDED.embedding_titulo,
                embedding_descripcion = EXCLUDED.embedding_descripcion,
                embedding_imagen = EXCLUDED.embedding_imagen
            """
            
            self.cursor.execute(insert_embeddings_sql, (
                product['id'],
                title_embedding,
                desc_embedding,
                None,
                image_embedding
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error generando embeddings para producto {product['id']}: {e}")
            return False
    
    def process_products(self):
        """Procesar todos los productos del JSON."""
        try:
            # Filtrar solo los campos necesarios
            filtered_products = []
            for product in PRODUCTS_JSON:
                filtered_product = {
                    'id': product['id'],
                    'title': product['title'],
                    'description': product['description'],
                    'image_url': product['image_url']
                }
                filtered_products.append(filtered_product)
            
            logger.info(f"Procesando {len(filtered_products)} productos del JSON")
            
            # Obtener tienda existente
            store_id = self.create_store()
            
            # Procesar cada producto
            successful_products = 0
            failed_products = 0
            
            for i, product in enumerate(filtered_products, 1):
                logger.info(f"Procesando producto {i}/{len(filtered_products)}: {product['title']}")
                
                try:
                    # Primero guardar el producto
                    if self.save_product(product, store_id):
                        # Luego generar y guardar embeddings
                        if self.generate_and_save_embeddings(product):
                            successful_products += 1
                            logger.info(f"Producto {product['id']} procesado exitosamente")
                        else:
                            failed_products += 1
                            logger.error(f"Error procesando embeddings para producto {product['id']}")
                    else:
                        failed_products += 1
                        logger.error(f"Error guardando producto {product['id']}")
                    
                    # Commit después de cada producto
                    self.conn.commit()
                    
                except Exception as e:
                    logger.error(f"Error procesando producto {product['id']}: {e}")
                    failed_products += 1
                    self.conn.rollback()
            
            logger.info(f"Procesamiento completado: {successful_products} exitosos, {failed_products} fallidos")
            
        except Exception as e:
            logger.error(f"Error en procesamiento de productos: {e}")
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
    importer = None
    
    try:
        logger.info("Iniciando importación de productos del JSON...")
        
        importer = JSONProductImporter()
        importer.process_products()
        
        logger.info("Importación completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en importación: {e}")
        sys.exit(1)
        
    finally:
        if importer:
            importer.close_connection()


if __name__ == "__main__":
    main()