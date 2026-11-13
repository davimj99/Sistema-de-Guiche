from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from accounts.models import Guiche
from ..models import Senha
from ..services import FilaService


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
    FilaService.chamar_proxima(guiche_id=guiche_id)
    return redirect(f"/filas/guiche/{guiche_id}/")


# =========================
# CHAMAR NOVAMENTE
# =========================
@login_required
@require_POST
def chamar_novamente(request, guiche_id):
    FilaService.chamar_novamente(guiche_id=guiche_id)
    return redirect(f"/filas/guiche/{guiche_id}/")
