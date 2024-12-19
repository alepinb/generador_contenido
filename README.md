# Brilliant Generator ✨

Brilliant Generator es una aplicación interactiva desarrollada con Streamlit que combina generación de contenido, consulta de noticias financieras, datos bursátiles y creación de contenido científico divulgativo. Todo en una sola plataforma, fácil de usar y altamente funcional. 🚀

## Interfaz:

![brilliant_generator](https://github.com/user-attachments/assets/49581ab9-3189-4036-852c-d984933647fe)


## Características Principales 📌

### 1. Generación de Contenido

Cree publicaciones personalizadas para:
* **LinkedIn**
* **Twitter (X)**
* **Blogs**
* **Instagram**

Personalice el tono, idioma y audiencia.

### 2. Noticias Financieras 📰

* Acceda a las últimas noticias del mundo financiero
* Manténgase informado con las actualizaciones más relevantes

### 3. Perfil de Empresas 🏢

* Consulte información sobre cualquier empresa listada en bolsa
* Obtenga detalles como:
  * Nombre de la empresa
  * Precio actual
  * Descripción

### 4. Índices Bursátiles 📊

Visualice los valores de índices globales:
* **Dow Jones**
* **S&P 500**
* **Nasdaq**
* **FTSE 100**
* **DAX**
* **Nikkei 225**

### 5. Contenido Científico Divulgativo 🔬

* Genere contenido científico accesible para el público general
* Basado en los últimos artículos de **arXiv**
* Disponible en varios idiomas

## Configuración del Proyecto ⚙️

### Prerrequisitos

* Python 3.12 o superior
* Las siguientes librerías instaladas:

```bash
pip install streamlit requests yfinance huggingface_hub python-dotenv
```

### Clonar el Repositorio

```bash
git clone https://github.com/tu_usuario/brilliant-generator.git
cd brilliant-generator
```

### Configurar Variables de Entorno

Cree un archivo `.env` en la raíz del proyecto con las siguientes claves:

```env
PIXABAY_API_KEY=tu_pixabay_api_key
NEWSAPI_KEY=tu_newsapi_key
FMP_API_KEY=tu_fmp_api_key
HF_TOKEN=tu_huggingface_token
```

### Ejecutar la Aplicación

Inicie la aplicación con el siguiente comando:

```bash
streamlit run app.py
```

## Uso de la Aplicación 💻

1. Seleccione una opción en el menú de la derecha:
   * **Generar Contenido**: Configure tema, audiencia, tono, idioma y plataforma
   * **Ver Noticias Financieras**: Lea las últimas actualizaciones financieras
   * **Mostrar Perfil de la Empresa**: Introduzca el símbolo bursátil
   * **Ver Índices Bursátiles**: Consulte los principales índices
   * **Generar Contenido Científico Divulgativo**: Introduzca un área científica de interés

2. Presione los botones correspondientes para ejecutar la funcionalidad deseada

## Estructura del Proyecto 🗂️

```
brilliant-generator/
├── app.py             # Código principal de la aplicación
├── requirements.txt   # Dependencias del proyecto
├── .env.example       # Ejemplo de configuración de variables de entorno
└── README.md          # Documentación
```

## Contribuciones 🤝

¡Las contribuciones son bienvenidas! Si deseas mejorar este proyecto:

1. Haz un fork del repositorio
2. Crea una nueva rama
3. Envía un pull request con tus cambios

## Autora 📄

Alejandra Piñango

¡Gracias por usar Brilliant Generator! 🌟
