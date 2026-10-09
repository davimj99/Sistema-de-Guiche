from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import EPIForm
from ..models import EPI


# ============================================================
# EPIs
# ============================================================

@login_required
def epis_lista(request):

    epis = EPI.objects.all()

    busca = request.GET.get(
        "busca",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    estoque = request.GET.get(
        "estoque",
        ""
    ).strip()

    if busca:

        epis = epis.filter(
            models.Q(nome__icontains=busca)
            | models.Q(codigo__icontains=busca)
            | models.Q(categoria__icontains=busca)
        )

    if status == "ativos":

        epis = epis.filter(
            ativo=True
        )

    elif status == "inativos":

        epis = epis.filter(
            ativo=False
        )

    if estoque == "baixo":

        epis = epis.filter(
            ativo=True,
            quantidade_estoque__lte=models.F(
                "estoque_minimo"
            )
        )

    return render(
        request,
        "epis/epis.html",
        {
            "epis": epis,
            "busca": busca,
            "status": status,
            "estoque": estoque,
        }
    )


@login_required
def epi_novo(request):

    if request.method == "POST":

        form = EPIForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "EPI cadastrado com sucesso."
            )

            return redirect(
                "epis:epis"
            )

    else:

        form = EPIForm()

    return render(
        request,
        "epis/epi_form.html",
        {
            "form": form,
            "titulo": "Novo EPI",
            "acao": "Cadastrar EPI",
        }
    )


@login_required
def epi_editar(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    if request.method == "POST":

        form = EPIForm(
            request.POST,
            instance=epi
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "EPI atualizado com sucesso."
            )

            return redirect(
                "epis:epis"
            )

    else:

        form = EPIForm(
            instance=epi
        )

    return render(
        request,
        "epis/epi_form.html",
        {
            "form": form,
            "epi": epi,
            "titulo": "Editar EPI",
            "acao": "Salvar alterações",
        }
    )


@login_required
@require_POST
def epi_alternar(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    epi.ativo = not epi.ativo

    epi.save(
        update_fields=["ativo"]
    )

    if epi.ativo:

        messages.success(
            request,
            f"{epi.nome} foi ativado."
        )

    else:

        messages.success(
            request,
            f"{epi.nome} foi desativado."
        )

    return redirect(
        "epis:epis"
    )


@login_required
@require_POST
def epi_excluir(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    nome = epi.nome

    try:

        epi.delete()

        messages.success(
            request,
            f"{nome} foi excluído com sucesso."
        )

    except ProtectedError:

        messages.error(
            request,
            (
                f"Não é possível excluir o EPI {nome}, "
                "pois existem entregas vinculadas a ele."
            )
        )

    return redirect(
        "epis:epis"
    )