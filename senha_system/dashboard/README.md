# 📊 Painel Administrativo Personalizado & BI — Faculdade ISCON

O **Painel Administrativo ISCON** é um dashboard executivo e operacional moderno, de nível de produção, desenvolvido para transformar dados operacionais do Sistema de Guichê e Filas em inteligência gerencial e tomada de decisão estratégica para a **Faculdade ISCON**.

---

## 🏗️ 1. Arquitetura e Organização dos Componentes

O módulo segue rigorosamente a arquitetura **MTV (Model-Template-View) + Services Layer** do Django:

```
senha_system/
├── dashboard/
│   ├── migrations/
│   │   └── 0001_initial.py             # Criação da tabela de auditoria de API
│   ├── models.py                       # ApiRequestLog (telemetria da API REST sem dados sensíveis)
│   ├── middleware.py                   # ApiMonitoringMiddleware (medição de latência e HTTP status)
│   ├── permissions.py                  # Decoradores de proteção (@admin_dashboard_required, @admin_api_required)
│   ├── services/
│   │   ├── date_filter.py              # Cálculo timezone-aware de períodos e variações percentuais
│   │   ├── kpi_service.py              # Cálculo de cards, métricas e tempos médios de atendimento
│   │   ├── chart_service.py            # Séries temporais e datasets Chart.js
│   │   ├── productivity_service.py     # Desempenho e rankings operacionais por guichê e atendente
│   │   └── api_monitoring_service.py   # Telemetria, volumetria diária, distribuição de status e métodos
│   ├── views/
│   │   ├── dashboard_views.py          # Renderização das páginas HTML (Visão Geral, Atendimentos, etc.)
│   │   └── api_views.py                # Endpoints JSON assíncronos (AJAX/Fetch API para atualização sem reload)
│   ├── urls.py                         # Rotas do painel (/dashboard/...)
│   └── tests/                          # Suíte de testes automatizados com cobertura completa
├── frontend/static/dashboard/
│   ├── css/dashboard.css               # Design System profissional (Tabler/Sneat, Dark/Light mode)
│   └── js/dashboard.js                 # Engine do tema, Chart.js dinâmico, Live Polling e Fetch API
└── frontend/templates/dashboard/
    ├── base_dashboard.html             # Shell mestre com Sidebar colapsável e Header
    ├── index.html                      # Dashboard Principal (Visão Geral)
    ├── atendimentos.html               # Análise Aprofundada de Atendimentos e Serviços
    ├── produtividade.html              # Produtividade por Guichê e Atendente
    ├── api_monitor.html                # Monitoramento de Requisições da API REST
    └── historico.html                  # Tabelas administrativas com busca, paginação e ordenação
```

---

## 📈 2. Mapeamento de Fontes de Dados e Indicadores

| Indicador | Origem dos Dados (Models) | Regra / Fórmula de Cálculo | Limitações / Observações |
| :--- | :--- | :--- | :--- |
| **Senhas Emitidas** | `filas.models.Senha` | `COUNT(id)` com filtro `criada_em__range` | Comparado com período anterior de mesma duração. |
| **Atendimentos Realizados** | `atendimentos.models.Atendimento` | `COUNT(id)` com filtro `fim__isnull=False` e `fim__range` | Considera atendimentos concluídos no período. |
| **Em Atendimento Agora** | `atendimentos.models.Atendimento` e `filas.models.Senha` | `MAX(Atendimento.objects.filter(fim__isnull=True).count(), Senha.objects.filter(status='atendimento').count())` | Indicador instantâneo em tempo real. |
| **Aguardando na Fila** | `filas.models.Senha` | `COUNT(id)` com filtro `status='espera'` | Fila de espera ao vivo para chamadas. |
| **Senhas Canceladas** | `filas.models.Senha` | `COUNT(id)` com filtro `status='cancelado'` | No fluxo atual do sistema, os status oficiais são `espera`, `chamando`, `atendimento` e `finalizado`. O cálculo retorna 0 com nota de integridade técnica. |
| **Requisições da API** | `dashboard.models.ApiRequestLog` | `COUNT(id)` com filtro `criado_em__range` | Capturado via `ApiMonitoringMiddleware` em chamadas para `/api/...`. |
| **Guichês Ativos** | `accounts.models.Guiche` | `COUNT(id)` com filtro `ativo=True` | Razão entre guichês disponíveis e total cadastrado. |
| **Atendentes Ativos** | `atendimentos.models.Atendimento` e `auth.models.User` | Atendentes distintos com registros no período e operadores staff ativos | Evita contagens falsas. |
| **Tempo Médio de Atendimento** | `atendimentos.models.Atendimento` | $\frac{\sum (\text{fim} - \text{inicio})}{\text{Total com Amostra Válida}}$ | Conversão de timezone precisa (`America/Sao_Paulo`) combinando `fim.date()` com `inicio` (TimeField). Filtra durações entre 10s e 4h. |

