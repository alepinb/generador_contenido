# Usa una imagen base oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos requeridos para la aplicación
COPY app21.py requirements.txt ./

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto utilizado por Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app21.py", "--server.port=8501", "--server.address=0.0.0.0"]
