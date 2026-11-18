from django.shortcuts import render
from ..services import FilaService

# =========================
# GERAR SENHA NORMAL
# =========================
def gerar_senha(request):
    senha = FilaService.emitir_senha(tipo="normal")
    return render(
        request,
        "totem/senha_gerada.html",
        {"senha": senha}
    )

# =========================
# GERAR SENHA PREFERENCIAL
# =========================
def gerar_senha_preferencial(request):
    senha = FilaService.emitir_senha(tipo="preferencial")
    return render(
        request,
        "totem/senha_gerada.html",
        {"senha": senha}
    )

def totem(request):
    return render(
        request,
        "totem/retirar.html",
        {
            "modo_totem": True
        }
    )
