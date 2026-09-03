from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from accounts.models import Guiche
from .models import Senha,ControleFila,Propaganda,Historico
from .service.spring_api import listar_filas


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


# =========================
# TELA DO GUICHÊ
# =========================
# @login_required
def tela_guiche(request, guiche_id):
    guiche = get_object_or_404(
        Guiche,
        id=guiche_id
    )
    senha_atual = (
        Senha.objects
        .filter(
            guiche=guiche,
            status="chamando"
        )
        .order_by("-id")
        .first()
    )
    hoje = timezone.localdate()
    fila = (
        Senha.objects
        .filter(status="espera",
                criada_em__date=hoje)
        .order_by("criada_em", "id")[:5]
    )
    context = {
        "guiche": guiche,
        "senha_atual": senha_atual,
        "fila": fila
    }

    return render(
        request,
        "filas/guiche.html",
        context
    )

# =========================
# CHAMAR PRÓXIMA SENHA
# =========================
# @login_required
@require_POST
def chamar_proxima(request, guiche_id):
    guiche = get_object_or_404(
        Guiche,
        id=guiche_id
    )
    hoje = timezone.localdate()
    with transaction.atomic():
        controle = (
            ControleFila.objects
            .select_for_update()
            .first()
        )
        if not controle:

            controle = ControleFila.objects.create(
                contador=0
            )

        senha_anterior = (
            Senha.objects
            .filter(
                guiche=guiche,
                status="chamando"
            )
            .order_by("-id")
            .first()
        )

        if senha_anterior:
            senha_anterior.status = "finalizado"
            senha_anterior.save(
                update_fields=["status"]
            )

            Historico.objects.create(
                senha=senha_anterior,
                guiche=guiche,
                acao="finalizado"
            )

        existe_preferencial = (
            Senha.objects
            .filter(
                status="espera",
                tipo="preferencial",
                criada_em__date=hoje
            )
            .exists()
        )

        existe_normal = (
            Senha.objects
            .filter(
                status="espera",
                tipo="normal",
                criada_em__date=hoje
            )
            .exists()
        )

        if not existe_preferencial and not existe_normal:

            return redirect(
                f"/filas/guiche/{guiche_id}/"
            )


        proximo_contador = (
            controle.contador + 1
        )

        if proximo_contador % 3 == 1:
            tipo_prioritario = "preferencial"
        else:
            tipo_prioritario = "normal"

        senha = (
            Senha.objects
            .select_for_update()
            .filter(
                status="espera",
                tipo=tipo_prioritario,
                criada_em__date=hoje
            )
            .order_by(
                "criada_em",
                "id"
            )
            .first()
        )

        if not senha:
            outro_tipo = (
                "normal"
                if tipo_prioritario == "preferencial"
                else "preferencial"
            )
            senha = (
                Senha.objects
                .select_for_update()
                .filter(
                    status="espera",
                    tipo=outro_tipo,
                    criada_em__date=hoje
                )
                .order_by(
                    "criada_em",
                    "id"
                )
                .first()
            )

        if not senha:
            return redirect(
                f"/filas/guiche/{guiche_id}/"
            )
        
        senha.status = "chamando"
        senha.guiche = guiche

        senha.save(
            update_fields=[
                "status",
                "guiche"
            ]
        )

        Historico.objects.create(
            senha=senha,
            guiche=guiche,
            acao="chamando"
        )

        controle.contador = (
            proximo_contador
        )

        controle.save(
            update_fields=[
                "contador"
            ]
        )

    return redirect(
        f"/filas/guiche/{guiche_id}/"
    )

def totem(request):
    return render(
        request,
        "totem/retirar.html",
        {
            "modo_totem": True
        }
    )

@require_POST
def chamar_novamente(request, guiche_id):
    guiche = get_object_or_404(Guiche, id=guiche_id)

    senha = (
        Senha.objects
        .filter(
            guiche=guiche,
            status="chamando"
        )
        .order_by("-id")
        .first()
    )

    if senha:
        Historico.objects.create(
            senha=senha,
            guiche=guiche,
            acao="chamando_novamente"
        )

    return redirect(f"/filas/guiche/{guiche_id}/")
# =========================
# PAINEL TV
# =========================
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


# =========================
# API PARA TV
# =========================
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

# =========================
# API PAINEL FUNCIONÁRIOS
# =========================
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

def testar_filas_spring(request):
    filas = listar_filas()
    return JsonResponse({"filas": filas})