from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render

from ..forms import EntregaEPIForm
from ..models import EntregaEPI


# ============================================================
# ENTREGAS
# ============================================================

@login_required
def entregas_lista(request):

    entregas = EntregaEPI.objects.select_related(
        "funcionario",
        "epi"
    ).all()

    busca = request.GET.get(
        "busca",
        ""
    ).strip()

    if busca:

        entregas = entregas.filter(
            models.Q(
                funcionario__nome__icontains=busca
            )
            | models.Q(
                epi__nome__icontains=busca
            )
            | models.Q(
                epi__codigo__icontains=busca
            )
        )

    return render(
        request,
        "epis/entregas.html",
        {
            "entregas": entregas,
            "busca": busca,
        }
    )


@login_required
def entrega_nova(request):

    if request.method == "POST":

        form = EntregaEPIForm(
            request.POST
        )

        if form.is_valid():

            entrega = form.save(
                commit=False
            )

            epi = entrega.epi

            if entrega.quantidade > epi.quantidade_estoque:

                form.add_error(
                    "quantidade",
                    (
                        "Estoque insuficiente. "
                        f"Disponível: "
                        f"{epi.quantidade_estoque}."
                    )
                )

            else:

                epi.quantidade_estoque -= (
                    entrega.quantidade
                )

                epi.save(
                    update_fields=[
                        "quantidade_estoque"
                    ]
                )

                entrega.save()

                messages.success(
                    request,
                    "Entrega registrada com sucesso."
                )

                return redirect(
                    "epis:entregas"
                )

    else:

        form = EntregaEPIForm()

    return render(
        request,
        "epis/entrega_form.html",
        {
            "form": form,
            "titulo": "Nova entrega",
            "acao": "Registrar entrega",
        }
    )

@login_required
def entrega_excluir(request, pk):
    if request.method == "POST":
        entrega = get_object_or_404(EntregaEPI, pk=pk)

        entrega.delete()

        messages.success(
            request,
            "Entrega de EPI excluída com sucesso."
        )

    return redirect("epis:entregas")
