import streamlit as st
from content_generator.pipeline import generate_content
from dotenv import load_dotenv
import os
import torch

# Cargar variables del entorno
load_dotenv()

# Interfaz de usuario en Streamlit
st.title("Generador de Contenido con IA")

# Entradas del usuario
topic = st.text_input("Tema del contenido")
audience = st.text_input("Audiencia objetivo")
platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])

if st.button("Generar Contenido"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            try:
                # Llamada a la función de generación de contenido
                result = generate_content(topic, audience, platform, tone)
                if result:
                    st.success("Contenido generado:")
                    st.write(result)
            except Exception as e:
                st.error(f"Ocurrió un error al generar el contenido: {e}")
    else:
        st.warning("Por favor, completa todos los campos.")
