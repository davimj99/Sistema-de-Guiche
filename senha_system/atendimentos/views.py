
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from xhtml2pdf import pisa
from .utils import get_atendimentos
from .models import Atendimento
from filas.models import Senha
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils import timezone


@login_required
@permission_required('atendimentos.view_atendimento', raise_exception=True)
def relatorio_atendimentos(request):
    erro = None
    try:
        atendimentos = get_atendimentos(request)
    except ValidationError as exc:
        atendimentos = Atendimento.objects.none()
        erro = '; '.join(exc.messages)
    pagina = Paginator(atendimentos, 50).get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)

    return render(request, 'atendimentos/atendimentos.html', {
        'atendimentos': pagina.object_list,
        'pagina': pagina,
        'query_sem_pagina': query.urlencode(),
        'erro_filtro': erro,
        'categorias': Atendimento.TIPOS_ATENDIMENTO,
        'status_senha': Senha.STATUS,
        'gerado_em': timezone.localtime(),
    })

@login_required
@permission_required('atendimentos.view_atendimento', raise_exception=True)
def gerar_pdf(request):
    try:
        atendimentos = get_atendimentos(request)
    except ValidationError as exc:
        return HttpResponse('; '.join(exc.messages), status=400)

    html = render_to_string(
        'atendimentos/pdf_atendimentos.html',
        {'atendimentos': atendimentos, 'gerado_em': timezone.localtime()},
        request=request
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="Relatorio_Atendimento_ISCON.pdf"'
    )

    def link_callback(uri, rel):
        if uri.startswith('/static/'):
            caminho_relativo = uri.replace('/static/', '', 1)
            caminho = finders.find(caminho_relativo)

            if caminho:
                return caminho

        return uri

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback,
        encoding='utf-8'
    )

    return response
