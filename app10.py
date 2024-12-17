import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
YAHOO_FINANCE_API_KEY = os.getenv("YAHOO_FINANCE_API_KEY")

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

# Función para obtener noticias financieras desde Yahoo Finance
def fetch_financial_news():
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed"
    headers = {
        'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com',
        'x-rapidapi-key': YAHOO_FINANCE_API_KEY
    }
    params = {"category": "generalnews", "region": "US"}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            st.write("Respuesta completa de la API:", data)  # Imprime la respuesta completa para depuración
            # Verificar si 'items' existe y es una lista
            if 'items' in data and isinstance(data['items'], list):
                return data['items']  # Retorna la lista de noticias
            else:
                st.warning("La respuesta no contiene noticias financieras o el formato es incorrecto.")
        elif response.status_code == 403:
            st.error("Error 403: No tienes permisos para acceder a esta API. Revisa tu suscripción en RapidAPI.")
        else:
            st.error(f"Error al obtener noticias financieras: Código {response.status_code}")
    except Exception as e:
        st.error(f"Error al conectar con la API de Yahoo Finance: {e}")
    
    return []  # Retorna una lista vacía si no hay noticias o hay un error




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

# Layout principal con columnas
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<p class="big-font"><b>Generador de Contenido con IA</b></p>', unsafe_allow_html=True)
    
    # Sección de generación de contenido
    model_choice = st.selectbox("Selecciona el modelo de generación de texto", [
        "mistralai/Mistral-7B-Instruct-v0.3", 
        "meta-llama/Llama-2-13b-chat-hf"
    ])
    topic = st.text_input("Tema del contenido")
    audience = st.text_input("Audiencia objetivo")
    personalization_info = st.text_area("Información adicional", "")
    platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
    tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])
    language = st.selectbox("Idioma", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])
    image_prompt = st.text_area("Prompt para imagen", "")

    if st.button("Generar Contenido e Imagen"):
        if topic and audience:
            with st.spinner("Generando contenido..."):
                result = generate_text(topic, audience, platform, tone, language, model_choice, personalization_info)
                if result:
                    st.success("Contenido generado:")
                    st.write(result)
                    if image_prompt:
                        images = fetch_image_from_pixabay(image_prompt)
                        for img_url in images:
                            st.image(img_url, caption="Imagen obtenida de Pixabay", use_container_width=True)
                else:
                    st.warning("No se pudo generar contenido.")
        else:
            st.warning("Por favor, completa todos los campos.")

    # Botón independiente para mostrar noticias financieras
    st.markdown("### Noticias Financieras 📈")
    if st.button("Mostrar Noticias Financieras"):
        with st.spinner("Obteniendo noticias financieras..."):
            financial_news = fetch_financial_news()
            if financial_news:
                for i, news_item in enumerate(financial_news[:5]):
                    title = news_item.get("title", "Título no disponible")
                    link = news_item.get("link", "#")
                    st.write(f"**{i+1}. {title}**")
                    st.markdown(f"[Leer más]({link})", unsafe_allow_html=True)
            else:
                st.warning("No se encontraron noticias financieras.")

with col2:
    st.image("logo.png", caption="Logo", use_container_width=True)