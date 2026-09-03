import requests

SPRING_API_URL = "http://10.20.0.7:8080"  # Replace with your Spring API URL

def listar_filas():
    response = requests.get(f"{SPRING_API_URL}/filas", timeout=5)

    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()  # Return the JSON response from the Spring API