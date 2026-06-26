from django.urls import path
from . import views

urlpatterns = [
    path('relatorio/', views.relatorio_atendimentos, name='relatorio_atendimentos'),
    path('relatorio/pdf/', views.gerar_pdf, name='gerar_pdf'),
]