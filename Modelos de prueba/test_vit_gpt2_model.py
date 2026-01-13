#!/usr/bin/env python3
"""
Script para probar el modelo ViT-GPT2 con la imagen 35.png
"""

import os
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch

def test_vit_gpt2_model():
    """Probar modelo ViT-GPT2 con imagen local."""
    
    # Configurar modelo ViT-GPT2
    model_name = "nlpconnect/vit-gpt2-image-captioning"
    print(f"Cargando modelo: {model_name}")
    
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    device = torch.device("cpu")
    model.to(device)
    model.eval()
    
    print(f"Modelo cargado en: {device}")
    
    # Cargar imagen
    image_path = "Modelos de prueba/35.png"
    
    if not os.path.exists(image_path):
        print(f"Error: No se encontró la imagen {image_path}")
        return
    
    print(f"Cargando imagen: {image_path}")
    image = Image.open(image_path)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Generar descripción
    print("Generando descripción...")
    
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    
    with torch.no_grad():
        output_ids = model.generate(
            pixel_values,
            max_length=50,
            num_beams=4,
            return_dict_in_generate=True
        ).sequences
    
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    # Mostrar resultado
    print("\n" + "="*50)
    print("RESULTADO - Modelo ViT-GPT2")
    print("="*50)
    print(f"Imagen: {image_path}")
    print(f"Descripción: {caption}")
    print("="*50)

if __name__ == "__main__":
    test_vit_gpt2_model()