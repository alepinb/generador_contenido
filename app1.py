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

def generate_text(topic, audience, platform, tone):
    api_key = os.getenv("HF_TOKEN")
    
    try:
        client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3", 
            token=api_key
        )

        prompt = (
            f"Escribe un {tone.lower()} post para {platform} dirigido a {audience}. "
            f"El tema es: {topic}."
        )

        response = client.text_generation(prompt, max_new_tokens=1000)
        return response

    except Exception as e:
        st.error(f"Error al generar contenido: {str(e)}")
        return None

# Interfaz de Streamlit
st.title("Generador de Contenido con IA")

topic = st.text_input("Tema del contenido")
audience = st.text_input("Audiencia objetivo")
platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])

if st.button("Generar Contenido"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            result = generate_text(topic, audience, platform, tone)
            
        if result:
            st.success("Contenido generado:")
            st.write(result)
    else:
        st.warning("Por favor, completa todos los campos.")