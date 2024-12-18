import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import yfinance as yf

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")

# Funciones de utilidad
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

def fetch_financial_news():
    url = f'https://newsapi.org/v2/everything?q=finance&apiKey={NEWSAPI_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener noticias: {e}")
        return []

def fetch_company_profile(symbol):
    url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    else:
        st.error(f"Error al conectar con Financial Modeling Prep: {response.status_code}")
        return None

# Configuración de la página
st.set_page_config(layout="wide")

# Layout principal
col1, col2 = st.columns([1, 4])

# Columna izquierda: botones
with col1:
    st.image("logo.png", use_container_width=True)
    
    
    if st.button("Generar Contenido"):
        st.session_state["current_view"] = "content"
    
    if st.button("Ver Noticias Financieras"):
        st.session_state["current_view"] = "news"
    
    if st.button("Mostrar Perfil de la Empresa"):
        st.session_state["current_view"] = "profile"

# Columna derecha: contenido dinámico
with col2:
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = None

    if st.session_state["current_view"] == "content":
        st.markdown("### Generar Contenido")
        model_choice = st.selectbox("Selecciona el modelo", ["mistralai/Mistral-7B-Instruct-v0.3", "EleutherAI/pythia-1.4b"])
        topic = st.text_input("Tema del contenido")
        audience = st.text_input("Audiencia objetivo")
        platform = st.selectbox("Plataforma", ["LinkedIn", "Twitter", "Blog", "Instagram"])
        tone = st.selectbox("Tono", ["Formal", "Informal", "Técnico", "Inspirador"])
        language = st.selectbox("Idioma", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])
        personalization_info = st.text_area("Información adicional")
        image_prompt = st.text_area("Prompt para imagen")
        
        if st.button("Generar"):
            with st.spinner("Generando contenido..."):
                result = generate_text(topic, audience, platform, tone, language, model_choice, personalization_info)
                if result:
                    st.success("Contenido generado:")
                    st.write(result)
                    if image_prompt:
                        images = fetch_image_from_pixabay(image_prompt)
                        for img_url in images:
                            st.image(img_url, caption="Imagen generada", use_container_width=True)
                else:
                    st.warning("No se pudo generar contenido.")

    elif st.session_state["current_view"] == "news":
        st.markdown("### Noticias Financieras")
        with st.spinner("Obteniendo noticias..."):
            articles = fetch_financial_news()
            if articles:
                for article in articles[:5]:
                    st.subheader(article['title'])
                    st.write(article.get('description', ''))
                    st.write(f"[Leer más]({article['url']})")
            else:
                st.warning("No se encontraron noticias.")

    elif st.session_state["current_view"] == "profile":
        st.markdown("### Perfil de la Empresa")
        symbol = st.text_input("Símbolo de la empresa (Ej: AAPL)")
        
        if st.button("Mostrar Perfil"):
            with st.spinner("Obteniendo perfil de la empresa..."):
                profile = fetch_company_profile(symbol)
                if profile:
                    st.subheader(profile.get("companyName", "Nombre no disponible"))
                    st.image(profile.get("image", ""), width=100)
                    st.write(f"**Precio Actual:** ${profile.get('price', 'No disponible')}")
                    st.write(f"**Descripción:** {profile.get('description', 'No disponible')}")
                else:
                    st.warning("No se encontró información para la empresa.")

    else:
        st.markdown("## Brilliant generator 🚀")
        st.markdown("- Genere contenidos para su Blog, Twitter(X), Linkendin e Instagram.")
        st.markdown("- Lea noticias financieras.")
        st.markdown("- Obtenga información financiera de la empresa de su preferencia.")
        st.write("Seleccione una opción en el menú de la izquierda para empezar.")
