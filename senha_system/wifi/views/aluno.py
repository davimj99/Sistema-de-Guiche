from django.shortcuts import render

from wifi.models import SolicitacaoWifi
from wifi.services.solicitacao import criar_solicitacao


def solicitar_wifi(request):
    if request.method == 'POST':
        nome_aluno = request.POST.get('nome_aluno')
        matricula = request.POST.get('matricula')
        curso = request.POST.get('curso')

        email = request.POST.get('email')
        dispositivo = request.POST.get('dispositivo')
        motivo = request.POST.get('motivo')

        solicitacao = criar_solicitacao(
            nome_aluno=nome_aluno,
            matricula=matricula,
            curso=curso,
            email=email,
            dispositivo=dispositivo,
            motivo=motivo,
        )

        return render(request,
            'wifi/solicitacao_sucesso.html',
            {'solicitacao': solicitacao }
        )
    return render(request, 'wifi/solicitar.html' )


def minhas_solicitacoes(request):
    protocolo = request.GET.get('protocolo', '').strip()
    if protocolo:
        try:
            solicitacao = SolicitacaoWifi.objects.get(
                protocolo__iexact=protocolo
            )
            return render(request,'wifi/detalhes.html',
                { 'solicitacao': solicitacao }
            )

        except SolicitacaoWifi.DoesNotExist:
            return render(request,'wifi/minhas_solicitacoes.html',
                { 'erro': 'Nenhuma solicitação encontrada para este protocolo.' }
            )
    return render(request,'wifi/minhas_solicitacoes.html')

def detalhes_solicitacao(request, protocolo):
    try:
        solicitacao = SolicitacaoWifi.objects.get(
            protocolo__iexact=protocolo
        )

    except SolicitacaoWifi.DoesNotExist:
        return render(
            request,
            'wifi/minhas_solicitacoes.html',
            {
                'erro': 'Solicitação não encontrada.'
            }
        )
    return render(request,'wifi/detalhes.html',
        {'solicitacao': solicitacao}
    )