from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from .utils import get_atendimentos
from django.conf import settings
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


# 🔐 PERMISSÃO ADMIN
def is_super_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_super_admin)
def relatorio_atendimentos(request):
    return render(request, 'atendimentos/atendimento.html')



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
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Atendimento_ISCON.pdf"'

    def link_callback(uri, rel):
        if uri.startswith('imagens/'):
            return os.path.join(settings.BASE_DIR, 'static', uri)
        return uri

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    return response