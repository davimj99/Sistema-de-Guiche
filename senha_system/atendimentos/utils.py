from .models import Atendimento


def get_atendimentos(request):
    atendimentos = Atendimento.objects.all().order_by('-fim')

    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if tipo:
        atendimentos = atendimentos.filter(tipo=tipo)

    if data_inicio:
        atendimentos = atendimentos.filter(fim__date__gte=data_inicio)

    if data_fim:
        atendimentos = atendimentos.filter(fim__date__lte=data_fim)

    return atendimentos