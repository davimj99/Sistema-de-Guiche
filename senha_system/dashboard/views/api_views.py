from django.http import JsonResponse
from dashboard.permissions import admin_api_required
from dashboard.services import (
    KpiService,
    ChartService,
    ProductivityService,
    ApiMonitoringService,
)
from filas.models import Senha
from atendimentos.models import Atendimento


@admin_api_required
def kpis_api(request):
    """Retorna KPIs em JSON para atualização dinâmica dos cards."""
    periodo = request.GET.get('periodo', '7d')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    guiche_id = request.GET.get('guiche_id')
    atendente = request.GET.get('atendente')
    tipo_atendimento = request.GET.get('tipo_atendimento')
    status_senha = request.GET.get('status_senha')

    guiche_id_int = int(guiche_id) if guiche_id and guiche_id.isdigit() else None

    dados = KpiService.obter_kpis_completos(
        periodo=periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        guiche_id=guiche_id_int,
        atendente=atendente,
        tipo_atendimento=tipo_atendimento,
        status_senha=status_senha,
    )
    return JsonResponse({"status": "sucesso", "dados": dados})


@admin_api_required
def charts_api(request):
    """Retorna datasets dos gráficos em JSON para renderização e update via Chart.js."""
    periodo = request.GET.get('periodo', '7d')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    guiche_id = request.GET.get('guiche_id')
    atendente = request.GET.get('atendente')
    tipo_atendimento = request.GET.get('tipo_atendimento')

    guiche_id_int = int(guiche_id) if guiche_id and guiche_id.isdigit() else None

    dados = ChartService.obter_graficos_dashboard(
        periodo=periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        guiche_id=guiche_id_int,
        atendente=atendente,
        tipo_atendimento=tipo_atendimento,
    )
    return JsonResponse({"status": "sucesso", "dados": dados})


@admin_api_required
def productivity_api(request):
    """Retorna relatório de produtividade em JSON."""
    periodo = request.GET.get('periodo', '7d')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    guiche_id = request.GET.get('guiche_id')
    atendente = request.GET.get('atendente')
<<<<<<< Updated upstream
=======
    tipo_atendimento = request.GET.get('tipo_atendimento')
>>>>>>> Stashed changes

    guiche_id_int = int(guiche_id) if guiche_id and guiche_id.isdigit() else None

    dados = ProductivityService.obter_relatorio_produtividade(
        periodo=periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        guiche_id=guiche_id_int,
        atendente=atendente,
<<<<<<< Updated upstream
=======
        tipo_atendimento=tipo_atendimento,
>>>>>>> Stashed changes
    )
    return JsonResponse({"status": "sucesso", "dados": dados})


@admin_api_required
def api_monitoring_api(request):
    """Retorna métricas de requisições da API REST em JSON."""
    periodo = request.GET.get('periodo', '7d')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    endpoint_filtro = request.GET.get('endpoint')
    metodo_filtro = request.GET.get('metodo')

    dados = ApiMonitoringService.obter_metricas_api(
        periodo=periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        endpoint_filtro=endpoint_filtro,
        metodo_filtro=metodo_filtro,
    )
    return JsonResponse({"status": "sucesso", "dados": dados})


@admin_api_required
def live_status_api(request):
    """
    Retorna métricas ao vivo para polling leve do painel (a cada 15-30s).
    """
    espera_total = Senha.objects.filter(status='espera').count()
    chamando_total = Senha.objects.filter(status='chamando').count()
    atendimento_total = Senha.objects.filter(status='atendimento').count()
    atendimentos_em_andamento = Atendimento.objects.filter(fim__isnull=True).count()

    return JsonResponse({
        "status": "sucesso",
        "ao_vivo": {
            "aguardando_espera": espera_total,
            "chamando": chamando_total,
            "em_atendimento": max(atendimento_total, atendimentos_em_andamento),
        }
    })
