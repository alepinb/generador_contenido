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

def fetch_stock_indices():
    indices = {
        "Dow Jones": "^DJI",
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "FTSE 100": "^FTSE",
        "DAX": "^GDAXI",
        "Nikkei 225": "^N225"
    }
    index_data = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")["Close"][-1]
            index_data[name] = price
        except Exception as e:
            index_data[name] = f"Error: {e}"
    return index_data

# Función para obtener artículos de arXiv
def fetch_arxiv_articles(query, max_results=3):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    response = requests.get(base_url + search_query)
    if response.status_code == 200:
        entries = response.text.split("<entry>")
        articles = []
        for entry in entries[1:]:
            title = entry.split("<title>")[1].split("</title>")[0]
            summary = entry.split("<summary>")[1].split("</summary>")[0]
            link = entry.split("<id>")[1].split("</id>")[0]
            articles.append({"title": title, "summary": summary, "link": link})
        return articles
    else:
        st.error(f"Error al obtener artículos de arXiv: {response.status_code}")
        return []

# Función para generar contenido científico divulgativo, pasando los resúmenes de los artículos como contexto
def generate_scientific_content_with_context(scientific_area, personalization_info):
    """
    Genera contenido divulgativo científico basado en artículos de arXiv.
    
    Args:
        scientific_area (str): Área científica de interés
        personalization_info (str): Información adicional para personalizar el contenido
    
    Returns:
        str: Contenido científico generado para divulgación
    """
    # Recuperar artículos sobre el área científica seleccionada
    articles = fetch_arxiv_articles(scientific_area, max_results=3)
    
    # Si no hay artículos, retornar un mensaje de error
    if not articles:
        st.warning("No se encontraron artículos relevantes en arXiv.")
        return None
    
    # Obtener los resúmenes de los artículos para usar como contexto
    article_summaries = "\n".join([
        f"Artículo: {article['title']}\nResumen: {article['summary']}" 
        for article in articles
    ])
    
    api_key = os.getenv("HF_TOKEN")
    try:
        client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=api_key)
        
        # Prompt más detallado que incluye los resúmenes de los artículos
        prompt = (
            f"Escribe un artículo de divulgación científica sobre {scientific_area} "
            f"en un lenguaje accesible para todo público. Debes incluir información de los siguientes artículos de investigación recientes:\n\n"
            f"{article_summaries}\n\n"
            f"Información adicional a considerar: {personalization_info}\n\n"
            "Estructura el texto de manera que sea comprensible, usa analogías si es necesario, "
            "y explica los conceptos técnicos de forma sencilla. El objetivo es que una persona sin formación científica pueda entender fácilmente el contenido."
        )
        
        max_tokens = 2500
        response = client.text_generation(prompt, max_new_tokens=max_tokens)
        return response
    except Exception as e:
        st.error(f"Error al generar contenido científico: {str(e)}")
        return None

# Configuración de la página
st.set_page_config(layout="wide")

# Layout principal: dos columnas
col1, col2 = st.columns([4, 1])

# Columna izquierda: logo y botones
with col2:
    # Cada botón actualiza el estado de la vista sin desaparecer
    if st.button("Generar Contenido"):
        st.session_state["current_view"] = "content"

    if st.button("Ver Noticias Financieras"):
        st.session_state["current_view"] = "news"

    if st.button("Mostrar Perfil de la Empresa"):
        st.session_state["current_view"] = "profile"

    if st.button("Ver Índices Bursátiles"):
        st.session_state["current_view"] = "indices"

    if st.button("Generar Contenido Científico Divulgativo"):
        st.session_state["current_view"] = "scientific_content"    

# Columna izquierda: contenido dinámico
with col1:
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = None

    # Verificar si el estado ya está actualizado y mostrar el contenido correspondiente
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

        if st.button("Generar Contenido Divulgativo"):
            if scientific_area:
                with st.spinner("Buscando artículos y generando contenido..."):
                    # Llamada a la nueva función modificada
                    result = generate_scientific_content_with_context(scientific_area, personalization_info)
                    
                    if result:
                        st.success("Contenido científico generado:")
                        st.write(result)
                        
                        # Mostrar los artículos originales de arXiv
                        st.markdown("#### Artículos de investigación consultados:")
                        articles = fetch_arxiv_articles(scientific_area, max_results=3)
                        for article in articles:
                            st.markdown(f"**{article['title']}**")
                            st.write(article['summary'])
                            st.write(f"[Enlace al artículo original]({article['link']})")
                    else:
                        st.warning("No se pudo generar el contenido científico.")
            else:
                st.warning("Por favor, ingrese un área científica de interés.")

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
                    st.write(f"**Precio Actual:** ${profile.get('price', 'N/A')}")
                    st.write(f"**Descripción:** {profile.get('description', 'Descripción no disponible')}")
                else:
                    st.warning("No se pudo obtener el perfil.")

    elif st.session_state["current_view"] == "indices":
        st.markdown("### Índices Bursátiles")
        with st.spinner("Obteniendo índices..."):
            index_data = fetch_stock_indices()
            for name, price in index_data.items():
                st.write(f"{name}: {price}")

    elif st.session_state["current_view"] == "scientific_content":
        st.markdown("### Generar Contenido Científico Divulgativo")
        scientific_area = st.text_input("Área científica de interés (ej: inteligencia artificial, física cuántica)")
        personalization_info = st.text_area("Información adicional o contexto específico (opcional)")
    
    

    else:
            st.markdown("## Brilliant generator 🚀")
            st.markdown("- Genere contenidos para su Blog, Twitter(X), LinkedIn e Instagram.")
            st.markdown("- Lea noticias financieras.")
            st.markdown("- Obtenga información financiera de la empresa de su preferencia.")
            st.markdown("- Consulte los índices bursátiles más importantes.")
            st.write("Seleccione una opción en el menú de la derecha para empezar.")