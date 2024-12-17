import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

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

# Función para obtener noticias financieras desde The Guardian
def fetch_financial_news():
    url = 'https://content.guardianapis.com/search'
    params = {
        'q': 'finances',  # Filtro por el tema de finanzas
        'api-key': GUARDIAN_API_KEY,  # Tu clave de API
        'page-size': 10,  # Número de artículos que deseas obtener
        'format': 'json',  # Formato de la respuesta
        'show-fields': 'headline,trailText,thumbnail',  # Mostrar solo los campos necesarios
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        articles = data['response']['results']
        news_list = []
        
        for article in articles:
            news_item = {
                'title': article['fields']['headline'],
                'description': article.get('fields', {}).get('trailText', 'No description available'),
                'url': article['webUrl'],  # Enlace al artículo en The Guardian
                'image_url': article.get('fields', {}).get('thumbnail', 'https://via.placeholder.com/150')
            }
            news_list.append(news_item)
        
        return news_list
    else:
        st.error(f"Error al obtener las noticias: {response.status_code}")
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
    # Mostrar noticias financieras con la imagen ajustada al contenedor
# Mostrar noticias financieras con miniaturas
st.markdown("### Noticias Financieras 📈")
if st.button("Mostrar Noticias Financieras"):
    with st.spinner("Obteniendo noticias financieras..."):
        financial_news = fetch_financial_news()
        if financial_news:
            for article in financial_news:
                st.subheader(article['title'])
                # Mostrar la imagen como miniatura
                st.image(article['image_url'], width=100, use_container_width=False)  # Tamaño ajustado
                st.write(article['description'])
                st.markdown(f"[Leer más]({article['url']})", unsafe_allow_html=True)
        else:
            st.warning("No se encontraron noticias financieras.")

with col2:
    st.image("logo.png", caption="Logo", use_container_width=True)
