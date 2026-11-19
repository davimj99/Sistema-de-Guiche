from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.decorators import renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_yasg.utils import swagger_auto_schema

from filas.services import FilaService
from api.throttles import PainelRateThrottle
from api.serializers import (
    ApiRootResponseSerializer,
    PainelResponseSerializer,
    StatusFilaResponseSerializer,
    UserProfileSerializer,
)


class ApiRootBrowsableRenderer(BrowsableAPIRenderer):
    """Browsable renderer with the API Root's Portuguese auth controls."""
    template = 'api/root.html'


@swagger_auto_schema(
    method='get',
    operation_summary="Catálogo Interativo de Endpoints da API",
    operation_description=(
        "Página inicial interativa da API v1. Apresenta hyperlinks reais e clicáveis "
        "para navegação ponto a ponto na Browsable API do Django REST Framework."
    ),
    responses={200: ApiRootResponseSerializer},
    tags=['Catálogo']
)
@api_view(['GET'])
@renderer_classes([JSONRenderer, ApiRootBrowsableRenderer])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Página inicial interativa da API REST (v1).
    Apresenta hyperlinks clicáveis para todos os recursos operacionais na Browsable API do DRF.
    """
    def res(name):
        try:
            return reverse(f"api:{name}", request=request, format=format)
        except Exception:
            try:
                return reverse(name, request=request, format=format)
            except Exception:
                return None

    endpoints = {
        "painel": res("painel"),
        "guiches": res("guiches-list") or res("guiches"),
        "filas": res("filas") or res("status_filas"),
        "senhas": res("senhas-list"),
        "atendimentos": res("atendimentos-list"),
        "status_filas": res("status_filas"),
        "auth_token": res("token_obtain_pair"),
        "auth_refresh": res("token_refresh"),
        "auth_me": res("user_profile"),
    }
    if request.user.is_authenticated and request.user.is_superuser:
        endpoints["swagger"] = res("schema-swagger-ui")
        endpoints["redoc"] = res("schema-redoc")

    data = {
        "nome": "API Sistema de Atendimento & Filas",
        "versao": "v1.0",
        "endpoints": {k: v for k, v in endpoints.items() if v is not None},
        "documentacao": (
            "Endpoints navegáveis via Django REST Framework Browsable API "
            "prontos para consumo por totens, TVs e sistemas externos."
        )
    }
    return Response(data)


# ============================================================
# ENDPOINTS PÚBLICOS DE OPERAÇÃO (TOTEM & PAINEL DE TV)
# ============================================================
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
@throttle_classes([PainelRateThrottle])
def painel_api(request):
    """
    Retorna o estado em tempo real do painel de chamadas consumindo o FilaService.
    """
    data = FilaService.obter_estado_painel()
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Status e Métricas das Filas do Dia",
    operation_description="Retorna métricas em tempo real das filas do dia atual via FilaService.",
    responses={200: StatusFilaResponseSerializer},
    tags=['Filas']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def status_fila_api(request):
    """
    Retorna métricas em tempo real das filas do dia.
    """
    data = FilaService.obter_status_filas()
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Perfil do Usuário Autenticado",
    operation_description="Retorna os dados do usuário autenticado via BasicAuthentication ou Bearer JWT.",
    responses={200: UserProfileSerializer},
    tags=['Autenticação']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Endpoint autenticado via BasicAuth ou Bearer JWT.
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


# ============================================================

