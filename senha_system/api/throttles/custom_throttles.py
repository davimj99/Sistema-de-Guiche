from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
    ScopedRateThrottle,
)


class CustomAnonRateThrottle(AnonRateThrottle):
    """Controle padrão para requisições anônimas não autenticadas."""
    scope = 'anon'


class CustomUserRateThrottle(UserRateThrottle):
    """Controle padrão para requisições autenticadas por usuário."""
    scope = 'user'


class TotemRateThrottle(AnonRateThrottle):
    """
    Controle específico para totens de autoatendimento.
    Permite emissão ágil sem sofrer bloqueio indevido por requisições legítimas.
    """
    scope = 'totem'


class PainelRateThrottle(AnonRateThrottle):
    """
    Controle para os monitores e TVs do painel de chamada.
    Configurado com limites elevados para suportar polling contínuo (ex: a cada 2-3 segundos).
    """
    scope = 'painel'


class ChamadaRateThrottle(UserRateThrottle):
    """
    Controle para ações de operadores de guichê (chamar próxima, rechamar).
    Garante proteção contra disparos repetitivos ou scripts automatizados.
    """
    scope = 'chamadas'
