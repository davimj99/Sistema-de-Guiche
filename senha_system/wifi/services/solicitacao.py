from wifi.models import SolicitacaoWifi


def gerar_protocolo():

    ultimo = (
        SolicitacaoWifi.objects
        .order_by('-id')
        .first()
    )

    if ultimo:
        numero = ultimo.id + 1
    else:
        numero = 1

    return f'WIFI-2026-{numero:06d}'


def criar_solicitacao(
    nome_aluno,
    matricula,
    curso,
    email=None,
    dispositivo=None,
    motivo=None,
):

    protocolo = gerar_protocolo()

    return SolicitacaoWifi.objects.create(
        protocolo=protocolo,
        nome_aluno=nome_aluno,
        matricula=matricula,
        curso=curso,
        email=email,
        dispositivo=dispositivo,
        motivo=motivo,
    )