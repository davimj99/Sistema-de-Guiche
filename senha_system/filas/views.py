from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from accounts.models import Guiche
from .models import Senha


# =========================
# GERAR SENHA NORMAL
# =========================
def gerar_senha(request):

    ultima = Senha.objects.filter(tipo="normal").last()
    numero = 1 if not ultima else ultima.numero + 1

    senha = Senha.objects.create(
        numero=numero,
        prefixo="A",
        tipo="normal",
        status="espera"
    )

    return render(request, "totem/senha_gerada.html", {"senha": senha})


# =========================
# GERAR SENHA PREFERENCIAL
# =========================
def gerar_senha_preferencial(request):

    ultima = Senha.objects.filter(tipo="preferencial").last()
    numero = 1 if not ultima else ultima.numero + 1

    senha = Senha.objects.create(
        numero=numero,
        prefixo="P",
        tipo="preferencial",
        status="espera"
    )

    return render(request, "totem/senha_gerada.html", {"senha": senha})


# =========================
# TELA DO GUICHÊ
# =========================
def tela_guiche(request, guiche_id):

    guiche = get_object_or_404(Guiche, id=guiche_id)

    senha_atual = Senha.objects.filter(
        guiche=guiche,
        status="chamando"
    ).last()

    fila = Senha.objects.filter(
        status="espera"
    ).order_by("criada_em")[:5]

    context = {
        "guiche": guiche,
        "senha_atual": senha_atual,
        "fila": fila
    }

    return render(request, "filas/guiche.html", context)


# =========================
# CHAMAR PRÓXIMA SENHA
# =========================
@require_POST
def chamar_proxima(request, guiche_id):

    guiche = get_object_or_404(Guiche, id=guiche_id)

    # FINALIZA QUALQUER SENHA ATIVA NO SISTEMA
    Senha.objects.filter(
        status="chamando"
    ).update(status="finalizado")

    # prioridade preferencial
    senha = Senha.objects.filter(
        status="espera",
        tipo="preferencial"
    ).order_by("criada_em").first()

    # se não houver preferencial
    if not senha:
        senha = Senha.objects.filter(
            status="espera",
            tipo="normal"
        ).order_by("criada_em").first()

    if senha:
        senha.status = "chamando"
        senha.guiche = guiche
        senha.save()

    return redirect(f"/filas/guiche/{guiche_id}/")

# =========================
# TOTEM
# =========================
def totem(request):
    return render(request, "totem/retirar.html")


# =========================
# PAINEL TV
# =========================
def painel_tv(request):

    # SENHA ATUAL (CORRETO)
    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-id").first()

    # HISTÓRICO (CORRETO)
    ultimas = Senha.objects.filter(
        status="finalizado"
    ).order_by("-id")[:10]

    # FILA
    fila = Senha.objects.filter(
        status="espera"
    ).order_by("criada_em")[:10]

    context = {
        "ultima": ultima,   
        "ultimas": ultimas,
        "fila": fila
    }

    return render(request, "tv/painel_tv.html", context)

# =========================
# API PARA TV
# =========================
def painel_tv_data(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-criada_em").first()

    ultimas = Senha.objects.filter(
        status="chamando"
    ).order_by("-criada_em")[:10]

    fila = Senha.objects.filter(
        status="espera"
    ).order_by("criada_em")[:10]

    data = {

        "ultima": {
            "senha": f"{ultima.prefixo}{ultima.numero}",
            "guiche": ultima.guiche.nome if ultima.guiche else ""
        } if ultima else None,

        "ultimas": [
            {
                "senha": f"{s.prefixo}{s.numero}",
                "guiche": s.guiche.nome if s.guiche else ""
            }
            for s in ultimas
        ],

        "fila": [
            f"{s.prefixo}{s.numero}"
            for s in fila
        ]
    }

    return JsonResponse(data)


# =========================
# API PAINEL FUNCIONÁRIOS
# =========================
def painel_dados(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-criada_em").first()

    fila = Senha.objects.filter(
        status="espera"
    ).order_by("criada_em")[:10]

    data = {
        "senha": f"{ultima.prefixo}{ultima.numero}" if ultima else "",
        "guiche": ultima.guiche.nome if ultima and ultima.guiche else "",
        "fila": [
            f"{s.prefixo}{s.numero}" for s in fila
        ]
    }

    return JsonResponse(data)