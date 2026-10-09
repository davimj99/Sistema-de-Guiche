from django.urls import path

from .views.aluno import (
    solicitar_wifi,
    minhas_solicitacoes,
    detalhes_solicitacao,
)


app_name = 'wifi'


urlpatterns = [

    path('solicitar/',solicitar_wifi,name='solicitar'),
    path('solicitacao/<str:protocolo>/',detalhes_solicitacao,name='detalhes'),
    path('minhas-solicitacoes/',minhas_solicitacoes,name='minhas_solicitacoes'),
]