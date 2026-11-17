import datetime
from collections import defaultdict
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from dashboard.models import ApiRequestLog
from .date_filter import calcular_intervalo_filtro, calcular_variacao_percentual


class ApiMonitoringService:
    """
    Serviço analítico para monitoramento de desempenho e tráfego da API REST.
    """

    @classmethod
    def obter_metricas_api(
        cls,
        periodo: str = "7d",
        data_inicio: str = None,
        data_fim: str = None,
        endpoint_filtro: str = None,
        metodo_filtro: str = None,
    ) -> dict:
        inicio_atual, fim_atual, inicio_ant, fim_ant, rotulo = calcular_intervalo_filtro(
            periodo, data_inicio, data_fim
        )

        qs = ApiRequestLog.objects.filter(criado_em__range=(inicio_atual, fim_atual))
        qs_ant = ApiRequestLog.objects.filter(criado_em__range=(inicio_ant, fim_ant))

        if endpoint_filtro:
            qs = qs.filter(endpoint__icontains=endpoint_filtro)
            qs_ant = qs_ant.filter(endpoint__icontains=endpoint_filtro)
        if metodo_filtro:
            qs = qs.filter(metodo=metodo_filtro.upper())
            qs_ant = qs_ant.filter(metodo=metodo_filtro.upper())

        total_atual = qs.count()
        total_ant = qs_ant.count()
        var_total = calcular_variacao_percentual(total_atual, total_ant)

        # Sucessos vs Erros
        sucessos_count = qs.filter(status_code__lt=400).count()
        erros_count = qs.filter(status_code__gte=400).count()
        taxa_sucesso = round((sucessos_count / total_atual) * 100, 1) if total_atual > 0 else 100.0

        # Tempo médio de resposta
        tempo_medio = qs.aggregate(media=Avg('tempo_resposta_ms'))['media'] or 0.0

        # Distribuição por Família HTTP (2xx, 3xx, 4xx, 5xx)
        codigos_2xx = qs.filter(status_code__gte=200, status_code__lt=300).count()
        codigos_3xx = qs.filter(status_code__gte=300, status_code__lt=400).count()
        codigos_4xx = qs.filter(status_code__gte=400, status_code__lt=500).count()
        codigos_5xx = qs.filter(status_code__gte=500).count()

        # Distribuição por Método HTTP
        metodos = list(
            qs.values('metodo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Distribuição por Endpoint (Top 10 mais chamados)
        endpoints = list(
            qs.values('endpoint')
            .annotate(total=Count('id'), media_ms=Avg('tempo_resposta_ms'))
            .order_by('-total')[:10]
        )

        # Histórico recente (últimas 25 requisições)
        ultimas_requisicoes = list(
            qs.order_by('-criado_em')[:25].values(
                'id', 'endpoint', 'metodo', 'status_code', 'tempo_resposta_ms', 'ip_origem', 'criado_em'
            )
        )

        # Série Temporal: Requisições por Dia
        req_por_dia = dict(
            qs.annotate(dia=TruncDate('criado_em'))
            .values('dia')
            .annotate(total=Count('id'))
            .values_list('dia', 'total')
        )
        labels_dias = []
        dados_dias = []
        curr = inicio_atual.date()
        while curr <= fim_atual.date():
            labels_dias.append(curr.strftime("%d/%m"))
            dados_dias.append(req_por_dia.get(curr, 0))
            curr += datetime.timedelta(days=1)

        # Distribuição por Hora (00:00 às 23:00)
        horas_req = defaultdict(int)
        for req in qs.only('criado_em'):
            horas_req[req.criado_em.hour] += 1
        
        labels_horas = [f"{h:02d}:00" for h in range(24)]
        dados_horas = [horas_req[h] for h in range(24)]

        return {
            "periodo": rotulo,
            "total_requisicoes": total_atual,
            "variacao_total": var_total,
            "sucessos": sucessos_count,
            "erros": erros_count,
            "taxa_sucesso": taxa_sucesso,
            "tempo_medio_ms": round(tempo_medio, 2),
            "distribuicao_status": {
                "2xx": codigos_2xx,
                "3xx": codigos_3xx,
                "4xx": codigos_4xx,
                "5xx": codigos_5xx,
            },
            "metodos": metodos,
            "top_endpoints": endpoints,
            "ultimas_requisicoes": ultimas_requisicoes,
            "grafico_dias": {
                "labels": labels_dias,
                "datasets": [{
                    "label": "Requisições por Dia",
                    "data": dados_dias,
                    "borderColor": "#0d6efd",
                    "backgroundColor": "rgba(13, 110, 253, 0.2)",
                    "borderWidth": 2,
                    "fill": True,
                    "tension": 0.3,
                }]
            },
            "grafico_horas": {
                "labels": labels_horas,
                "datasets": [{
                    "label": "Requisições por Hora",
                    "data": dados_horas,
                    "backgroundColor": "#0a3d91",
                    "borderRadius": 4,
                }]
            },
            "grafico_status": {
                "labels": ["2xx Sucesso", "3xx Redirecionamento", "4xx Erro Cliente", "5xx Erro Servidor"],
                "datasets": [{
                    "data": [codigos_2xx, codigos_3xx, codigos_4xx, codigos_5xx],
                    "backgroundColor": ["#20c997", "#0dcaf0", "#ffc107", "#d32f2f"],
                }]
            }
        }
