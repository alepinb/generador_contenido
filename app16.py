import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import datetime
import yfinance as yf

# Cargar variables del entorno
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

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

# Función para obtener noticias financieras
def fetch_financial_news():
    # Endpoint de NewsAPI con la palabra clave 'finance'
    url = f'https://newsapi.org/v2/everything?q=finance&apiKey={NEWSAPI_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa

        data = response.json()

        # Si la respuesta tiene artículos, devolverlos
        if 'articles' in data:
            return data['articles']
        else:
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener noticias: {e}")
        return []

# Función para obtener perfiles de empresas
def fetch_company_profile(symbol):
    FMP_API_KEY = os.getenv("FMP_API_KEY")  # Tu clave API de FMP
    url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]  # Retorna el perfil de la empresa (primer elemento)
        else:
            st.warning("No se encontró información para el símbolo ingresado.")
            return None
    else:
        st.error(f"Error al conectar con Financial Modeling Prep: {response.status_code}")
        return None


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
        "EleutherAI/gpt-neo-125M"
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
    st.markdown("### 📊 Valores de los Mercados Financieros")
    with st.spinner("Obteniendo valores de los mercados..."):
        market_data = fetch_market_data()
        if market_data:
            for market in market_data:
                st.write(f"**{market['index']}:** {market['price']} USD")
        else:
            st.warning("No se pudieron obtener los valores de los mercados.")

    # Botón para mostrar noticias financieras
    if st.button("Ver Noticias Financieras"):
        with st.spinner("Obteniendo noticias financieras..."):
            financial_news = fetch_financial_news()
            if financial_news:
                for article in financial_news[:10]:  # Mostrar solo las primeras 10 noticias
                    st.subheader(article['title'])
                    st.write(article['description'])
                    st.write(f"[Leer más]({article['url']})")
                    st.write(f"Publicado el: {article['publishedAt']}")
            else:
                st.warning("No se encontraron noticias.")

    # Buscar información de la compañía
    st.markdown("### 🏢 Información de la Empresa")
    company_symbol = st.text_input("Ingresa el símbolo de la empresa (Ejemplo: AAPL para Apple)", value="AAPL")

    if st.button("Mostrar Perfil de la Empresa"):
        with st.spinner("Obteniendo perfil de la empresa..."):
            company_profile = fetch_company_profile(company_symbol)
            if company_profile:
                st.subheader(company_profile.get("companyName", "Nombre no disponible"))
                st.image(company_profile.get("image", ""), width=100, caption="Logo de la Empresa")
                st.write(f"**Precio Actual:** ${company_profile.get('price', 'No disponible')}")
                st.write(f"**Capitalización de Mercado:** ${company_profile.get('mktCap', 'No disponible'):,}")
                st.write(f"**Beta:** {company_profile.get('beta', 'No disponible')}")
                st.write(f"**Descripción:** {company_profile.get('description', 'No disponible')}")
                st.write(f"**Sector:** {company_profile.get('sector', 'No disponible')}")
                st.write(f"**Industria:** {company_profile.get('industry', 'No disponible')}")
                st.write(f"**Sede Principal:** {company_profile.get('city', 'No disponible')}, {company_profile.get('country', 'No disponible')}")
                st.markdown(f"[Página Web de la Empresa]({company_profile.get('website', '#')})")
            else:
                st.warning("No se pudo obtener el perfil de la empresa.")

with col2:
    st.image("logo.png", use_container_width=True)
