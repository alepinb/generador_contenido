import requests

# Configurar URL y cabeceras
url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed"
headers = {
    'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com',
    'x-rapidapi-key': "8c99ef05aamsh3e1f343a86740cep19267cjsn4ba43a3bdcdd"  # Tu clave API aquí
}
params = {"category": "generalnews", "region": "US"}

# Hacer la solicitud a la API
try:
    response = requests.get(url, headers=headers, params=params)
    print("Código de respuesta:", response.status_code)  # Mostrar código de respuesta
    print("Contenido de la respuesta:")
    print(response.text)  # Mostrar el contenido completo de la respuesta JSON
except Exception as e:
    print("Error al conectar con la API:", e)

