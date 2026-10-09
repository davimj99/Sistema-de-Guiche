from django.http import JsonResponse
from ..service.spring_api import listar_guiches, listar_filas


def testar_filas_spring(request):
    filas = listar_filas()
    return JsonResponse({"filas": filas})


def testar_guiches_spring(request):
    guiches = listar_guiches()
    return JsonResponse({"guiches": guiches})