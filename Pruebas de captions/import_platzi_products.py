#!/usr/bin/env python3
"""
Script para importar productos de Platzi Fake Store API y procesarlos con embeddings.
Guarda los productos y embeddings en PostgreSQL (sin captions).
"""

import requests
import psycopg2
import os
import sys
from typing import List, Dict, Optional
from PIL import Image
import io
import time
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar servicios del proyecto
from core.services.product_service import ProductService    

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlatziProductImporter:
    """Clase para importar y procesar productos de Platzi Fake Store API."""
    
    def __init__(self):
        """Inicializar servicios y conexión a base de datos."""
        # Configuración de base de datos
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
        
        # Conexión a base de datos
        self.conn = None
        self.cursor = None
        self._connect_db()
        
        # Crear tablas si no existen
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
            # Crear tabla tienda
            create_tienda_sql = """
            CREATE TABLE IF NOT EXISTS tienda (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT
            );
            """
            
            # Crear tabla producto
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
            
            # Crear tabla embeddings
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
    
    def fetch_products_from_api(self) -> List[Dict]:
        """Obtener productos de Platzi Fake Store API con reintentos."""
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Obteniendo productos de Platzi API (intento {attempt})...")
                
                # Headers para evitar bloqueos
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Connection': 'keep-alive'
                }
                
                response = requests.get(
                    'https://api.escuelajs.co/api/v1/products',
                    headers=headers,
                    timeout=60,
                    verify=True
                )
                response.raise_for_status()
                
                platzi_products = response.json()
                logger.info(f"Obtenidos {len(platzi_products)} productos de Platzi")
                
                # Filtrar campos de Platzi
                filtered_products = []
                for product in platzi_products:
                    # Tomar solo la primera imagen del array
                    first_image = product.get('images', [''])[0] if product.get('images') else ''
                    
                    filtered_product = {
                        'id': f"pz_{product['id']}",
                        'title': product['title'],
                        'description': product['description'],
                        'image': first_image
                    }
                    filtered_products.append(filtered_product)
                
                return filtered_products
                
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    wait_time = 5 * attempt
                    logger.warning(f"Error de conexión (intento {attempt}): {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error de conexión después de {max_retries} intentos: {e}")
                    raise
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 3 * attempt
                    logger.warning(f"Error obteniendo productos (intento {attempt}): {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error obteniendo productos de Platzi después de {max_retries} intentos: {e}")
                    raise
    
    def download_image(self, image_url: str) -> Optional[Image.Image]:
        """Descargar imagen desde URL con manejo especial para Imgur."""
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                # Headers especiales para Imgur
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site'
                }
                
                # Espera más larga para Imgur
                if 'imgur.com' in image_url:
                    time.sleep(2 * attempt)  # Espera progresiva para Imgur
                
                response = requests.get(
                    image_url, 
                    headers=headers,
                    timeout=45,
                    stream=True
                )
                response.raise_for_status()

                # Convertir a PIL Image
                image = Image.open(io.BytesIO(response.content))
                return image

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limiting
                    wait_time = 10 * attempt  # Espera más larga para rate limiting
                    logger.info(f"Rate limit en imagen (intento {attempt}): {image_url}. Esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"HTTP Error {e.response.status_code} descargando imagen: {image_url}")
                    return None
            except Exception as e:
                if attempt < max_retries:
                    wait = 5 * attempt
                    logger.info(f"Intento {attempt} falló descargando imagen {image_url}: {e}. Reintentando en {wait}s")
                    time.sleep(wait)
                    continue
                else:
                    logger.warning(f"Error descargando imagen {image_url}: {e}")
                    return None
        
        return None
    
    def create_store(self) -> int:
        """Obtener ID de la tienda existente."""
        try:
            # Obtener la tienda existente
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
                None,  # caption vacío
                product['image']
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando producto {product['id']}: {e}")
            return False
    

    
    def process_products(self):
        """Procesar solo productos con imagen descargable: importar, generar embeddings y guardar."""
        try:
            # Obtener productos de la API
            products = self.fetch_products_from_api()
            
            # Obtener tienda existente
            store_id = self.create_store()
            
            # Procesar cada producto
            successful_products = 0
            failed_products = 0
            skipped_products = 0
            
            for i, product in enumerate(products, 1):
                logger.info(f"Procesando producto {i}/{len(products)}: {product['title']}")
                
                try:
                    # Primero intentar descargar la imagen
                    image = self.download_image(product['image'])
                    if not image:
                        logger.warning(f"Saltando producto {product['id']} - no se pudo descargar imagen")
                        skipped_products += 1
                        continue
                    
                    # Generar embedding de imagen
                    try:
                        image_emb_array = self.product_service.image_service._compute_image_embedding(image)
                        image_embedding = image_emb_array.flatten().tolist()
                        logger.info(f"Embedding de imagen generado para producto {product['id']}")
                    except Exception as e:
                        logger.warning(f"Saltando producto {product['id']} - error generando embedding de imagen: {e}")
                        skipped_products += 1
                        continue
                    
                    # Generar embeddings de texto
                    title_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(product['title'])
                    desc_embedding = self.product_service.vector_repo.embedding_service.generate_embedding(product['description'])
                    
                    # Guardar producto
                    if self.save_product(product, store_id):
                        # Guardar embeddings
                        if self.save_embeddings(product['id'], title_embedding, desc_embedding, image_embedding):
                            successful_products += 1
                            logger.info(f"Producto {product['id']} procesado exitosamente")
                        else:
                            failed_products += 1
                            logger.error(f"Error guardando embeddings para producto {product['id']}")
                    else:
                        failed_products += 1
                        logger.error(f"Error guardando producto {product['id']}")
                    
                    # Commit después de cada producto exitoso
                    self.conn.commit()
                    
                except Exception as e:
                    logger.error(f"Error procesando producto {product['id']}: {e}")
                    failed_products += 1
                    self.conn.rollback()
            
            logger.info(f"Procesamiento completado: {successful_products} exitosos, {failed_products} fallidos, {skipped_products} saltados")
            
        except Exception as e:
            logger.error(f"Error en procesamiento de productos: {e}")
            raise
    
    def save_embeddings(self, product_id: str, title_embedding: list, desc_embedding: list, image_embedding: list) -> bool:
        """Guardar embeddings en base de datos."""
        try:
            insert_embeddings_sql = """
            INSERT INTO embeddings (id_producto, embedding_titulo, embedding_descripcion, embedding_caption, embedding_imagen)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id_producto) DO UPDATE SET
                embedding_titulo = EXCLUDED.embedding_titulo,
                embedding_descripcion = EXCLUDED.embedding_descripcion,
                embedding_imagen = EXCLUDED.embedding_imagen
            """
            
            self.cursor.execute(insert_embeddings_sql, (
                product_id,
                title_embedding,
                desc_embedding,
                None,  # embedding_caption vacío
                image_embedding
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando embeddings para producto {product_id}: {e}")
            return False
    
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
        logger.info("Iniciando importación de productos Platzi...")
        
        # Crear instancia del importador
        importer = PlatziProductImporter()
        
        # Procesar productos
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