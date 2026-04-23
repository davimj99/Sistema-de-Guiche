from django.shortcuts import render
from filas.models import Senha
from accounts.models import Guiche
from django.http import JsonResponse

def painel_publico(request):
    guiches = Guiche.objects.all()
    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-criada_em").first()

    ultimas = Senha.objects.filter(
        status="finalizado"
    ).order_by("-criada_em")[:10]

    context = {
        "guiches": guiches,
        "ultima": ultima,
        "ultimas": ultimas,
    }
    return render(request, "painel/painel.html", context)

def painel_dados(request):
    from filas.models import Senha
    ultima = Senha.objects.filter(
        status="chamando"
    ).order_by("-criada_em").first()

    data = {
        "senha": None,
        "guiche": None
    }

    if ultima:
        data["senha"] = f"{ultima.prefixo}{ultima.numero}"
        data["guiche"] = ultima.guiche.nome if ultima.guiche else ""
    return JsonResponse(data)