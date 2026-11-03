from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Guiche
from filas.models import Senha, Historico
from .serializers import (
    ApiRootResponseSerializer,
    PainelResponseSerializer,
    GuichesListResponseSerializer,
    StatusFilaResponseSerializer,
    UserProfileSerializer,
)


@swagger_auto_schema(
    method='get',
    operation_summary="Catálogo de Endpoints da API",
    operation_description="Retorna os endpoints públicos e operacionais disponíveis no Sistema de Atendimento.",
    responses={200: ApiRootResponseSerializer},
    tags=['Catálogo']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Índice da API v1 do Sistema de Atendimento.
    Documentação navegável dos endpoints públicos e operacionais.
    """
    data = {
        "nome": "API Sistema de Atendimento & Filas",
        "versao": "v1.0",
        "endpoints": {
            "painel": "/api/v1/painel/",
            "guiches": "/api/v1/guiches/",
            "status_filas": "/api/v1/filas/status/",
            "auth_token": "/api/v1/auth/token/",
            "auth_refresh": "/api/v1/auth/token/refresh/",
            "auth_me": "/api/v1/auth/me/",
            "swagger": "/swagger/",
            "redoc": "/redoc/",
        },
        "documentacao": "Endpoints em formato JSON REST prontos para consumo por totens, TVs e sistemas externos."
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Estado em Tempo Real do Painel de TV",
    operation_description=(
        "Retorna os dados ao vivo para exibição nos monitores da sala de espera:\n"
        "- Última senha chamada com guichê e tipo\n"
        "- Histórico recente das últimas 10 chamadas\n"
        "- Fila de espera do dia atual"
    ),
    responses={200: PainelResponseSerializer},
    tags=['Painel & Totem']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def painel_api(request):
    """
    Retorna o estado em tempo real do painel de chamadas:
    - Última senha chamada (com guichê e tipo)
    - Histórico recente das últimas 10 chamadas
    - Fila atual de senhas em espera no dia
    """
    hoje = timezone.localdate()

    # Última senha sendo chamada
    ultima_chamada = (
        Historico.objects
        .filter(acao__in=["chamando", "chamando_novamente"])
        .select_related("senha", "guiche")
        .order_by("-id")
        .first()
    )

    # Histórico recente
    ultimas_chamadas = list(
        Historico.objects
        .filter(acao__in=["chamando", "chamando_novamente"])
        .select_related("senha", "guiche")
        .order_by("-id")[:10]
    )

    # Fila de espera do dia
    fila_espera = list(
        Senha.objects
        .filter(status="espera", criada_em__date=hoje)
        .order_by("criada_em", "id")[:15]
    )

    dados_ultima = None
    if ultima_chamada and ultima_chamada.senha:
        dados_ultima = {
            "senha": f"{ultima_chamada.senha.prefixo}{ultima_chamada.senha.numero}",
            "tipo": ultima_chamada.senha.tipo,
            "guiche": ultima_chamada.guiche.nome if ultima_chamada.guiche else "",
            "chamada_id": ultima_chamada.id,
            "acao": ultima_chamada.acao,
            "hora": timezone.localtime(ultima_chamada.criada_em).strftime("%H:%M:%S") if hasattr(ultima_chamada, "criada_em") and ultima_chamada.criada_em else None,
        }

    data = {
        "status": "sucesso",
        "timestamp": timezone.now().isoformat(),
        "ultima": dados_ultima,
        "ultimas": [
            {
                "senha": f"{h.senha.prefixo}{h.senha.numero}" if h.senha else "",
                "guiche": h.guiche.nome if h.guiche else "",
                "chamada_id": h.id,
                "acao": h.acao,
            }
            for h in ultimas_chamadas
        ],
        "fila": [
            {
                "senha": f"{s.prefixo}{s.numero}",
                "tipo": s.tipo,
                "posicao": idx + 1,
            }
            for idx, s in enumerate(fila_espera)
        ]
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Listar Guichês Ativos",
    operation_description="Retorna a lista de todos os guichês de atendimento ativos cadastrados no sistema.",
    responses={200: GuichesListResponseSerializer},
    tags=['Guichês']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def guiches_api(request):
    """
    Retorna a lista de guichês de atendimento cadastrados e ativos.
    Executa apenas 1 query eficiente no banco.
    """
    guiches = list(Guiche.objects.filter(ativo=True).order_by("id"))

    data = {
        "status": "sucesso",
        "total": len(guiches),
        "guiches": [
            {
                "id": g.id,
                "nome": g.nome,
                "ativo": g.ativo,
            }
            for g in guiches
        ]
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Status e Métricas das Filas do Dia",
    operation_description="Retorna métricas em tempo real das filas: senhas emitidas, em espera, em chamada e finalizadas.",
    responses={200: StatusFilaResponseSerializer},
    tags=['Filas']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def status_fila_api(request):
    """
    Retorna métricas em tempo real das filas do dia:
    - Quantidade em espera (total, normais, preferenciais)
    - Quantidade em atendimento
    - Quantidade finalizada
    """
    hoje = timezone.localdate()
    senhas_hoje = Senha.objects.filter(criada_em__date=hoje)

    espera_normal = senhas_hoje.filter(status="espera", tipo="normal").count()
    espera_pref = senhas_hoje.filter(status="espera", tipo="preferencial").count()
    chamando = senhas_hoje.filter(status="chamando").count()
    finalizadas = senhas_hoje.filter(status="finalizado").count()

    data = {
        "status": "sucesso",
        "data": hoje.strftime("%Y-%m-%d"),
        "total_emitidas_hoje": senhas_hoje.count(),
        "em_espera": {
            "total": espera_normal + espera_pref,
            "normal": espera_normal,
            "preferencial": espera_pref,
        },
        "chamando": chamando,
        "finalizadas": finalizadas,
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Perfil do Usuário Autenticado",
    operation_description="Retorna os dados do usuário autenticado via cabeçalho HTTP `Authorization: Bearer <token_jwt>`.",
    responses={200: UserProfileSerializer},
    tags=['Autenticação JWT']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Endpoint autenticado via Bearer JWT.
    Retorna o perfil do usuário atualmente autenticado.
    """
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    }
    return Response(data)