---

## 📊 3. Gráficos Interativos Implementados (Chart.js)

1. **Senhas Emitidas vs Atendimentos Realizados**: Série temporal com preenchimento em gradiente translúcido comparando entrada de fila vs resolução.
2. **Distribuição por Tipo de Serviço Acadêmico**: Gráfico Donut com percentual de Matrícula, Financeiro, Secretaria, Declaração, etc.
3. **Distribuição por Guichê**: Gráfico de barras indicando a carga de trabalho de cada guichê.
4. **Distribuição por Atendente**: Volume de atendimentos finalizados por membro da equipe.
5. **Horários de Maior Movimento**: Concentração de chamadas entre as 07:00 e 22:00, identificando os horários de pico.
6. **Série Diária, Semanal e Mensal de Atendimentos**: Agrupamento temporal via `TruncDate`, `TruncWeek` e `TruncMonth`.
7. **Telemetria de API REST**: Volume diário de requisições, tráfego por hora e proporção de códigos HTTP (2xx, 3xx, 4xx, 5xx).

---

## 🌐 4. Endpoints e Rotas Criadas

### Páginas HTML (Protegidas com `@admin_dashboard_required`)
- `GET /dashboard/`: Visão Geral do Painel.
- `GET /dashboard/atendimentos/`: Análise aprofundada de atendimentos e categorias.
- `GET /dashboard/produtividade/`: Produtividade e médias de guichês e atendentes.
- `GET /dashboard/api-monitor/`: Telemetria, latência e códigos HTTP da API.
- `GET /dashboard/historico/`: Tabelas completas com paginação e busca.

### Endpoints JSON Assíncronos (Protegidos com `@admin_api_required`)
- `GET /dashboard/api/kpis/?periodo=...`: Retorna dados dos cards de KPIs e variação percentual.
- `GET /dashboard/api/charts/?periodo=...`: Retorna datasets completos para atualização do Chart.js sem refresh.
- `GET /dashboard/api/productivity/?periodo=...`: Retorna relatório de desempenho.
- `GET /dashboard/api/api-monitoring/?periodo=...`: Retorna telemetria da API.
- `GET /dashboard/api/live-status/`: Polling leve (20s) com contagem de espera e atendimento ao vivo.

---

## 🎨 5. Identidade Visual e UI/UX

- **Design System**: Inspirado no Tabler Dashboard e Sneat, com paleta oficial da Faculdade ISCON:
  - Azul ISCON: `#0d6efd`
  - Azul Noturno: `#0a3d91`
  - Vermelho ISCON: `#d32f2f`
- **Dark Mode e Light Mode**: Alternância instantânea com persistência no `localStorage`.
- **Gráficos Reativos ao Tema**: As cores das grades, fontes e tooltips do Chart.js adaptam-se automaticamente ao modo claro ou escuro.
- **Responsividade Total**: Sidebar retrátil em desktops e gaveta (drawer) com backdrop touch no mobile/tablet.

---

## 🔒 6. Segurança e Permissões

- Todas as views e APIs exigem que o usuário esteja autenticado (`user.is_authenticated`) e possua perfil administrativo (`user.is_staff` ou `user.is_superuser`).
- Tentativas de acesso não autenticadas são redirecionadas para `accounts:login`.
- Usuários autenticados sem permissão administrativa são redirecionados com mensagem amigável de erro.
- Formulários e ações utilizam proteção CSRF.
- O `ApiMonitoringMiddleware` **não registra payloads**, senhas, tokens JWT ou cabeçalhos de autorização.

---

## 🧪 7. Testes Automatizados

A suíte de testes em `dashboard/tests/` cobre:
1. `test_services.py`: Filtros de data, cálculo de tendência, agregações de KPIs, geração de gráficos, relatório de produtividade, telemetria de API e resiliência em banco de dados vazio.
2. `test_views.py`: Bloqueio de anônimos, bloqueio de não-staff, autorização de staff, payloads JSON de APIs e paginação com filtros de histórico.
3. `test_middleware.py`: Captura de requisições em `/api/` e descarte de rotas fora do escopo.

Para rodar todos os testes:
```bash
python manage.py test dashboard
```
