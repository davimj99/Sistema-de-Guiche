from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Páginas do Painel Administrativo
    path('', views.index, name='index'),
    path('atendimentos/', views.atendimentos_view, name='atendimentos'),
    path('produtividade/', views.produtividade_view, name='produtividade'),
    path('api-monitor/', views.api_monitor_view, name='api_monitor'),
    path('historico/', views.historico_view, name='historico'),

    # Endpoints JSON para atualização assíncrona dos Gráficos e Filtros
    path('api/kpis/', views.kpis_api, name='api_kpis'),
    path('api/charts/', views.charts_api, name='api_charts'),
    path('api/productivity/', views.productivity_api, name='api_productivity'),
    path('api/api-monitoring/', views.api_monitoring_api, name='api_monitoring'),
    path('api/live-status/', views.live_status_api, name='api_live_status'),
]
