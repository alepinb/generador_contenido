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

# Cargar variables del entorno
load_dotenv()

def generate_text(topic, audience, platform, tone, language, max_tokens):
    api_key = os.getenv("HF_TOKEN")
    
    try:
        client = InferenceClient(
            model="mistralai/Mistral-7B-v0.1", 
            token=api_key
        )

        # Crear el prompt
        prompt = (
            f"Escribe un {tone.lower()} post en {language} para {platform} dirigido a {audience}. "
            f"El tema es: {topic}. "
            "El contenido debe ser largo y completo."
        )

        # Estimación de tokens (1 palabra ≈ 1.33 tokens)
        prompt_tokens = len(prompt.split()) * 1.33

        # Ajustar max_new_tokens según la longitud del prompt
        remaining_tokens = max_tokens - int(prompt_tokens)  # Restamos los tokens del prompt
        if remaining_tokens < 0:
            st.warning("El prompt es demasiado largo para el número de tokens solicitado.")
            return None

        # Generar el contenido
        response = client.text_generation(prompt, max_new_tokens=remaining_tokens)
        
        # Devolver el texto generado
        generated_text = response  # Asumimos que la respuesta es un texto

        return generated_text

    except Exception as e:
        st.error(f"Error al generar contenido: {str(e)}")
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

# Selección del número de palabras (aproximadamente en tokens)
word_count = st.selectbox("Cantidad de palabras", [50, 100, 150, 200, 250])

# Convertir las palabras seleccionadas a tokens aproximados (1 palabra ≈ 1.33 tokens)
max_tokens = int(word_count * 1.33)

# Botón para generar el contenido
if st.button("Generar Contenido"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            result = generate_text(topic, audience, platform, tone, language, max_tokens)
            
        if result:
            st.success("Contenido generado:")
            st.write(result)
    else:
        st.warning("Por favor, completa todos los campos.")
