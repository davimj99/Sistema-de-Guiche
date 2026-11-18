from django.shortcuts import render
from django.core.paginator import Paginator
from accounts.models import Guiche
<<<<<<< Updated upstream
=======
from django.db.models import Q
>>>>>>> Stashed changes
from filas.models import Senha, Historico
from atendimentos.models import Atendimento
from dashboard.models import ApiRequestLog
from dashboard.permissions import admin_dashboard_required
from dashboard.services import (
    KpiService,
    ChartService,
    ProductivityService,
    ApiMonitoringService,
    calcular_intervalo_filtro
)


def _obter_contexto_filtros(request):
    """Extrai e valida parâmetros de filtro da requisição GET."""
    periodo = request.GET.get('periodo', '7d')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    guiche_id = request.GET.get('guiche_id')
    atendente = request.GET.get('atendente')
    tipo_atendimento = request.GET.get('tipo_atendimento')
    status_senha = request.GET.get('status_senha')

    guiche_id_int = None
    if guiche_id and guiche_id.isdigit():
        guiche_id_int = int(guiche_id)

    # Opções para os seletores
    todos_guiches = Guiche.objects.filter(ativo=True).order_by('id')
    tipos_atendimento = Atendimento.TIPOS_ATENDIMENTO
<<<<<<< Updated upstream
    lista_atendentes = [nome for nome, _ in Atendimento.ATENDENTES]
=======
    lista_atendentes = list(
        Atendimento.objects.exclude(Q(atendente__isnull=True) | Q(atendente=""))
        .order_by("atendente").values_list("atendente", flat=True).distinct()
    )
>>>>>>> Stashed changes
    status_opcoes = Senha.STATUS

    return {
        "periodo": periodo,
        "data_inicio": data_inicio or "",
        "data_fim": data_fim or "",
        "guiche_id": guiche_id_int,
        "atendente": atendente or "",
        "tipo_atendimento": tipo_atendimento or "",
        "status_senha": status_senha or "",
        "todos_guiches": todos_guiches,
        "tipos_atendimento": tipos_atendimento,
        "lista_atendentes": lista_atendentes,
        "status_opcoes": status_opcoes,
    }


@admin_dashboard_required
def index(request):
    """
    Dashboard Principal — Visão Geral Operacional e Estratégica.
    Apresenta cards com KPIs, evolução temporal, distribuição de atendimentos e status em tempo real.
    """
    filtros = _obter_contexto_filtros(request)

    kpi_data = KpiService.obter_kpis_completos(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        guiche_id=filtros['guiche_id'],
        atendente=filtros['atendente'],
        tipo_atendimento=filtros['tipo_atendimento'],
        status_senha=filtros['status_senha'],
    )

    chart_data = ChartService.obter_graficos_dashboard(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        guiche_id=filtros['guiche_id'],
        atendente=filtros['atendente'],
        tipo_atendimento=filtros['tipo_atendimento'],
    )

    # Últimas 5 senhas em espera e últimas 5 chamadas recentes para monitoramento instantâneo
    senhas_em_espera = Senha.objects.filter(status='espera').order_by('criada_em')[:5]
    ultimos_atendimentos = Atendimento.objects.select_related('senha').order_by('-id')[:5]

    context = {
        **filtros,
        "kpis": kpi_data['kpis'],
        "periodo_rotulo": kpi_data['periodo_rotulo'],
        "chart_data": chart_data,
        "senhas_em_espera": senhas_em_espera,
        "ultimos_atendimentos": ultimos_atendimentos,
        "active_tab": "visao_geral",
    }
    return render(request, 'dashboard/index.html', context)


@admin_dashboard_required
def atendimentos_view(request):
    """
    Seção específica para Análise Aprofundada de Atendimentos e Filas.
    """
    filtros = _obter_contexto_filtros(request)

    kpi_data = KpiService.obter_kpis_completos(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        guiche_id=filtros['guiche_id'],
        atendente=filtros['atendente'],
        tipo_atendimento=filtros['tipo_atendimento'],
    )

    chart_data = ChartService.obter_graficos_dashboard(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        guiche_id=filtros['guiche_id'],
        atendente=filtros['atendente'],
        tipo_atendimento=filtros['tipo_atendimento'],
    )

    context = {
        **filtros,
        "kpis": kpi_data['kpis'],
        "periodo_rotulo": kpi_data['periodo_rotulo'],
        "chart_data": chart_data,
        "active_tab": "atendimentos",
    }
    return render(request, 'dashboard/atendimentos.html', context)


@admin_dashboard_required
def produtividade_view(request):
    """
    Seção de Produtividade e Desempenho Operacional por Guichê e por Atendente.
    """
    filtros = _obter_contexto_filtros(request)

    relatorio = ProductivityService.obter_relatorio_produtividade(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        guiche_id=filtros['guiche_id'],
        atendente=filtros['atendente'],
<<<<<<< Updated upstream
=======
        tipo_atendimento=filtros['tipo_atendimento'],
>>>>>>> Stashed changes
    )

    context = {
        **filtros,
        "relatorio": relatorio,
        "active_tab": "produtividade",
    }
    return render(request, 'dashboard/produtividade.html', context)


@admin_dashboard_required
def api_monitor_view(request):
    """
    Seção dedicada ao Monitoramento de Requisições, Desempenho e Erros da API REST.
    """
    filtros = _obter_contexto_filtros(request)
    endpoint_filtro = request.GET.get('endpoint', '')
    metodo_filtro = request.GET.get('metodo', '')

    metricas = ApiMonitoringService.obter_metricas_api(
        periodo=filtros['periodo'],
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        endpoint_filtro=endpoint_filtro,
        metodo_filtro=metodo_filtro,
    )

    context = {
        **filtros,
        "metricas": metricas,
        "endpoint_filtro": endpoint_filtro,
        "metodo_filtro": metodo_filtro,
        "active_tab": "api_monitor",
    }
    return render(request, 'dashboard/api_monitor.html', context)


