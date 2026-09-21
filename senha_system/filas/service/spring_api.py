# import requests

# SPRING_API_URL = "http://10.20.0.7:8080"  # Replace with your Spring API URL

# def listar_filas():
#     response = requests.get(f"{SPRING_API_URL}/filas", timeout=5)

#     response.raise_for_status()  # Raise an exception for HTTP errors
#     return response.json()  # Return the JSON response from the Spring API

import requests

SPRING_API_URL = "http://localhost:8080"


def listar_guiches():
    response = requests.get(
        f"{SPRING_API_URL}/guiches",
        timeout=5
    )

    print("========== SPRING API ==========")
    print("URL:", response.url)
    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.text)
    print("================================")

    response.raise_for_status()

    return response.json()


def buscar_guiche(guiche_id):
    response = requests.get(
        f"{SPRING_API_URL}/guiches/{guiche_id}",
        timeout=5
    )

    response.raise_for_status()

    return response.json()
    response = requests.delete(
        f"{SPRING_API_URL}/guiches/{guiche_id}",
        timeout=5
    )

    response.raise_for_status()

    return True