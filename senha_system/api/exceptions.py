import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Handler padronizado de exceções para a API REST.
    Garante respostas em JSON estruturado com status, código HTTP, mensagem amigável
    e detalhes sem vazar stack traces em produção.
    """
    response = exception_handler(exc, context)

    if response is not None:
        codigo = response.status_code

        # Mensagem contextual conforme a categoria de status DRF
        mensagens_padrao = {
            status.HTTP_400_BAD_REQUEST: "Dados da requisição inválidos ou mal formatados.",
            status.HTTP_401_UNAUTHORIZED: "Credenciais de autenticação não fornecidas ou inválidas.",
            status.HTTP_403_FORBIDDEN: "Acesso negado. Você não possui permissão para este recurso.",
            status.HTTP_404_NOT_FOUND: "Recurso solicitado não foi encontrado.",
            status.HTTP_405_METHOD_NOT_ALLOWED: "Método HTTP não permitido para este endpoint.",
            status.HTTP_429_TOO_MANY_REQUESTS: "Limite de requisições excedido. Tente novamente mais tarde.",
        }

        mensagem = mensagens_padrao.get(codigo, "Ocorreu um erro durante o processamento da requisição.")

        # Se houver detalhe string direto (ex: detail='Not found'), aproveita
        if isinstance(response.data, dict) and "detail" in response.data:
            mensagem = str(response.data["detail"])

        payload = {
            "status": "erro",
            "codigo": codigo,
            "mensagem": mensagem,
            "detalhes": response.data,
        }
        response.data = payload
        return response

    # Erro interno não tratado (HTTP 500)
    logger.exception(
        "Erro não tratado na API: %s - Contexto: %s",
        str(exc),
        context.get("view", "Desconhecido")
    )

    detalhe_interno = str(exc) if getattr(settings, "DEBUG", False) else None

    return Response(
        {
            "status": "erro",
            "codigo": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "mensagem": "Erro interno no servidor. Contate a equipe de TI caso o problema persista.",
            "detalhes": detalhe_interno,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
