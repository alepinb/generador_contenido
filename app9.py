import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# Función para generar texto
def generate_text(topic, audience, platform, tone, language, model, personalization_info):
    api_key = os.getenv("HF_TOKEN")
    try:
        client = InferenceClient(model=model, token=api_key)
        personalization_text = f" La información adicional sobre la empresa o persona es: {personalization_info}." if personalization_info else ""
        prompt = (
            f"Escribe un {tone.lower()} post en {language} para {platform} dirigido a {audience}. "
            f"El tema es: {topic}.{personalization_text}"
        )
        max_tokens = 2000
        response = client.text_generation(prompt, max_new_tokens=max_tokens)
        if len(response) < 50:
            st.warning("El contenido generado es demasiado corto. Intenta aumentar el límite de tokens.")
        return response
    except Exception as e:
        st.error(f"Error al generar contenido: {str(e)}")
        return None

# Función para obtener imágenes de Pixabay
def fetch_image_from_pixabay(query):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page=3"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["hits"]:
            return [hit["webformatURL"] for hit in data["hits"]]
        else:
            st.warning("No se encontraron imágenes en Pixabay.")
    else:
        st.error("Error al conectar con Pixabay.")
    return []

# Configuración de ancho y estilos generales
st.set_page_config(layout="wide")  # Aprovechar ancho completo de la pantalla
st.markdown("""
    <style>
        .big-font {
            font-size: 24px !important;
        }
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select, 
        .stTextArea>div>textarea {
            font-size: 1.2em !important;  /* Tamaño de letra más grande en inputs */
        }
    </style>
    """, unsafe_allow_html=True)

# Layout con columnas
col1, col2 = st.columns([3, 1])  # 3 partes para formulario, 1 parte para logo

with col1:
    # Formulario y título a la izquierda
    st.markdown('<p class="big-font"><b>Generador de Contenido con IA</b></p>', unsafe_allow_html=True)

    # Selección de modelo de IA
    model_choice = st.selectbox("Selecciona el modelo de generación de texto", [
        "mistralai/Mistral-7B-Instruct-v0.3", 
        "meta-llama/Llama-2-13b-chat-hf"
    ])

    # Entradas de texto
    topic = st.text_input("Tema del contenido")
    audience = st.text_input("Audiencia objetivo")
    personalization_info = st.text_area("Información sobre la empresa o persona", 
                                        "Escribe aquí tu nombre o el nombre de la empresa a la cual pertences. Aparecerá al final del texto.")
    
    # Selecciones
    platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
    tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])
    language = st.selectbox("Selecciona el idioma", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])
    
    # Entrada para el prompt de la imagen
    image_prompt = st.text_area("Describe el prompt para la imagen", "Escribe aquí la descripción para buscar la imagen")
    
    # Botón para generar
    if st.button("Generar Contenido e Imagen"):
        if topic and audience:
            with st.spinner('Generando contenido...'):
                result = generate_text(topic, audience, platform, tone, language, model_choice, personalization_info)
                if result:
                    st.success("Contenido generado:")
                    st.write(result)
                    if image_prompt:
                        images = fetch_image_from_pixabay(image_prompt)
                        for img_url in images:
                            st.image(img_url, caption="Imagen obtenida de Pixabay", use_container_width=True)
                else:
                    st.warning("Por favor, completa todos los campos.")
        else:
            st.warning("Por favor, completa todos los campos.")

with col2:
    # Logo a la derecha
    st.image("logo.png", use_container_width=True)
