from django.urls import path
from .views import chamar_novamente, gerar_senha, tela_guiche, chamar_proxima, totem, painel_tv, painel_tv_data, gerar_senha_preferencial,painel_dados, testar_filas_spring

urlpatterns = [
    path("gerar/", gerar_senha),
    path("guiche/<int:guiche_id>/", tela_guiche),
    path("chamar/<int:guiche_id>/", chamar_proxima),
    path("totem/", totem),
    path("tv/", painel_tv, name="painel_tv"),
    path("tv/data/", painel_tv_data, name="tv_data"),
    #path("painel/dados/", painel_dados),
    path("chamar-novamente/<int:guiche_id>/",chamar_novamente),
    path("preferencial/", gerar_senha_preferencial, name="senha_preferencial"),
    path("testar/filas/spring/", testar_filas_spring, name="testar_filas_spring")
]