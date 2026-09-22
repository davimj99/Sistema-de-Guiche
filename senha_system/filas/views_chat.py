import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .chatbot import obter_resposta


@login_required
@require_POST
def chatbot_api(request):

    try:
        data = json.loads(request.body)

        pergunta = data.get("pergunta", "").strip()

        resposta = obter_resposta(pergunta)

        return JsonResponse({
            "sucesso": True,
            **resposta
        })

    except json.JSONDecodeError as e:

        return JsonResponse({
            "sucesso": False,
            "erro": f"JSON inválido: {str(e)}"
        }, status=400)

    except Exception as e:

        print("ERRO CHATBOT:", e)

        return JsonResponse({
            "sucesso": False,
            "erro": str(e)
        }, status=500)