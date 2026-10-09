from django.shortcuts import render
from django.utils import timezone

from ..models import Senha

# =========================
# GERAR SENHA NORMAL
# =========================
def gerar_senha(request):
    hoje = timezone.localdate()

    ultima = (
        Senha.objects
        .filter(tipo="normal",criada_em__date=hoje)
        .order_by("-numero")
        .first()
    )

    numero = 1 if not ultima else ultima.numero + 1
    senha = Senha.objects.create(
        numero=numero,
        prefixo="A",
        tipo="normal",
        status="espera"
    )

    return render(
        request,
        "totem/senha_gerada.html",
        {"senha": senha}
    )

# =========================
# GERAR SENHA PREFERENCIAL
# =========================
def gerar_senha_preferencial(request):
    hoje = timezone.localdate()

    ultima = (
        Senha.objects
        .filter(tipo="preferencial",criada_em__date=hoje)
        .order_by("-numero")
        .first()
    )

    numero = 1 if not ultima else ultima.numero + 1
    senha = Senha.objects.create(
        numero=numero,
        prefixo="P",
        tipo="preferencial",
        status="espera"
    )

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
