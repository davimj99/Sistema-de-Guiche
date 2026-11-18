from django.core.exceptions import ValidationError
from django.db.models import CharField
from django.db.models.functions import Cast
from django.utils.dateparse import parse_date
from .models import Atendimento


def get_atendimentos(request):
    atendimentos = Atendimento.objects.select_related('senha').all().order_by('-fim', '-id')

    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    atendente = request.GET.get('atendente')
    guiche = request.GET.get('guiche')
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    numero_senha = request.GET.get('senha')

    if tipo:
        atendimentos = atendimentos.filter(tipo=tipo)

    if data_inicio:
        parsed = parse_date(data_inicio)
        if not parsed:
            raise ValidationError('Data inicial inválida.')
        atendimentos = atendimentos.filter(fim__date__gte=parsed)

    if data_fim:
        parsed = parse_date(data_fim)
        if not parsed:
            raise ValidationError('Data final inválida.')
        atendimentos = atendimentos.filter(fim__date__lte=parsed)

    if data_inicio and data_fim and parse_date(data_inicio) > parse_date(data_fim):
        raise ValidationError('Data inicial não pode ser posterior à data final.')
    if atendente:
        atendimentos = atendimentos.filter(atendente__icontains=atendente.strip())
    if guiche:
        if not guiche.isdigit():
            raise ValidationError('Guichê inválido.')
        atendimentos = atendimentos.filter(guiche=int(guiche))
    if categoria:
        atendimentos = atendimentos.filter(tipo=categoria)
    if status:
        atendimentos = atendimentos.filter(senha__status=status)
    if numero_senha:
        atendimentos = atendimentos.annotate(
            _numero_senha_texto=Cast('senha__numero', CharField())
        ).filter(_numero_senha_texto__icontains=numero_senha.strip())

    return atendimentos
