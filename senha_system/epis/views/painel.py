from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render

from ..models import EPI, EntregaEPI, Funcionario


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def painel(request):

    contexto = {
        "total_funcionarios": Funcionario.objects.filter(
            ativo=True
        ).count(),

        "total_epis": EPI.objects.filter(
            ativo=True
        ).count(),

        "total_entregas": EntregaEPI.objects.count(),

        "estoque_baixo": EPI.objects.filter(
            ativo=True,
            quantidade_estoque__lte=models.F(
                "estoque_minimo"
            )
        ).count(),
    }

    return render(
        request,
        "epis/painel_epis.html",
        contexto
    )