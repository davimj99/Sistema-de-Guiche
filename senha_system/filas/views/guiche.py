from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction

from accounts.models import Guiche
from ..models import Senha, ControleFila, Historico

# =========================
# TELA DO GUICHÊ
# =========================
@login_required
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
@login_required
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