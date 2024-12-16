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

def generate_text(topic, audience, platform, tone, language):
    api_key = os.getenv("HF_TOKEN")
    
    try:
        client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3", 
            token=api_key
        )

        # Ajustar el prompt para incluir el idioma
        prompt = (
            f"Escribe un {tone.lower()} post en {language} para {platform} dirigido a {audience}. "
            f"El tema es: {topic}."
        )

        # Generar el contenido
        response = client.text_generation(prompt, max_new_tokens=1000)
        return response

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

# Botón para generar el contenido
if st.button("Generar Contenido"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            result = generate_text(topic, audience, platform, tone, language)
            
        if result:
            st.success("Contenido generado:")
            st.write(result)
    else:
        st.warning("Por favor, completa todos los campos.")
