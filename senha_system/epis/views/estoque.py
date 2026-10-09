from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render

from ..models import EPI


# ============================================================
# ESTOQUE
# ============================================================

@login_required
def estoque(request):

    epis = EPI.objects.filter(
        ativo=True
    )

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status == "baixo":

        epis = epis.filter(
            quantidade_estoque__lte=models.F(
                "estoque_minimo"
            )
        )

    elif status == "zerado":

        epis = epis.filter(
            quantidade_estoque=0
        )

    return render(
        request,
        "epis/estoque.html",
        {
            "epis": epis,
            "status": status,
        }
    )