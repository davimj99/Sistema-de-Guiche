from django.urls import path
from .views.totem import gerar_senha, gerar_senha_preferencial, totem
from .views.guiche import tela_guiche, chamar_proxima, chamar_novamente
from .views.painel import painel_tv, painel_tv_data
#painel_dados
from .views.spring import testar_guiches_spring, testar_filas_spring
from .views import chatbot_api


urlpatterns = [
    # Totem
    path("gerar/", gerar_senha),
    path("preferencial/", gerar_senha_preferencial, name="senha_preferencial"),
    path("totem/", totem),

    # Guichê
    path("guiche/<int:guiche_id>/", tela_guiche),
    path("chamar/<int:guiche_id>/", chamar_proxima),
    path("chamar-novamente/<int:guiche_id>/", chamar_novamente),

    # Painel TV
    path("tv/", painel_tv, name="painel_tv"),
    path("tv/data/", painel_tv_data, name="tv_data"),

    # Painel funcionários
    # path("painel/dados/", painel_dados),

    # Spring API
    path("testar/filas/spring/", testar_filas_spring, name="testar_filas_spring"),
    path("testar/guiches/spring/", testar_guiches_spring, name="testar_guiches_spring"),path("testar/guiches/spring/", testar_guiches_spring, name="testar_guiches_spring"),

    # Chatbot
    path("chatbot/", chatbot_api, name="chatbot_api"),
]