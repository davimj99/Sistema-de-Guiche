/**
 * PAINEL ADMINISTRATIVO ISCON - DASHBOARD ENGINE
 * Gerencia Dark Mode, Gráficos Chart.js reativos, Filtros assíncronos e Live Updates.
 */

(function () {
  'use strict';

  // Instâncias ativas dos gráficos
  const chartInstances = {};

  // =========================================================================
  // 1. GERENCIADOR DE TEMA (DARK / LIGHT MODE)
  // =========================================================================
  function initTheme() {
    const savedTheme = localStorage.getItem('iscon_dash_theme') || 'light';
    applyTheme(savedTheme);

    const toggleBtn = document.getElementById('btnThemeToggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('iscon_dash_theme', newTheme);
        updateChartThemes(newTheme);
      });
    }
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const label = document.getElementById('themeLabel');
    const icon = document.getElementById('themeIcon');
    if (label) {
      label.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
    }
    if (icon) {
      icon.innerHTML = theme === 'dark' 
        ? '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>'
        : '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    }
  }

  function getChartColorsForTheme(theme) {
    const isDark = theme === 'dark';
    return {
      textColor: isDark ? '#94a3b8' : '#64748b',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      tooltipBg: isDark ? '#1e293b' : '#0f172a',
      tooltipText: '#ffffff',
    };
  }

  function updateChartThemes(theme) {
    const colors = getChartColorsForTheme(theme);
    Object.values(chartInstances).forEach(chart => {
      if (chart && chart.options) {
        if (chart.options.scales) {
          if (chart.options.scales.x) {
            chart.options.scales.x.ticks.color = colors.textColor;
            chart.options.scales.x.grid.color = colors.gridColor;
          }
          if (chart.options.scales.y) {
            chart.options.scales.y.ticks.color = colors.textColor;
            chart.options.scales.y.grid.color = colors.gridColor;
          }
        }
        if (chart.options.plugins && chart.options.plugins.legend) {
          chart.options.plugins.legend.labels.color = colors.textColor;
        }
        chart.update();
      }
    });
  }

  // =========================================================================
  // 2. SIDEBAR MOBILE / TOGGLE
  // =========================================================================
  function initSidebar() {
    const toggleBtn = document.getElementById('btnSidebarToggle');
    const sidebar = document.getElementById('dashSidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', () => {
        const isOpen = sidebar.classList.toggle('sidebar-open');
        toggleBtn.setAttribute('aria-expanded', String(isOpen));
        if (backdrop) backdrop.classList.toggle('active', isOpen);
      });
    }

    const closeSidebar = () => {
      if (sidebar) sidebar.classList.remove('sidebar-open');
      if (backdrop) backdrop.classList.remove('active');
      if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
    };
    if (sidebar) sidebar.querySelectorAll('a').forEach(link => link.addEventListener('click', closeSidebar));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeSidebar();
    });

    if (backdrop) {
      backdrop.addEventListener('click', closeSidebar);
    }
  }

  function showFeedback(message, type) {
    const el = document.getElementById('dashFeedback');
    if (!el) return;
    el.textContent = message;
    el.dataset.type = type || 'success';
    el.hidden = false;
  }

  function isAjaxDashboard() {
    const tab = document.body.dataset.activeTab;
    return tab === 'visao_geral' || tab === 'atendimentos';
  }

  function navigateWithFilters(periodOverride) {
    const params = new URLSearchParams(window.location.search);
    const activePeriod = document.querySelector('.period-btn.active[data-periodo]');
    const period = periodOverride || (activePeriod && activePeriod.dataset.periodo) || params.get('periodo') || '7d';
    params.set('periodo', period);
    params.delete('page');

    [
      ['filterGuiche', 'guiche_id'],
      ['filterAtendente', 'atendente'],
      ['filterTipo', 'tipo_atendimento'],
      ['filterStatus', 'status_senha'],
      ['filterDataInicio', 'data_inicio'],
      ['filterDataFim', 'data_fim'],
    ].forEach(([elementId, key]) => {
      const field = document.getElementById(elementId);
      if (!field) return;
      if (field.value) params.set(key, field.value);
      else params.delete(key);
    });

    if (period === 'personalizado') {
      const start = params.get('data_inicio');
      const end = params.get('data_fim');
      if (!start || !end || start > end) {
        showFeedback('Informe um período válido, com data inicial anterior à final.', 'error');
        return;
      }
    }
    window.location.assign(`${window.location.pathname}?${params.toString()}`);
  }

  // =========================================================================
  // 3. CRIAÇÃO DE GRÁFICOS (CHART.JS)
  // =========================================================================
  function renderChart(canvasId, type, data, customOptions = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    if (!window.Chart) {
      setChartStatus(canvas, 'Não foi possível carregar a biblioteca de gráficos. Atualize a página para tentar novamente.');
      return null;
    }

    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }

    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const themeColors = getChartColorsForTheme(currentTheme);

    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: type !== 'bar' || data.datasets.length > 1,
          position: 'top',
          labels: {
            color: themeColors.textColor,
            font: { family: 'Open Sans', size: 12, weight: 600 },
          }
        },
        tooltip: {
          backgroundColor: themeColors.tooltipBg,
          titleColor: themeColors.tooltipText,
          bodyColor: themeColors.tooltipText,
          padding: 10,
          cornerRadius: 6,
          boxPadding: 4,
        }
      },
      scales: (type === 'pie' || type === 'doughnut') ? {} : {
        x: {
          ticks: { color: themeColors.textColor, font: { size: 11 } },
          grid: { color: themeColors.gridColor }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: themeColors.textColor,
            font: { size: 11 },
            precision: 0,
          },
          grid: { color: themeColors.gridColor }
        }
      }
    };

    const finalOptions = deepMerge(baseOptions, customOptions);

    chartInstances[canvasId] = new Chart(canvas, {
      type: type,
      data: data,
      options: finalOptions
    });
    const hasValues = (data.datasets || []).some(dataset =>
      (dataset.data || []).some(value => Number(value) > 0)
    );
    setChartStatus(canvas, hasValues ? '' : 'Sem atendimentos no período selecionado.');

    return chartInstances[canvasId];
  }

  function setChartStatus(canvas, message) {
    const container = canvas.closest('.chart-canvas-container');
    if (!container) return;
    let status = container.querySelector('.chart-status');
    if (!status) {
      status = document.createElement('p');
      status.className = 'chart-status';
      status.setAttribute('role', 'status');
      container.appendChild(status);
    }
    status.textContent = message;
    status.hidden = !message;
  }

  function deepMerge(target, source) {
    for (const key of Object.keys(source)) {
      if (source[key] instanceof Object && key in target) {
        Object.assign(source[key], deepMerge(target[key], source[key]));
      }
    }
    Object.assign(target || {}, source);
    return target;
  }

  // =========================================================================
  // 4. ATUALIZAÇÃO ASSÍNCRONA VIA FILTROS (FETCH API)
  // =========================================================================
  function getFilterParams() {
    const params = new URLSearchParams();
    const activePeriod = document.querySelector('.period-btn.active');
    if (activePeriod) {
      params.set('periodo', activePeriod.getAttribute('data-periodo') || '7d');
    }

    const guicheSelect = document.getElementById('filterGuiche');
    if (guicheSelect && guicheSelect.value) params.set('guiche_id', guicheSelect.value);

    const atendenteSelect = document.getElementById('filterAtendente');
    if (atendenteSelect && atendenteSelect.value) params.set('atendente', atendenteSelect.value);

    const tipoSelect = document.getElementById('filterTipo');
    if (tipoSelect && tipoSelect.value) params.set('tipo_atendimento', tipoSelect.value);

    const statusSelect = document.getElementById('filterStatus');
    if (statusSelect && statusSelect.value) params.set('status_senha', statusSelect.value);

    const dataInicio = document.getElementById('filterDataInicio');
    if (dataInicio && dataInicio.value) params.set('data_inicio', dataInicio.value);

    const dataFim = document.getElementById('filterDataFim');
    if (dataFim && dataFim.value) params.set('data_fim', dataFim.value);

    return params;
  }

  async function reloadDashboardData() {
    const params = getFilterParams();
    const queryStr = params.toString();

    // Feedback visual de carregamento
    showLoadingState(true);

    try {
      // 1. Atualizar KPIs
      const kpisRes = await fetch(`/dashboard/api/kpis/?${queryStr}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (!kpisRes.ok) throw new Error('Falha ao atualizar indicadores.');
      const kpisJson = await kpisRes.json();
      if (kpisJson.status !== 'sucesso') throw new Error('A API não retornou os indicadores.');
      updateKpisUI(kpisJson.dados.kpis, kpisJson.dados.periodo_rotulo);

      // 2. Atualizar Gráficos se estiver na visão geral ou atendimentos
      const chartsRes = await fetch(`/dashboard/api/charts/?${queryStr}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (!chartsRes.ok) throw new Error('Falha ao atualizar gráficos.');
      const chartsJson = await chartsRes.json();
      if (chartsJson.status !== 'sucesso') throw new Error('A API não retornou os gráficos.');
      updateChartsUI(chartsJson.dados);
      showFeedback('Indicadores e gráficos atualizados.', 'success');
    } catch (err) {
      console.warn("Erro ao atualizar dados assíncronos:", err);
      showFeedback(err.message || 'Não foi possível atualizar os dados. Tente novamente.', 'error');
    } finally {
      showLoadingState(false);
    }
  }

  function showLoadingState(isLoading) {
    const loader = document.getElementById('dashLoader');
    if (loader) {
      loader.style.display = isLoading ? 'flex' : 'none';
    }
  }

  function updateKpisUI(kpis, rotulo) {
    const rotuloEl = document.getElementById('periodoRotuloDisplay');
    if (rotuloEl && rotulo) rotuloEl.textContent = rotulo;

    if (!kpis) return;

    const setMetric = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };
    if (kpis.total_atendimentos) setMetric('kpiTotalAtendimentos', Number(kpis.total_atendimentos.total).toLocaleString('pt-BR'));
    if (kpis.atendimentos_concluidos) setMetric('kpiConcluidos', Number(kpis.atendimentos_concluidos.total).toLocaleString('pt-BR'));
    if (kpis.media_diaria) setMetric('kpiMediaDiaria', Number(kpis.media_diaria.valor).toLocaleString('pt-BR', { maximumFractionDigits: 1 }));
    if (kpis.taxa_conclusao) setMetric('kpiTaxaConclusao', `${Number(kpis.taxa_conclusao.percentual).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`);

    function setCardValue(valId, trendId, kpiObj) {
      const valEl = document.getElementById(valId);
      if (valEl && kpiObj) {
        valEl.textContent = Number(kpiObj.total).toLocaleString('pt-BR');
      }
      const trendEl = document.getElementById(trendId);
      if (trendEl && kpiObj && kpiObj.variacao) {
        trendEl.className = `trend-badge trend-${kpiObj.variacao.tendencia}`;
        trendEl.textContent = kpiObj.variacao.texto;
      }
    }

    setCardValue('kpiSenhasVal', 'kpiSenhasTrend', kpis.senhas_emitidas);
    setCardValue('kpiAtendVal', 'kpiAtendTrend', kpis.atendimentos_realizados);
    setCardValue('kpiApiVal', 'kpiApiTrend', kpis.requisicoes_api);

    // Indicadores ao vivo
    const emAndamentoEl = document.getElementById('kpiAndamentoVal');
    if (emAndamentoEl && kpis.em_andamento) {
      emAndamentoEl.textContent = kpis.em_andamento.total;
    }

    const esperaEl = document.getElementById('kpiEsperaVal');
    if (esperaEl && kpis.aguardando_espera) {
      esperaEl.textContent = kpis.aguardando_espera.total;
    }

    const canceladasEl = document.getElementById('kpiCanceladasVal');
    if (canceladasEl && kpis.senhas_canceladas) {
      canceladasEl.textContent = kpis.senhas_canceladas.total;
    }

    const guichesEl = document.getElementById('kpiGuichesVal');
    if (guichesEl && kpis.guiches_ativos) {
      guichesEl.textContent = `${kpis.guiches_ativos.total} / ${kpis.guiches_ativos.total_geral}`;
    }

    const atendentesEl = document.getElementById('kpiAtendentesVal');
    if (atendentesEl && kpis.atendentes_ativos) {
      atendentesEl.textContent = kpis.atendentes_ativos.total;
    }

    const tempoMedioEl = document.getElementById('kpiTempoMedioVal');
    if (tempoMedioEl && kpis.tempo_medio) {
      tempoMedioEl.textContent = kpis.tempo_medio.formatado;
    }
  }

  function updateChartsUI(chartData) {
    if (!chartData) return;

    [
      ['chartAtendimentosDia', chartData.atendimentos_por_dia, 'line'],
      ['chartAtendimentosSemana', chartData.atendimentos_por_semana, 'bar'],
      ['chartAtendimentosMes', chartData.atendimentos_por_mes, 'bar'],
    ].forEach(([id, data, type]) => {
      if (!data) return;
      if (chartInstances[id]) {
        chartInstances[id].data = data;
        chartInstances[id].update();
        const hasValues = (data.datasets || []).some(dataset =>
          (dataset.data || []).some(value => Number(value) > 0)
        );
        setChartStatus(document.getElementById(id), hasValues ? '' : 'Sem atendimentos no período selecionado.');
      } else {
        renderChart(id, type, data, {
          plugins: { legend: { display: false } },
          ...(type === 'line' ? { elements: { line: { tension: 0.3 } } } : {})
        });
      }
    });

    if (chartInstances['chartComparativo'] && chartData.serie_temporal_comparativa) {
      chartInstances['chartComparativo'].data = chartData.serie_temporal_comparativa;
      chartInstances['chartComparativo'].update();
    }

    if (chartInstances['chartTipo'] && chartData.distribuicao_tipo) {
      chartInstances['chartTipo'].data = chartData.distribuicao_tipo;
      chartInstances['chartTipo'].update();
    }

    if (chartInstances['chartGuiche'] && chartData.distribuicao_guiche) {
      chartInstances['chartGuiche'].data = chartData.distribuicao_guiche;
      chartInstances['chartGuiche'].update();
    }

    if (chartInstances['chartAtendente'] && chartData.distribuicao_atendente) {
      chartInstances['chartAtendente'].data = chartData.distribuicao_atendente;
      chartInstances['chartAtendente'].update();
    }

    if (chartInstances['chartHorarios'] && chartData.horarios_movimento) {
      chartInstances['chartHorarios'].data = chartData.horarios_movimento;
      chartInstances['chartHorarios'].update();
    }
  }

  // =========================================================================
  // 5. LIVE POLLING SUAVE (STATUS DA FILA AO VIVO)
  // =========================================================================
  function initLivePolling() {
    if (!isAjaxDashboard()) return;
    setInterval(async () => {
      try {
        const res = await fetch('/dashboard/api/live-status/', {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (res.ok) {
          const json = await res.json();
          if (json.status === 'sucesso' && json.ao_vivo) {
            const esperaEl = document.getElementById('kpiEsperaVal');
            if (esperaEl) esperaEl.textContent = json.ao_vivo.aguardando_espera;

            const andamentoEl = document.getElementById('kpiAndamentoVal');
            if (andamentoEl) andamentoEl.textContent = json.ao_vivo.em_atendimento;
          }
        }
      } catch (e) {
        // Falha silenciosa no polling de fundo
      }
    }, 20000); // 20s
  }

  // =========================================================================
  // 6. INICIALIZAÇÃO GERAL
  // =========================================================================
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initLivePolling();

    // Eventos dos botões de período rápido
    const periodButtons = document.querySelectorAll('.period-btn');
    periodButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const period = btn.getAttribute('data-periodo');
        if (!period) return;
        periodButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Alterna campo de data personalizada se necessário
        const customContainer = document.getElementById('customDateRange');
        if (customContainer) {
          customContainer.style.display = period === 'personalizado' ? 'flex' : 'none';
        }

        if (isAjaxDashboard()) reloadDashboardData();
        else navigateWithFilters(period);
      });
    });

    // Eventos dos filtros dropdown
    const filterSelects = document.querySelectorAll('.filter-select-auto');
    filterSelects.forEach(sel => {
      sel.addEventListener('change', () => {
        if (isAjaxDashboard()) reloadDashboardData();
        else navigateWithFilters();
      });
    });

    const btnCustomDate = document.getElementById('btnApplyCustomDate');
    if (btnCustomDate) {
      btnCustomDate.addEventListener('click', () => {
        const start = document.getElementById('filterDataInicio')?.value;
        const end = document.getElementById('filterDataFim')?.value;
        if (!start || !end || start > end) {
          showFeedback('Informe um período válido, com data inicial anterior à final.', 'error');
          return;
        }
        if (isAjaxDashboard()) reloadDashboardData();
        else navigateWithFilters('personalizado');
      });
    }
  });

  // Exportar funções globais úteis para os templates
  window.IsconDashboard = {
    renderChart,
    reloadDashboardData,
    updateChartsUI,
  };

})();
