from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from ..models import Senha, Propaganda, Historico


def painel_tv(request):
    ultima = (
        Senha.objects
        .filter(status="chamando")
        .order_by("-id")
        .first()
    )

    ultimas = (
        Senha.objects
        .filter(status="finalizado")
        .order_by("-id")[:10]
    )
    hoje = timezone.localdate()
    fila = (
        Senha.objects
        .filter(status="espera",
                criada_em__date=hoje)
        .order_by("criada_em", "id")[:10]
    )

    propagandas_db = Propaganda.objects.filter(ativa=True)

    propagandas = []

    for propaganda in propagandas_db:
        if propaganda.imagem:
            propagandas.append(propaganda.imagem.name)

        if propaganda.video:
            propagandas.append(propaganda.video.name)

    context = {
        "ultima": ultima,
        "ultimas": ultimas,
        "fila": fila,
        "propagandas": propagandas,
        "modo_tv": True
    }

    return render(request, "tv/painel_tv.html", context)

def painel_tv_data(request):

    ultima_chamada = (
        Historico.objects
        .filter(
            acao__in=[
                "chamando",
                "chamando_novamente"
            ]
        )
        .select_related(
            "senha",
            "guiche"
        )
        .order_by("-id")
        .first()
    )

    ultimas = (
        Historico.objects
        .filter(
            acao__in=[
                "chamando",
                "chamando_novamente"
            ]
        )
        .select_related(
            "senha",
            "guiche"
        )
        .order_by("-id")[:10]
    )
    hoje = timezone.localdate()
    fila = (
        Senha.objects
        .filter(status="espera", criada_em__date=hoje)
        .order_by(
            "criada_em",
            "id"
        )[:10]
    )

    data = {
        "ultima": {
            "senha": (
                f"{ultima_chamada.senha.prefixo}"
                f"{ultima_chamada.senha.numero}"
            ),

            "guiche": (
                ultima_chamada.guiche.nome
                if ultima_chamada.guiche
                else ""
            ),

            # MUITO IMPORTANTE
            "chamada_id": ultima_chamada.id,

            "acao": ultima_chamada.acao

        } if ultima_chamada else None,

        "ultimas": [
            {
                "senha": (
                    f"{historico.senha.prefixo}"
                    f"{historico.senha.numero}"
                ),

                "guiche": (
                    historico.guiche.nome
                    if historico.guiche
                    else ""
                ),

                "chamada_id": historico.id,

                "acao": historico.acao
            }

            for historico in ultimas
        ],

        "fila": [
            f"{senha.prefixo}{senha.numero}"
            for senha in fila
        ]
    }

    return JsonResponse(data)


# API PAINEL FUNCIONÁRIOS
@login_required
def painel_dados(request):
    ultima = (
        Historico.objects
        .filter(acao__in=["chamando", "chamando_novamente"])
        .select_related("senha", "guiche")
        .order_by("-id")
        .first()
    )
    hoje = timezone.localdate()
    fila = (
        Senha.objects
        .filter(status="espera", 
                criada_em__date=hoje)
        .order_by("criada_em", "id")[:10]
    )

    if not ultima:
        return JsonResponse({
            "status": "vazio",
            "fila": [f"{s.prefixo}{s.numero}" for s in fila]
        })

    return JsonResponse({
        "status": "sucesso",
        "dados": {
            "senha": f"{ultima.senha.prefixo}{ultima.senha.numero}",
            "guiche": ultima.guiche.nome if ultima.guiche else "",
            "tipo": ultima.senha.tipo,
            "chamada_id": ultima.id
        },
        "fila": [f"{s.prefixo}{s.numero}" for s in fila]
    })