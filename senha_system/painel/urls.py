from django.urls import path
from .views import painel_publico
from filas.views import painel_dados 

urlpatterns = [
    path("", painel_publico),
    path("dados/", painel_dados, name="painel_dados"),
]