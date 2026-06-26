from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from .utils import get_atendimentos
from django.conf import settings
import os
from django.shortcuts import render

def relatorio_atendimentos(request):
    atendimentos = get_atendimentos(request)

    return render(request, 'atendimentos/atendimentos.html', {
        'atendimentos': atendimentos
    })


def gerar_pdf(request):
    atendimentos = get_atendimentos(request)

    html = render_to_string(
        'atendimentos/pdf_atendimentos.html',
        {'atendimentos': atendimentos}
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatorio Atendimento ISCON.pdf"'


    def link_callback(uri, rel):
        # remove /static/ e transforma em caminho real
        if uri.startswith('imagens/'):
            return os.path.join(settings.BASE_DIR, 'static', uri)

        return uri


    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    return response