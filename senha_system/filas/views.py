from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.db import transaction

from accounts.models import Guiche
from .models import Senha, ControleFila, Propaganda


# =========================
# GERAR SENHA NORMAL
# =========================
def gerar_senha(request):

    ultima = Senha.objects.filter(tipo="normal").order_by("-numero").first()
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

    ultima = Senha.objects.filter(tipo="preferencial").order_by("-numero").first()
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
@login_required
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
# CHAMAR PRÓXIMA SENHA (VERSÃO PROFISSIONAL)
# =========================
#@login_required
@require_POST
def chamar_proxima(request, guiche_id):

    guiche = get_object_or_404(Guiche, id=guiche_id)

    with transaction.atomic():

        # 🔒 TRAVA O CONTROLE GLOBAL
        controle = ControleFila.objects.select_for_update().first()

        if not controle:
            controle = ControleFila.objects.create(contador=0)

        # FINALIZA APENAS A SENHA DESSE GUICHÊ
        Senha.objects.filter(
            guiche=guiche,
            status="chamando"
        ).update(status="finalizado")

        # INCREMENTA CONTADOR GLOBAL
        controle.contador += 1
        controle.save()

        # DEFINE REGRA: 1 PREFERENCIAL + 2 NORMAIS
        if controle.contador % 3 == 1:
            tipo_prioritario = "preferencial"
        else:
            tipo_prioritario = "normal"

        # BUSCA SENHA COM LOCK
        senha = (
            Senha.objects.select_for_update()
            .filter(status="espera", tipo=tipo_prioritario)
            .order_by("criada_em")
            .first()
        )

        # FALLBACK (se não tiver do tipo esperado)
        if not senha:
            outro_tipo = "normal" if tipo_prioritario == "preferencial" else "preferencial"

            senha = (
                Senha.objects.select_for_update()
                .filter(status="espera", tipo=outro_tipo)
                .order_by("criada_em")
                .first()
            )

        # ATUALIZA SENHA
        if senha:
            senha.status = "chamando"
            senha.guiche = guiche
            senha.save()

    return redirect(f"/filas/guiche/{guiche_id}/")


# =========================
# TOTEM
# =========================
def totem(request):
    return render(request, "totem/retirar.html", {
        "modo_totem": True
    })


# =========================
# PAINEL TV
# =========================
#@login_required
def painel_tv(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-id").first()

    ultimas = Senha.objects.filter(
        status="finalizado"
    ).order_by("-id")[:10]

    fila = Senha.objects.filter(
        status="espera"
    ).order_by("criada_em")[:10]

    propagandas = list(
    Propaganda.objects.filter(ativa=True)
    .values_list('imagem', flat=True)
    )

    context = {
        "ultima": ultima,
        "ultimas": ultimas,
        "fila": fila,
        "propagandas": propagandas,
        "modo_tv": True
    }

    return render(request, "tv/painel_tv.html", context)

# =========================
# API PARA TV
# =========================
#@login_required
def painel_tv_data(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-id").first()

    ultimas = Senha.objects.filter(
        status="finalizado"
    ).order_by("-id")[:10]

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
@login_required
def painel_dados(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-id").first()

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