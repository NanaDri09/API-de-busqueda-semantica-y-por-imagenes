#!/usr/bin/env python3
"""
Script de prueba para el modelo Florence-2 con imagen local.
"""

import os
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch

def test_florence2_model():
    """Probar modelo Florence-2 con imagen local."""
    
    # Configurar modelo Florence-2
    model_name = "microsoft/Florence-2-base"
    print(f"Cargando modelo: {model_name}")
    
    try:
        processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        
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
        
        # Generar descripción detallada
        print("Generando descripción detallada...")
        
        prompt = "<MORE_DETAILED_CAPTION>"
        inputs = processor(text=prompt, images=image, return_tensors="pt")
        
        with torch.no_grad():
            generated_ids = model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                num_beams=3
            )
        
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = processor.post_process_generation(generated_text, task="<MORE_DETAILED_CAPTION>", image_size=(image.width, image.height))
        
        # Mostrar resultado
        print("\n" + "="*50)
        print("RESULTADO - Modelo Florence-2")
        print("="*50)
        print(f"Imagen: {image_path}")
        print(f"Descripción detallada: {parsed_answer['<MORE_DETAILED_CAPTION>']}")
        print("="*50)
        
        # Probar caption simple también
        print("\nGenerando caption simple...")
        
        prompt_simple = "<CAPTION>"
        inputs_simple = processor(text=prompt_simple, images=image, return_tensors="pt")
        
        with torch.no_grad():
            generated_ids_simple = model.generate(
                input_ids=inputs_simple["input_ids"],
                pixel_values=inputs_simple["pixel_values"],
                max_new_tokens=1024,
                num_beams=3
            )
        
        generated_text_simple = processor.batch_decode(generated_ids_simple, skip_special_tokens=False)[0]
        parsed_answer_simple = processor.post_process_generation(generated_text_simple, task="<CAPTION>", image_size=(image.width, image.height))
        
        print(f"Caption simple: {parsed_answer_simple['<CAPTION>']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Nota: Florence-2 requiere trust_remote_code=True y puede necesitar dependencias adicionales")

if __name__ == "__main__":
    test_florence2_model()