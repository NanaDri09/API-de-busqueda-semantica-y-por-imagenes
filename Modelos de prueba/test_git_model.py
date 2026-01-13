#!/usr/bin/env python3
"""
Script para probar el modelo GIT con la imagen 35.png
"""

import os
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch

def test_git_model():
    """Probar modelo GIT con imagen local."""
    
    # Configurar modelo GIT
    model_name = "microsoft/git-base-coco"
    print(f"Cargando modelo: {model_name}")
    
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
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
    
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values=inputs.pixel_values,
            max_length=50,
            num_beams=4
        )
    
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # Mostrar resultado
    print("\n" + "="*50)
    print("RESULTADO - Modelo GIT")
    print("="*50)
    print(f"Imagen: {image_path}")
    print(f"Descripción: {caption}")
    print("="*50)

if __name__ == "__main__":
    test_git_model()