from .models import Atendimento

def get_atendimentos(request):
    atendimentos = Atendimento.objects.all().order_by('-inicio')

    tipo = request.GET.get('tipo')
    if tipo:
        atendimentos = atendimentos.filter(tipo=tipo)

    return atendimentos