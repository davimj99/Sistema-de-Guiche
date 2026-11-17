from django.shortcuts import render
from accounts.models import Guiche


def index(request):
    """
    Página inicial (Hub do Sistema e Vitrine Comercial).
    Centraliza o acesso operacional a todos os módulos e apresenta a plataforma
    para clientes e novos interessados.
    """
    try:
        guiches = Guiche.objects.filter(ativo=True).order_by('id')
    except Exception:
        guiches = []

    context = {
        'guiches': guiches,
    }
    return render(request, 'core/index.html', context)
