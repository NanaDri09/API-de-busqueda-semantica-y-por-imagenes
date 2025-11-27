from pathlib import Path
import os
import requests
import time
import logging
import base64
from typing import Any, Dict, List, Tuple, Optional
from PIL import Image
import io
import torch
import numpy as np
from transformers import CLIPModel, CLIPProcessor, BlipProcessor, BlipForConditionalGeneration,  MarianMTModel, MarianTokenizer
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from typing import Union, List, Tuple
import faiss
import numpy as np
from data.productos_del_json_copy import PRODUCTS_JSON



logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self):
        # Load the pre-trained Sentence-BERT model
        self.model_encoder = SentenceTransformer('all-MiniLM-L12-v2')

        # model = SentenceTransformer("jinaai/jina-embeddings-v2-base-es", trust_remote_code=True)
        self.model_encoder.max_seq_length = 256

        # Cargar modelo y procesador: CLIP
        self.model_name = "openai/clip-vit-base-patch32"
        self.model = CLIPModel.from_pretrained(self.model_name)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Cargar modelo para traducir
        self.model_name_traduccion = "Helsinki-NLP/opus-mt-es-en"
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name_traduccion)
        self.traduccion_model = MarianMTModel.from_pretrained(self.model_name_traduccion)

        self.api_key_scenexplain = "ySCqYgHENRfnH2QRXFJ4:845b2faeb087f6e350f195f171a9f3554e275d26fc7dad8c4b90b29393a6e89b"

        # Api_keys de respuesto
        self.api_key_16 = "fGp22h2gtCdWFRguJ7sq:7cd5e12611ee4dd8690d8c1e288cbf58743c8a7d192c4f740973c3fcc1a71c30" # sin creditos
        self.api_key_17 = "BNGTGGi3SvZMbOkKbLfA:131a54cfc8d2dc775badf491f8cfd11a8c8c559d4149c0a27ec09919292c6051" # en uso
        self.api_key_18 = "eN3c481Y4t56G1z2aj4r:11616ab34aa108fe19d7f73ca00710764e7ebd47e275ae6264ab6e001f63ab74" # en uso
        self.api_key_19 = "fxMmnTT1vM9k9s6tbWLd:2da496d94ade9db85dc3268286943167945f8df94b790aab7eb88d723040cec8" # en uso
        self.api_key_20 = "NYRXuhfYY24Dy9MbWlKw:6e5275901d1cb508e2f1d3ee4890fab3a9f416aaf5c39963d82d1b07211e5f8d" # en uso
        self.api_key_21 = "fj7gkGjdR9RvxtB0pUy5:c31371680763b78196d20b77ead985b08861d048347decc90ca9b4163131ce31" # en uso
        self.api_key_22 = "tBwMipfL1qxyARnFluUn:08f0a24a3c63f299d72259e87bfa361b5acfe90cfa420e8b5077f19ca04a5190" # en uso
        self.api_key_23 = "WBBC89rlz8qhQf3fZSf9:5b359c397c82c5bc4277dcef5d76abd143101d928644ffc90540a6002aa565da" # en uso
        self.api_key_24 = "yWU1I9H3A3QIinQfwulL:eb37d34742e1d741d9d3f0c1dced8157aee69a6598b2cf5abc3a8ce963dec1f9" # en uso
        self.api_key_25 = "nlIZKTjzwElGsCjbpo8N:5a875370781999c3132ef8b1caeac535d949099e735af6c0cc8f8da246cb9059" # en uso
        self.api_key_26 = "EfS4e91bJxp1oDqgBiWX:347a0a97b30aa58fd8990b57c4544d7998b166355154a168ae1c8e5cad24bc05" # en uso
        self.api_key_27 = "ZXUIqdezndwunuADBdqB:4b9358113d8b583e8ed6a35b58a35cd617849e0ea17e9aaf739aba7865825d93" # en uso
        self.api_key_28 = "ZGn2PsW8tpmBY3rnGWYd:b1a98d1e1b016be0301579a25f44a82b97fa75b068fb16a4741d059bab0b9fc3" # en uso
        self.api_key_29 = "hGihAnRdMRY4kIi8dzl0:1a58e02238577f2572cd03a716debe4143c8b964b5e573b67a59228bfe313e12" # en uso
        self.api_key_30 = "lDgjN6YhbNfSmK19Od2V:4428c75aaa13cfe12c225ed16b841ac9bee34d2639653611e020d701be0cc892" # en uso
        self.api_key_31 = "tErPukQdG0AJ84nNP44g:a6debb088f9f42135cf71f09f8600e9acb57fc91a9a970c1b03b911faf368ddf" # en uso
        self.api_key_32 = "HkgUBQFdQgUgMFQp0sdr:072d8b301f58d8eed8249f5a9a8c596f51c4f2d5996abde7e93483d05a1109e1" # en uso
        self.api_key_33 = "ySCqYgHENRfnH2QRXFJ4:845b2faeb087f6e350f195f171a9f3554e275d26fc7dad8c4b90b29393a6e89b"

        # Parámetros para manejo de timeouts y reintentos
        self.TIMEOUT_BASE = 25  # Timeout inicial en segundos
        self.TIMEOUT_RETRY = 45  # Timeout para reintentos
        self.MAX_RETRIES = 4    # Número máximo de reintentos en caso de timeout o error de conexión



    def encoder_list(self, texts: List[str]):
        embeddings = self.model_encoder.encode(texts)
        return np.array(embeddings)

    def encoder(self, text):
        embeddings = self.model_encoder.encode([text])
        return np.array(embeddings)


    # Función para obtener embeddings de lista urls de imágenes
    def get_image_embeddings(self, image_paths):
        embeddings = []
        for image_path in tqdm(image_paths, desc="Procesando imágenes"): # Barra de progreso
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device) # Procesar la imagen
            with torch.no_grad():
                image_embedding = self.model.get_image_features(**inputs) # Obtener el embedding de la imagen
            image_embedding = image_embedding.cpu().numpy() # Mover a CPU y convertir a numpy
            embeddings.append(image_embedding) 
        return np.vstack(embeddings) # Apilar todos los embeddings en una matriz

    # Funcion para codificar una imagen, acepta la url tambien
    def _compute_image_embedding(self, image: Union[str, Image.Image]) -> np.ndarray:
        if isinstance(image, str):
            img = Image.open(image).convert("RGB")
        elif isinstance(image, Image.Image):
            img = image.convert("RGB")
        else:
            raise TypeError("image debe ser una ruta (str) o PIL.Image.Image")

        inputs = self.processor(images=img, return_tensors="pt").to(self.device)
        with torch.no_grad():
            emb = self.model.get_image_features(**inputs)
        emb = emb.cpu().numpy().astype("float32")
        return emb

    # codificar una lista con imagenes y url
    def get_list_embeddings(self, images: List[Union[str, Image.Image]]):

        embeddings = []

        for image in tqdm(images, desc="Procesando imágenes"):

            if isinstance(image, str):
                img = Image.open(image).convert("RGB")
            elif isinstance(image, Image.Image):
                img = image.convert("RGB")
            else:
                raise TypeError("Debe ser una ruta (str) o PIL.Image.Image")

            emb = self._compute_image_embedding(img)
            embeddings.append(emb)

        return np.vstack(embeddings)


    # funciones relacionadas con la descripción de imagenes con scenexplain
    def image_to_base64(self, image_path: str) -> str:
        """Convierte imagen local a base64 con formato data URI."""
        try:
            
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                    
            # Determinar el tipo MIME basado en la extensión
            extension = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(extension, 'image/jpeg')
            
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:{mime_type};base64,{image_b64}"
            
        except Exception as e:
            raise RuntimeError(f"Error procesando imagen {image_path}: {e}")


    def call_scenex_api(self, image: Union[str, Image.Image], api_key: str, algorithm: str = "jelly", language: str = "es", timeout: int = 0, retry_count: int = 0) -> Any:
        """
        Llama al endpoint oficial de SceneX con imagen local convertida a base64.

        """
        if timeout == 0:
            timeout: int = self.TIMEOUT_BASE

        url = "https://api.scenex.jina.ai/v1/describe"

        if isinstance(image, Image.Image):
        # Convertir PIL Image a data URI (base64)
            try:
                buf = io.BytesIO()
                # Guardar como PNG para preservar transparencia si existe
                image.save(buf, format="PNG")
                image_bytes = buf.getvalue()
                mime_type = "image/png"
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                image_data_uri = f"data:{mime_type};base64,{image_b64}"
            except Exception as e:
                logger.error(f"Error convirtiendo PIL Image a bytes: {e}")
        elif isinstance(image, str):
            # Convertir imagen local a base64
            image_data_uri = self.image_to_base64(image)
        else:
            raise TypeError("image debe ser una ruta (str) o PIL.Image.Image")

        # Payload optimizado para JELLY - descripciones concisas de productos
        payload = {
            "data": [
                {
                    "image": image_data_uri,
                    "algorithm": algorithm,
                    "languages": [language],
                    "features": {
                        "objects": True,
                        "colors": True,
                        "materials": True
                    },
                    "max_tokens": 120,
                    "prompt": "Describe solo el producto, características principales y color. Sé conciso y directo."
                }
            ]
        }

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        try:
            logger.info(f"Enviando la imagen con algoritmo {algorithm} (intento {retry_count + 1})")
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            
            if response.status_code == 200:

                return response.json()
            elif response.status_code == 400:
                error_text = response.text.lower()
                if "algorithm" in error_text and "not supported" in error_text:
                    raise RuntimeError(f"Algoritmo '{algorithm}' no soportado.")
                else:
                    raise RuntimeError(f"Error 400: {response.text}")
            elif response.status_code == 429:
                # Rate limiting - esperar y reintentar
                wait_time = 60  # Esperar 1 minuto
                logger.warning(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
                time.sleep(wait_time)
                raise RuntimeError("Rate limit - reintentando...")
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = str(error_json)
                except:
                    pass
                raise RuntimeError(f"SceneX API error {response.status_code}: {error_detail}")
                
        except requests.exceptions.Timeout:
            if retry_count < self.MAX_RETRIES:
                logger.warning(f"Timeout en intento {retry_count + 1}. Reintentando con timeout mayor...")
                # Reintentar con timeout más largo
                return self.call_scenex_api(image, api_key, algorithm, language, self.TIMEOUT_RETRY, retry_count + 1)
            else:
                raise RuntimeError(f"Timeout después de {self.MAX_RETRIES + 1} intentos")
        except requests.exceptions.ConnectionError:
            if retry_count < self.MAX_RETRIES:
                logger.warning(f"Error de conexión. Reintentando en 25 segundos...")
                time.sleep(20)
                return self.call_scenex_api(image, api_key, algorithm, language, timeout, retry_count + 1)
            else:
                raise RuntimeError("Error de conexión después de múltiples intentos")
        except Exception as e:
            raise RuntimeError(f"Error de conexión: {e}")

    def extract_caption(self, resp: Any) -> str:
        """Extrae texto descriptivo de la respuesta de SceneX."""
        if resp is None:
            return ""
            
        if isinstance(resp, str):
            return resp.strip()
        
        if isinstance(resp, dict):
            if ('result' in resp and isinstance(resp['result'], list) and 
                len(resp['result']) > 0 and isinstance(resp['result'][0], dict)):
                
                first_result = resp['result'][0]
                
                if 'output' in first_result and first_result['output']:
                    return first_result['output'].strip()
                
                if 'text' in first_result and first_result['text']:
                    return first_result['text'].strip()
                
                if 'error' in first_result:
                    error_msg = first_result['error'].get('message', 'Error desconocido')
                    logger.warning(f"Error en API: {error_msg}")
                    return ""
        
        return self.find_text_recursive(resp)


    def find_text_recursive(self, obj) -> str:
        """Busca texto descriptivo recursivamente."""
        if isinstance(obj, str) and len(obj) > 20 and not obj.startswith('{'):
            return obj.strip()
        
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['text', 'caption', 'description', 'output'] and isinstance(value, str) and value.strip():
                    return value.strip()
                result = self.find_text_recursive(value)
                if result:
                    return result
                    
        elif isinstance(obj, list) and obj:
            return self.find_text_recursive(obj[0])
        
        return ""

    def generar_descripciones_por_listas(
        self,
        lista_imagenes: List[str],
        lista_ids: List[str],
        api_key,
        algorithm: str = "jelly",
        language: str = "es",
        timeout: int = 0,
        delay: float = 2.0  # Aumentar delay entre peticiones
    ) -> List[Tuple[int, str, str]]:

        """
        Genera descripciones para una lista de imágenes y sus IDs correspondientes.
        """
        if timeout == 0:
            timeout: int = self.TIMEOUT_BASE


        if len(lista_imagenes) != len(lista_ids):
            raise ValueError(f"Las listas deben tener la misma longitud. Imágenes: {len(lista_imagenes)}, IDs: {len(lista_ids)}")
        
        resultados = []
        exitosas = 0
        fallos = 0
        descripciones_generadas = 0
        
        logger.info(f"Iniciando procesamiento de {len(lista_imagenes)} imágenes con algoritmo {algorithm.upper()}...")
        
        for i, (image_path, product_id) in enumerate(zip(lista_imagenes, lista_ids), start=1):
            if not Path(image_path).exists():
                logger.warning(f"[{i}/{len(lista_imagenes)}] Imagen no encontrada: {image_path}")
                resultados.append((product_id, image_path, ""))
                fallos += 1
                continue
            
            logger.info(f"[{i}/{len(lista_imagenes)}] Procesando {Path(image_path).name} (ID: {product_id}) con {algorithm.upper()}...")
            logger.info(f"Progreso global: {descripciones_generadas} descripciones generadas")
            
            try:
                response = self.call_scenex_api(image_path, api_key, algorithm, language, timeout)
                caption = self.extract_caption(response)
                
                if caption and "error" not in caption.lower():
                    resultados.append((product_id, image_path, caption))
                    exitosas += 1
                    descripciones_generadas += 1
                    logger.info(f"Descripción generada: {i})")
                else:
                    resultados.append((product_id, image_path, ""))
                    fallos += 1
                    logger.warning(f"No se generó descripción válida")
                    
            except Exception as e:
                resultados.append((product_id, image_path, ""))
                fallos += 1
                logger.error(f"Error: {e}")

            # Esperar entre peticiones (más tiempo para evitar rate limiting)
            if i < len(lista_imagenes):
                logger.info(f"Esperando {delay} segundos antes de la siguiente imagen...")
                time.sleep(delay)

        logger.info(f"Procesamiento completado: {exitosas} exitosas, {fallos} fallos")
        logger.info(f"Total descripciones generadas en esta sesión: {descripciones_generadas}")
        
        return resultados

    def chunk_list(self, lst, n):
        """Divide una lista en sublistas de tamaño n"""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    def generar_descripciones_simple(self, imagenes: List[str], ids: List[str], algorithm: str = "jelly") -> List[str]:
        resultados_simples = []
        batch_size = 8
        api_keys = [self.api_key_26, self.api_key_27, self.api_key_28, self.api_key_29]  # Lista de cuentas para rotar
        
        for batch_index, (img_batch, id_batch) in enumerate(zip(self.chunk_list(imagenes, batch_size), self.chunk_list(ids, batch_size))):
            # Cambiar cuenta cada batch
            api_key = api_keys[batch_index % len(api_keys)]
            
            resultados_completos = self.generar_descripciones_por_listas(img_batch, id_batch, api_key, algorithm)
            resultados_simples.extend([desc for (_, _, desc) in resultados_completos])
                
        return resultados_simples


    # Funcion para genrar una descripcion a partir de una imagen: Image
    def generar_descripcion_imagen(self, image: Union[str, Image.Image], algorithm: str = "jelly", language: str = "es") -> str:
        """Genera la descripción completa para un objeto PIL Image.

        Parámetros:
        - image: instancia de PIL.Image.Image o ruta

        Retorna la descripción completa (sin truncar). Devuelve cadena vacía en caso de error.
        """
        try:
                timeout = self.TIMEOUT_BASE
                response = self.call_scenex_api(image, self.api_key_scenexplain, algorithm, language, timeout)
                caption = self.extract_caption(response)
                
                if caption and "error" not in caption.lower():
                    logger.info(f"Descripción generada")
                else:
                    logger.warning(f"No se generó descripción válida")
        except Exception as e:
                logger.error(f"Error: {e}")

        return caption

    def generar_descripciones_from_images_and_ids(self, images: List[Image.Image], ids: List[str], api_key: Optional[str] = None, algorithm: str = "jelly", language: str = "es", timeout: int = 0, delay: float = 1.0) -> List[Tuple[int, str]]:
        """Genera descripciones para una lista de objetos PIL Image y devuelve lista de tuplas (id, caption).

        No trunca las descripciones. Si hay error con una imagen devuelve cadena vacía en su lugar.
        """
        if len(images) != len(ids):
            raise ValueError("Las listas de imágenes e ids deben tener la misma longitud")
        if api_key is None:
            api_key = self.api_key_scenexplain

        timeout = self.TIMEOUT_BASE
        resultados: List[Tuple[int, str]] = []
        for img, pid in zip(images, ids):
            cap = self.generar_descripcion_imagen(img, api_key=api_key, algorithm=algorithm, language=language, timeout=timeout)
            resultados.append((pid, cap))
            time.sleep(delay)

        return resultados

    # Función para traducir las descripciones
    def traducir_lista(self, descripciones):
        traducidas = []
        for des in descripciones:
            # Verificar que des sea un string válido
            if not isinstance(des, str) or not des.strip():
                traducidas.append("empty description")
                continue

            traducida = self.traducir_descripcion(des)
            traducidas.append(traducida)
                        
        return traducidas
     
    # Función para traducir las descripciones
    def traducir_descripcion(self, descripcion):
                
        # Asegurarse de que des sea una lista para el tokenizer
        des_lista = [descripcion.strip()]
        
        try:
            inputs = self.tokenizer(des_lista, return_tensors="pt", padding=True, truncation=True)
            traducida = self.traduccion_model.generate(**inputs)
            tgt_text = self.tokenizer.batch_decode(traducida, skip_special_tokens=True)
            
            # Extraer solo el texto traducido y limpiar - CORRECCIÓN PRINCIPAL
            texto_final = tgt_text[0].strip() if tgt_text else "translation failed"		
        except Exception as e:
            print(f"Error traduciendo '{descripcion}': {e}")
        
        return texto_final

    def get_product(self, product_id: str) -> Optional[dict]:
        """Return a copy of the product dict matching product_id, or None if not found."""
        id = int(product_id)
        for producto in PRODUCTS_JSON:
            if producto.get("id") == id:
                return producto.copy()
        return None
