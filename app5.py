import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Intentar importar torch de manera segura
try:
    import torch
except ImportError:
    st.warning("PyTorch no está instalado correctamente.")

from huggingface_hub import InferenceClient
from diffusers import StableDiffusionPipeline  # Usar diffusers en lugar de transformers

# Cargar variables del entorno
load_dotenv()

def generate_text(topic, audience, platform, tone, language):
    api_key = os.getenv("HF_TOKEN")
    
    try:
        client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3", 
            token=api_key
        )

        # Ajustar el prompt según la plataforma seleccionada
        if platform == "LinkedIn":
            prompt = (
                f"Escribe un {tone.lower()} post en {language} para LinkedIn dirigido a {audience}. "
                f"El tema es: {topic}. El contenido debe ser profesional, informativo y adecuado para una audiencia de LinkedIn."
            )
        elif platform == "Twitter":
            prompt = (
                f"Escribe un {tone.lower()} tweet en {language} para Twitter dirigido a {audience}. "
                f"El tema es: {topic}. El contenido debe ser breve y atractivo, adaptado a los 280 caracteres de Twitter."
            )
        elif platform == "Blog":
            prompt = (
                f"Escribe un {tone.lower()} artículo en {language} para un blog dirigido a {audience}. "
                f"El tema es: {topic}. El contenido debe ser detallado, con un enfoque educativo y profesional."
            )
        elif platform == "Instagram":
            prompt = (
                f"Escribe un {tone.lower()} post en {language} para Instagram dirigido a {audience}. "
                f"El tema es: {topic}. El contenido debe ser visual, creativo y adaptado al formato de Instagram, con un enfoque más informal."
            )
        else:
            prompt = (
                f"Escribe un {tone.lower()} post en {language} para {platform} dirigido a {audience}. "
                f"El tema es: {topic}."
            )

        # Aumentar el límite de tokens para mayor longitud de contenido
        max_tokens = 2000  # Puedes ajustar este valor según el modelo y los límites permitidos
        
        # Generar el contenido
        response = client.text_generation(prompt, max_new_tokens=max_tokens)
        
        # Verificar si el texto generado es demasiado corto o si hubo un corte
        if len(response) < 50:  # Umbral de texto corto
            st.warning("El contenido generado es demasiado corto. Intenta aumentar el límite de tokens.")
        
        return response

    except Exception as e:
        st.error(f"Error al generar contenido: {str(e)}")
        return None

def generate_image_from_text(prompt):
    """Genera una imagen usando el modelo Stable Diffusion de Hugging Face."""
    try:
        # Usar el pipeline de Stable Diffusion para generar la imagen
        model = StableDiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-1",  # Modelo de Stable Diffusion
            # Eliminar el dtype=torch.float16 para que use float32 por defecto
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Generar la imagen con tamaño 256x256
        image = model(prompt, height=256, width=256).images[0]
        
        return image

    except Exception as e:
        st.error(f"Error al generar la imagen: {str(e)}")
        return None

# Interfaz de Streamlit
st.title("Generador de Contenido con IA")

# Entradas de texto para el tema y la audiencia
topic = st.text_input("Tema del contenido")
audience = st.text_input("Audiencia objetivo")

# Selección de plataforma y tono
platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])

# Selección de idioma
language = st.selectbox("Selecciona el idioma", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])

# Botón para generar el contenido y la imagen
if st.button("Generar Contenido e Imagen"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            # Generar texto
            result = generate_text(topic, audience, platform, tone, language)
            
            if result:
                st.success("Contenido generado:")
                st.write(result)

                # Generar imagen asociada al tema
                image_prompt = f"Imagen creativa relacionada con el tema '{topic}' para la plataforma {platform}, en un estilo {tone.lower()}, para una audiencia {audience}."
                image = generate_image_from_text(image_prompt)

                if image:
                    st.image(image, caption="Imagen generada por Stable Diffusion", use_column_width=True)
    else:
        st.warning("Por favor, completa todos los campos.")