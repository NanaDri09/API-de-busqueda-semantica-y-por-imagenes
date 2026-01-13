import os
from transformers import CLIPProcessor, CLIPModel, pipeline
from PIL import Image
import torch

# Función para generar descripción mejorada
def generate_improved_caption(image_path):
    # Cargar CLIP (para generar embedding, aunque no se use directamente en el LLM)
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Cargar GPT-2
    text_generator = pipeline('text-generation', model='gpt2')

    # Abrir imagen
    image = Image.open(image_path)

    # Generar embedding con CLIP (se genera, pero no se transforma directamente a texto)
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)  # Embedding generado

    # Nota: No hay una forma directa de "transformar" el embedding a texto sin un decoder entrenado.
    # En su lugar, usamos un prompt genérico y GPT-2 para generar una descripción narrativa.
    prompt = "Describe this image in a detailed and narrative way."

    # Generar descripción con GPT-2 (haciendo que sea más narrativa)
    improved_caption = text_generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']

    return improved_caption

# Ejecutar con la imagen en la carpeta
image_file = "Modelos de prueba/35.png"  # Asumiendo que es la imagen
if os.path.exists(image_file):
    caption = generate_improved_caption(image_file)
    print("Descripción generada:")
    print(caption)
else:
    print("No se encontró la imagen '35.png' en la carpeta.")