from django.http import JsonResponse
from .models import Senha

def painel_dados(request):

    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-id").first()

    if not ultima:
        return JsonResponse({
            "status": "vazio",
            "mensagem": "Nenhuma senha sendo chamada"
        })

    return JsonResponse({
        "status": "sucesso",
        "dados": {
            "senha": f"{ultima.prefixo}{ultima.numero}",
            "guiche": ultima.guiche.nome if ultima.guiche else "",
            "tipo": ultima.tipo,
            "status": ultima.status,
            "chamada_em": ultima.chamada_em
        }
    })