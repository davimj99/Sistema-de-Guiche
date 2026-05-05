from django.urls import path
from .views import painel_dados

urlpatterns = [
    path('painel/dados/', painel_dados, name='painel_dados'),
]