from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date

from xhtml2pdf import pisa

from epis.models import EPI, Funcionario, EntregaEPI



def usuario_autorizado(user):
    return user.is_superuser

def link_callback(uri, rel):
    static_url = settings.STATIC_URL or "/static/"

    if uri.startswith(static_url):
        caminho_relativo = uri[len(static_url):].split("?", 1)[0]
        caminho = finders.find(caminho_relativo)

        if caminho:
            return str(caminho)

    return uri

@login_required
@user_passes_test(usuario_autorizado)
def relatorio_controle_epi(request):
    funcionarios = Funcionario.objects.filter(ativo=True)
    epis = EPI.objects.filter(ativo=True)

    funcionario_id = request.GET.get("funcionario", "").strip()
    epi_id = request.GET.get("epi", "").strip()
    data_inicio_texto = request.GET.get("data_inicio", "").strip()
    data_fim_texto = request.GET.get("data_fim", "").strip()

    data_inicio = parse_date(data_inicio_texto) if data_inicio_texto else None
    data_fim = parse_date(data_fim_texto) if data_fim_texto else None

    erros = []

    if data_inicio_texto and not data_inicio:
        erros.append("A data inicial é inválida.")

    if data_fim_texto and not data_fim:
        erros.append("A data final é inválida.")

    if data_inicio and data_fim and data_inicio > data_fim:
        erros.append("A data inicial não pode ser posterior à data final.")

    funcionario_selecionado = None
    epi_selecionado = None

    if funcionario_id:
        if not funcionario_id.isdigit():
            erros.append("Funcionário inválido.")
        else:
            funcionario_selecionado = funcionarios.filter(
                pk=int(funcionario_id)
            ).first()

            if not funcionario_selecionado:
                erros.append("Funcionário não encontrado ou inativo.")

    if epi_id:
        if not epi_id.isdigit():
            erros.append("EPI inválido.")
        else:
            epi_selecionado = epis.filter(
                pk=int(epi_id)
            ).first()

            if not epi_selecionado:
                erros.append("EPI não encontrado ou inativo.")

    if request.GET.get("pdf") == "1" and not erros:
        estoque = EPI.objects.filter(ativo=True).order_by("nome")

        if epi_selecionado:
            estoque = estoque.filter(pk=epi_selecionado.pk)

        entregas = EntregaEPI.objects.select_related(
            "funcionario",
            "epi",
        ).all()

        if funcionario_selecionado:
            entregas = entregas.filter(
                funcionario=funcionario_selecionado
            )

        if epi_selecionado:
            entregas = entregas.filter(epi=epi_selecionado)

        if data_inicio:
            entregas = entregas.filter(
                data_entrega__gte=data_inicio
            )

        if data_fim:
            entregas = entregas.filter(
                data_entrega__lte=data_fim
            )

        entregas = entregas.order_by(
            "-data_entrega",
            "-id",
        )

        contexto = {
            "estoque": estoque,
            "entregas": entregas,
            "funcionario_selecionado": funcionario_selecionado,
            "epi_selecionado": epi_selecionado,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "data_emissao": date.today(),
        }

        html = render_to_string(
            "epis/relatorio_pdf.html",
            contexto,
            request=request,
        )

        resposta = HttpResponse(
            content_type="application/pdf"
        )
        resposta["Content-Disposition"] = (
            'inline; filename="relatorio_controle_epi.pdf"'
        )

        resultado = pisa.CreatePDF(
            src=html,
            dest=resposta,
            encoding="utf-8",
            link_callback=link_callback,
        )

        if resultado.err:
            return HttpResponse(
                "Não foi possível gerar o relatório PDF.",
                status=500,
            )

        return resposta

    return render(
        request,
        "epis/relatorio_filtros.html",
        {
            "funcionarios": funcionarios,
            "epis": epis,
            "filtros": request.GET,
            "erros": erros,
        },
    )