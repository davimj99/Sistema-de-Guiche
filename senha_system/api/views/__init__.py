"""Views da API organizadas por responsabilidade funcional."""

from .public import api_root, painel_api, status_fila_api, user_profile_api
from .guiche import GuicheViewSet, guiches_api
from .senha import SenhaViewSet
from .atendimento import AtendimentoViewSet

__all__ = [
    'api_root',
    'painel_api',
    'status_fila_api',
    'user_profile_api',
    'GuicheViewSet',
    'guiches_api',
    'SenhaViewSet',
    'AtendimentoViewSet',
]
