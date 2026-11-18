from .dashboard_views import (
    index,
    atendimentos_view,
    produtividade_view,
    api_monitor_view,
    historico_view,
)
from .api_views import (
    kpis_api,
    charts_api,
    productivity_api,
    api_monitoring_api,
    live_status_api,
)

__all__ = [
    "index",
    "atendimentos_view",
    "produtividade_view",
    "api_monitor_view",
    "historico_view",
    "kpis_api",
    "charts_api",
    "productivity_api",
    "api_monitoring_api",
    "live_status_api",
]
