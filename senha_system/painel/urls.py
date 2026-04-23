from django.urls import path
from .views import painel_publico, painel_dados

urlpatterns = [
    path("", painel_publico),
    path("dados/", painel_dados),
]