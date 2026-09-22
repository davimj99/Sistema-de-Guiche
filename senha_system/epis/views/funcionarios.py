from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import FuncionarioForm
from ..models import Funcionario


# ============================================================
# FUNCIONÁRIOS
# ============================================================

@login_required
def funcionarios(request):

    funcionarios = Funcionario.objects.all()

    busca = request.GET.get(
        "busca",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if busca:
        funcionarios = funcionarios.filter(
            models.Q(nome__icontains=busca)
            | models.Q(matricula__icontains=busca)
            | models.Q(setor__icontains=busca)
            | models.Q(cargo__icontains=busca)
        )

    if status == "ativos":

        funcionarios = funcionarios.filter(
            ativo=True
        )

    elif status == "inativos":

        funcionarios = funcionarios.filter(
            ativo=False
        )

    contexto = {
        "funcionarios": funcionarios,
        "busca": busca,
        "status": status,
    }

    return render(
        request,
        "epis/funcionarios_epis.html",
        contexto
    )


@login_required
def funcionario_novo(request):

    if request.method == "POST":

        form = FuncionarioForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Funcionário cadastrado com sucesso."
            )

            return redirect(
                "epis:funcionarios"
            )

    else:

        form = FuncionarioForm()

    return render(
        request,
        "epis/funcionarios_epis_form.html",
        {
            "form": form,
            "titulo": "Novo funcionário",
            "acao": "Cadastrar funcionário",
        }
    )


@login_required
def funcionario_editar(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    if request.method == "POST":

        form = FuncionarioForm(
            request.POST,
            instance=funcionario
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Funcionário atualizado com sucesso."
            )

            return redirect(
                "epis:funcionarios"
            )

    else:

        form = FuncionarioForm(
            instance=funcionario
        )

    return render(
        request,
        "epis/funcionarios_epis_form.html",
        {
            "form": form,
            "funcionario": funcionario,
            "titulo": "Editar funcionário",
            "acao": "Salvar alterações",
        }
    )


@login_required
@require_POST
def funcionario_alternar(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    funcionario.ativo = not funcionario.ativo

    funcionario.save(
        update_fields=["ativo"]
    )

    if funcionario.ativo:

        messages.success(
            request,
            f"{funcionario.nome} foi ativado."
        )

    else:

        messages.success(
            request,
            f"{funcionario.nome} foi desativado."
        )

    return redirect(
        "epis:funcionarios"
    )

@login_required
@require_POST
def funcionario_excluir(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    nome = funcionario.nome

    funcionario.delete()

    messages.success(
        request,
        f"{nome} foi excluído com sucesso."
    )

    return redirect(
        "epis:funcionarios"
    )