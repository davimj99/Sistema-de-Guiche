from rest_framework.routers import DefaultRouter, APIRootView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import GuicheViewSet, SenhaViewSet, AtendimentoViewSet


class InteractiveAPIRootView(APIRootView):
    """
    API Root navegável e interativa para o Django REST Framework Browsable API.
    Apresenta hyperlinks reais e clicáveis para cada recurso no DRF Browsable API
    e URLs absolutas no JSON, permitindo navegação direta ponto a ponto.
    """

    def get(self, request, *args, **kwargs):
        format = kwargs.get('format', None)

        def res(name):
            try:
                return reverse(f"api:{name}", request=request, format=format)
            except Exception:
                try:
                    return reverse(name, request=request, format=format)
                except Exception:
                    return None

        # Endpoints estruturados com hyperlinks absolutos navegáveis
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
            "swagger": res("schema-swagger-ui"),
            "redoc": res("schema-redoc"),
        }

        # Filtra apenas endpoints resolvidos
        valid_endpoints = {k: v for k, v in endpoints.items() if v is not None}

        data = {
            "nome": "API Sistema de Atendimento & Filas",
            "versao": "v1.0",
            "endpoints": valid_endpoints,
            "documentacao": (
                "Endpoints navegáveis via Django REST Framework Browsable API "
                "prontos para consumo por totens, TVs e sistemas externos."
            )
        }
        return Response(data)


class InteractiveRouter(DefaultRouter):
    """
    Router estendido que disponibiliza a API Root interativa com suporte total
    à interface navegável (Browsable API) do Django REST Framework.
    """
    APIRootView = InteractiveAPIRootView


# Router central da API REST v1
router = InteractiveRouter()

# Registro canônico de ViewSets por domínio
router.register(r'guiches', GuicheViewSet, basename='guiches')
router.register(r'senhas', SenhaViewSet, basename='senhas')
router.register(r'atendimentos', AtendimentoViewSet, basename='atendimentos')

urlpatterns = router.urls
