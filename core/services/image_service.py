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
from transformers import CLIPModel, CLIPProcessor, AutoProcessor, AutoModelForCausalLM, MarianMTModel, MarianTokenizer
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
        self.model_encoder.max_seq_length = 256

        # Cargar modelo y procesador: CLIP
        self.model_name = "openai/clip-vit-base-patch32"
        self.model = CLIPModel.from_pretrained(self.model_name)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Cargar Florence2 para descripciones
        self.florence_model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
        self.florence_processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
        self.florence_model.to(self.device)

        # Cargar modelo para traducir
        self.model_name_traduccion = "Helsinki-NLP/opus-mt-es-en"
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name_traduccion)
        self.traduccion_model = MarianMTModel.from_pretrained(self.model_name_traduccion)


    def encoder_list(self, texts: List[str]):
        embeddings = self.model_encoder.encode(texts)
        return np.array(embeddings)

    def encoder(self, text):
        embeddings = self.model_encoder.encode([text])
        return np.array(embeddings)

    # Función para obtener embeddings de lista urls de imágenes
    def get_image_embeddings(self, image_paths):
        embeddings = []
        for image_path in tqdm(image_paths, desc="Procesando imágenes"):
            if isinstance(image_path, str) and image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
            else:
                image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_embedding = self.model.get_image_features(**inputs)
            image_embedding = image_embedding.cpu().numpy()
            embeddings.append(image_embedding) 
        return np.vstack(embeddings)

    def _compute_image_embedding(self, image: Union[str, Image.Image]) -> np.ndarray:
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                response = requests.get(image, timeout=10)
                response.raise_for_status()
                img = Image.open(io.BytesIO(response.content)).convert("RGB")
            else:
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

    def get_list_embeddings(self, images: List[Union[str, Image.Image]]):
        embeddings = []
        for image in tqdm(images, desc="Procesando imágenes"):
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    response = requests.get(image, timeout=10)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                else:
                    img = Image.open(image).convert("RGB")
            elif isinstance(image, Image.Image):
                img = image.convert("RGB")
            else:
                raise TypeError("Debe ser una ruta (str) o PIL.Image.Image")

            emb = self._compute_image_embedding(img)
            embeddings.append(emb)

        return np.vstack(embeddings)

    def generar_descripcion_imagen(self, image: Union[str, Image.Image]) -> str:
        """Genera descripción usando Florence2."""
        try:
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    response = requests.get(image, timeout=10)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                else:
                    img = Image.open(image).convert("RGB")
            else:
                img = image.convert("RGB")
            
            prompt = "<MORE_DETAILED_CAPTION>"
            inputs = self.florence_processor(text=prompt, images=img, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                generated_ids = self.florence_model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3
                )
            
            generated_text = self.florence_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = self.florence_processor.post_process_generation(generated_text, task=prompt, image_size=(img.width, img.height))
            
            return parsed_answer.get("<MORE_DETAILED_CAPTION>", "")
            
        except Exception as e:
            logger.error(f"Error generando descripción: {e}")
            return ""

    def generar_descripciones_simple(self, imagenes: List[str], ids: List[str]) -> List[str]:
        """Genera descripciones usando Florence2 para lista de imágenes."""
        resultados = []
        
        for imagen in tqdm(imagenes, desc="Generando descripciones"):
            descripcion = self.generar_descripcion_imagen(imagen)
            resultados.append(descripcion)
            
        return resultados

    # Función para traducir las descripciones
    def traducir_lista(self, descripciones):
        traducidas = []
        for des in descripciones:
            if not isinstance(des, str) or not des.strip():
                traducidas.append("empty description")
                continue
            traducida = self.traducir_descripcion(des)
            traducidas.append(traducida)
        return traducidas
     
    def traducir_descripcion(self, descripcion):
        des_lista = [descripcion.strip()]
        try:
            inputs = self.tokenizer(des_lista, return_tensors="pt", padding=True, truncation=True)
            traducida = self.traduccion_model.generate(**inputs)
            tgt_text = self.tokenizer.batch_decode(traducida, skip_special_tokens=True)
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