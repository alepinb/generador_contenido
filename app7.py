import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def generate_text(topic, audience, platform, tone, language, model):
    api_key = os.getenv("HF_TOKEN")
    
    try:
        # Configurar cliente para el modelo seleccionado
        client = InferenceClient(
            model=model, 
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

# Interfaz de Streamlit
st.title("Generador de Contenido con IA")

# Selección de modelo de generación de texto
model_choice = st.selectbox("Selecciona el modelo de generación de texto", [
    "mistralai/Mistral-7B-Instruct-v0.3", 
    "meta-llama/Llama-2-13b-chat-hf"
])

# Entradas de texto para el tema y la audiencia
topic = st.text_input("Tema del contenido")
audience = st.text_input("Audiencia objetivo")

# Selección de plataforma y tono
platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])

# Selección de idioma
language = st.selectbox("Selecciona el idioma", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])

# Entrada para el prompt de la imagen
image_prompt = st.text_area("Describe el prompt para la imagen", "Escribe aquí la descripción para buscar la imagen")

# Botón para generar el contenido y la imagen
if st.button("Generar Contenido e Imagen"):
    if topic and audience:
        with st.spinner('Generando contenido...'):
            # Generar texto
            result = generate_text(topic, audience, platform, tone, language, model_choice)
            
            if result:
                st.success("Contenido generado:")
                st.write(result)

                if image_prompt:
                    images = fetch_image_from_pixabay(image_prompt)
                    for img_url in images:
                        st.image(img_url, caption="Imagen obtenida de Pixabay")
                else:
                    st.warning("Por favor, ingresa un prompt para la imagen.")
    else:
        st.warning("Por favor, completa todos los campos.")
