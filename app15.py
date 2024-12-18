import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import datetime

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


import yfinance as yf

# Función para obtener valores de diferentes mercados financieros
def fetch_market_data():
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "Nasdaq": "^IXIC",
        "Nikkei 225": "^N225",
        "FTSE 100": "^FTSE",
        "DAX": "^GDAXI",
        "CAC 40": "^FCHI",
        "IBEX 35": "^IBEX"
    }

    market_data = []
    for name, ticker in indices.items():
        try:
            data = yf.Ticker(ticker)
            last_price = data.history(period="1d").iloc[-1]["Close"]  # Último valor de cierre
            market_data.append({"index": name, "price": round(last_price, 2)})
        except Exception as e:
            market_data.append({"index": name, "price": "Error"})
    
    return market_data



# Función para obtener noticias financieras desde el New York Times
def fetch_financial_news_nyt():
    NYT_API_KEY = os.getenv("NYT_API_KEY")  # Clave de API del NYT
    today = datetime.date.today().strftime('%Y-%m-%d')  # Fecha de hoy
    
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {
        "q": "finance OR economy OR business",  # Términos de búsqueda relacionados con finanzas
        "begin_date": today.replace("-", ""),  # Formato yyyyMMdd
        "api-key": NYT_API_KEY,  # API Key
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get("response", {}).get("docs", [])
        news_list = []

        for article in articles:
            news_item = {
                "title": article.get("headline", {}).get("main", "No Title"),
                "description": article.get("snippet", "No description available"),
                "url": article.get("web_url", "#"),
                "image_url": f"https://static01.nyt.com/{article.get('multimedia', [{}])[0].get('url', '')}",
                "date": article.get("pub_date", "No date available"),
            }
            news_list.append(news_item)
        
        return news_list
    else:
        st.error(f"Error al obtener las noticias del NYT: {response.status_code}")
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


# Mostrar noticias financieras con miniaturas y fecha desde NYT
st.markdown("### Noticias Financieras 📈")
# Mostrar valores de mercados financieros
st.markdown("### 📊 Valores de los Mercados Financieros")
with st.spinner("Obteniendo valores de los mercados..."):
    market_data = fetch_market_data()
    if market_data:
        for market in market_data:
            st.write(f"**{market['index']}:** {market['price']} USD")
    else:
        st.warning("No se pudieron obtener los valores de los mercados.")


if st.button("Mostrar Noticias Financieras"):
    with st.spinner("Obteniendo noticias financieras del NYT..."):
        financial_news = fetch_financial_news_nyt()
        if financial_news:
            for article in financial_news:
                st.subheader(article['title'])
                st.image(article['image_url'], width=100, use_container_width=False)
                st.write(article['description'])
                st.markdown(f"**Fecha de publicación:** {article['date']}")
                st.markdown(f"[Leer más]({article['url']})", unsafe_allow_html=True)
        else:
            st.warning("No se encontraron noticias financieras.")

with col2:
    st.image("logo.png", caption="Logo", use_container_width=True)