@admin_dashboard_required
def historico_view(request):
    """
    Tabelas Administrativas com Paginação, Busca Textual, Filtros e Ordenação.
    Permite alternar entre Senhas, Atendimentos, Histórico e Requisições API.
    """
    filtros = _obter_contexto_filtros(request)
    aba = request.GET.get('tabela', 'atendimentos')
    busca = request.GET.get('busca', '').strip()
    pagina = request.GET.get('page', 1)

<<<<<<< Updated upstream
    inicio_atual, fim_atual, _, _, _ = calcular_intervalo_filtro(
        filtros['periodo'], filtros['data_inicio'], filtros['data_fim']
    )

    if aba == 'senhas':
        qs = Senha.objects.filter(criada_em__range=(inicio_atual, fim_atual)).select_related('guiche').order_by('-id')
=======
    if filtros['periodo'] == 'todos':
        inicio_atual = fim_atual = None
    else:
        inicio_atual, fim_atual, _, _, _ = calcular_intervalo_filtro(
            filtros['periodo'], filtros['data_inicio'], filtros['data_fim']
        )

    if aba == 'senhas':
        qs = Senha.objects.all()
        if inicio_atual:
            qs = qs.filter(criada_em__range=(inicio_atual, fim_atual))
        qs = qs.select_related('guiche').order_by('-id')
>>>>>>> Stashed changes
        if busca:
            qs = qs.filter(numero__icontains=busca) | qs.filter(prefixo__icontains=busca)
        if filtros['status_senha']:
            qs = qs.filter(status=filtros['status_senha'])
        if filtros['guiche_id']:
            qs = qs.filter(guiche_id=filtros['guiche_id'])
        paginador = Paginator(qs, 20)
        registros = paginador.get_page(pagina)

    elif aba == 'historico_operacoes':
<<<<<<< Updated upstream
        qs = Historico.objects.filter(criada_em__range=(inicio_atual, fim_atual)).select_related('senha', 'guiche').order_by('-id')
=======
        qs = Historico.objects.all()
        if inicio_atual:
            qs = qs.filter(criada_em__range=(inicio_atual, fim_atual))
        qs = qs.select_related('senha', 'guiche').order_by('-id')
>>>>>>> Stashed changes
        if busca:
            qs = qs.filter(acao__icontains=busca)
        if filtros['guiche_id']:
            qs = qs.filter(guiche_id=filtros['guiche_id'])
        paginador = Paginator(qs, 20)
        registros = paginador.get_page(pagina)

    elif aba == 'requisicoes_api':
<<<<<<< Updated upstream
        qs = ApiRequestLog.objects.filter(criado_em__range=(inicio_atual, fim_atual)).order_by('-criado_em')
=======
        qs = ApiRequestLog.objects.all()
        if inicio_atual:
            qs = qs.filter(criado_em__range=(inicio_atual, fim_atual))
        qs = qs.order_by('-criado_em')
>>>>>>> Stashed changes
        if busca:
            qs = qs.filter(endpoint__icontains=busca) | qs.filter(metodo__icontains=busca)
        paginador = Paginator(qs, 20)
        registros = paginador.get_page(pagina)

    else:  # Padrão: Atendimentos
        aba = 'atendimentos'
<<<<<<< Updated upstream
        qs = Atendimento.objects.filter(fim__range=(inicio_atual, fim_atual)).select_related('senha').order_by('-id')
=======
        qs = Atendimento.objects.all()
        if inicio_atual:
            qs = qs.filter(fim__range=(inicio_atual, fim_atual))
        qs = qs.select_related('senha').order_by('-id')
>>>>>>> Stashed changes
        if busca:
            qs = qs.filter(aluno__icontains=busca) | qs.filter(atendente__icontains=busca)
        if filtros['tipo_atendimento']:
            qs = qs.filter(tipo=filtros['tipo_atendimento'])
        if filtros['atendente']:
            qs = qs.filter(atendente=filtros['atendente'])
        if filtros['guiche_id']:
            qs = qs.filter(guiche=filtros['guiche_id'])
<<<<<<< Updated upstream
        paginador = Paginator(qs, 20)
        registros = paginador.get_page(pagina)

=======
        if filtros['status_senha']:
            qs = qs.filter(senha__status=filtros['status_senha'])
        paginador = Paginator(qs, 20)
        registros = paginador.get_page(pagina)

    query_filters = request.GET.copy()
    query_filters.pop('tabela', None)
    query_filters.pop('page', None)
    query_sem_busca = query_filters.copy()
    query_sem_busca.pop('busca', None)
>>>>>>> Stashed changes
    context = {
        **filtros,
        "tabela": aba,
        "busca": busca,
        "registros": registros,
<<<<<<< Updated upstream
        "active_tab": "historico",
    }
=======
        "query_sem_pagina": request.GET.copy(),
        "query_filters": query_filters.urlencode(),
        "query_sem_busca": query_sem_busca.urlencode(),
        "active_tab": "historico",
    }
    context['query_sem_pagina'].pop('page', None)
    context['query_sem_pagina'] = context['query_sem_pagina'].urlencode()
>>>>>>> Stashed changes
    return render(request, 'dashboard/historico.html', context)
