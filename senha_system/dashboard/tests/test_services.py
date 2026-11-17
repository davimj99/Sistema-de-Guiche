import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from accounts.models import Guiche
from filas.models import Senha, Historico
from atendimentos.models import Atendimento
from dashboard.models import ApiRequestLog
from dashboard.services import (
    calcular_intervalo_filtro,
    calcular_variacao_percentual,
    KpiService,
    ChartService,
    ProductivityService,
    ApiMonitoringService,
)


class DashboardServicesTestCase(TestCase):
    """
    Testes automatizados para os serviços de métricas, KPIs, gráficos e monitoramento do Dashboard.
    """

    def setUp(self):
        # Usuário Staff
        self.user_staff = User.objects.create_user(
            username="gestor_iscon",
            password="password123",
            is_staff=True
        )

        # Guichês
        self.guiche_1 = Guiche.objects.create(nome="Guichê 01", ativo=True)
        self.guiche_2 = Guiche.objects.create(nome="Guichê 02", ativo=True)
        self.guiche_inativo = Guiche.objects.create(nome="Guichê 03", ativo=False)

        hoje = timezone.localtime()

        # Criação de Senhas
        self.senha_1 = Senha.objects.create(
            prefixo="A", numero=1, tipo="normal", status="finalizado", guiche=self.guiche_1
        )
        self.senha_2 = Senha.objects.create(
            prefixo="P", numero=1, tipo="preferencial", status="atendimento", guiche=self.guiche_2
        )
        self.senha_3 = Senha.objects.create(
            prefixo="A", numero=2, tipo="normal", status="espera"
        )

        # Criação de Atendimentos
        hora_inicio = datetime.time(10, 0, 0)
        dt_fim = hoje.replace(hour=10, minute=15, second=0, microsecond=0)

        self.atendimento_1 = Atendimento.objects.create(
            senha=self.senha_1,
            guiche=self.guiche_1.id,
            atendente="Rafael",
            aluno="Aluno Teste A",
            tipo="matricula",
            inicio=hora_inicio,
            fim=dt_fim
        )

        self.atendimento_2 = Atendimento.objects.create(
            senha=self.senha_2,
            guiche=self.guiche_2.id,
            atendente="Alessandra",
            aluno="Aluno Teste B",
            tipo="financeiro",
            inicio=hora_inicio,
            fim=None  # Em andamento
        )

        # Logs de API
        ApiRequestLog.objects.create(
            endpoint="/api/v1/painel/",
            metodo="GET",
            status_code=200,
            tempo_resposta_ms=12.5,
            ip_origem="127.0.0.1"
        )
        ApiRequestLog.objects.create(
            endpoint="/api/v1/senhas/emitir/",
            metodo="POST",
            status_code=201,
            tempo_resposta_ms=25.0,
            ip_origem="127.0.0.1"
        )
        ApiRequestLog.objects.create(
            endpoint="/api/v1/guiches/999/",
            metodo="GET",
            status_code=404,
            tempo_resposta_ms=8.0,
            ip_origem="127.0.0.1"
        )

    def test_calcular_intervalo_filtro(self):
        """Valida se o cálculo de períodos (hoje, 7d, 30d, etc.) retorna limites corretos."""
        inicio, fim, ini_ant, fim_ant, rotulo = calcular_intervalo_filtro("hoje")
        self.assertEqual(rotulo, "Hoje")
        self.assertLess(inicio, fim)
        self.assertLess(ini_ant, fim_ant)

        inicio_7d, fim_7d, _, _, rotulo_7d = calcular_intervalo_filtro("7d")
        self.assertEqual(rotulo_7d, "Últimos 7 dias")
        self.assertEqual((fim_7d.date() - inicio_7d.date()).days, 6)

    def test_calcular_variacao_percentual(self):
        """Valida o cálculo de tendência e percentual."""
        var_alta = calcular_variacao_percentual(20, 10)
        self.assertEqual(var_alta["tendencia"], "alta")
        self.assertEqual(var_alta["percentual"], 100.0)

        var_baixa = calcular_variacao_percentual(5, 10)
        self.assertEqual(var_baixa["tendencia"], "baixa")
        self.assertEqual(var_baixa["percentual"], -50.0)

        var_zero = calcular_variacao_percentual(0, 0)
        self.assertEqual(var_zero["percentual"], 0.0)
        self.assertEqual(var_zero["tendencia"], "neutro")

    def test_kpi_service_valores(self):
        """Valida o cálculo consolidado de todos os KPIs operacionais."""
        dados = KpiService.obter_kpis_completos(periodo="hoje")
        kpis = dados["kpis"]

        # Senhas
        self.assertEqual(kpis["senhas_emitidas"]["total"], 3)
        # Atendimentos finalizados
        self.assertEqual(kpis["atendimentos_realizados"]["total"], 1)
        # Em andamento
        self.assertGreaterEqual(kpis["em_andamento"]["total"], 1)
        # Aguardando
        self.assertEqual(kpis["aguardando_espera"]["total"], 1)
        # Canceladas
        self.assertEqual(kpis["senhas_canceladas"]["total"], 0)
        # Requisições API
        self.assertEqual(kpis["requisicoes_api"]["total"], 3)
        # Guichês
        self.assertEqual(kpis["guiches_ativos"]["total"], 2)
        self.assertEqual(kpis["guiches_ativos"]["total_geral"], 3)
        # Atendentes
        self.assertGreaterEqual(kpis["atendentes_ativos"]["total"], 1)
        # Tempo Médio (15 minutos = 900s)
        self.assertEqual(kpis["tempo_medio"]["minutos"], 15.0)
        self.assertEqual(kpis["tempo_medio"]["formatado"], "15m 00s")

    def test_chart_service_estruturas(self):
        """Valida se o serviço de gráficos retorna estruturas válidas para Chart.js."""
        dados = ChartService.obter_graficos_dashboard(periodo="7d")
        
        self.assertIn("serie_temporal_comparativa", dados)
        self.assertIn("distribuicao_tipo", dados)
        self.assertIn("distribuicao_guiche", dados)
        self.assertIn("distribuicao_atendente", dados)
        self.assertIn("horarios_movimento", dados)

        # Checa datasets
        comp = dados["serie_temporal_comparativa"]
        self.assertEqual(len(comp["datasets"]), 2)
        self.assertIn("labels", comp)

        tipo = dados["distribuicao_tipo"]
        self.assertIn("Matrícula", tipo["labels"])

    def test_productivity_service(self):
        """Valida a consolidação de produtividade por atendente e guichê."""
        relatorio = ProductivityService.obter_relatorio_produtividade(periodo="hoje")

        self.assertEqual(relatorio["total_atendimentos"], 1)
        self.assertIn("guiches", relatorio)
        self.assertIn("atendentes", relatorio)

        # Guichê 01 deve liderar com 1 atendimento
        g1 = next((g for g in relatorio["guiches"] if g["guiche_id"] == self.guiche_1.id), None)
        self.assertIsNotNone(g1)
        self.assertEqual(g1["total"], 1)
        self.assertEqual(g1["percentual_total"], 100.0)

        # Atendente Rafael deve ter 1 atendimento
        at_rafael = next((a for a in relatorio["atendentes"] if a["nome"] == "Rafael"), None)
        self.assertIsNotNone(at_rafael)
        self.assertEqual(at_rafael["total"], 1)

    def test_api_monitoring_service(self):
        """Valida o cálculo de métricas de telemetria da API REST."""
        metricas = ApiMonitoringService.obter_metricas_api(periodo="hoje")

        self.assertEqual(metricas["total_requisicoes"], 3)
        self.assertEqual(metricas["sucessos"], 2)
        self.assertEqual(metricas["erros"], 1)
        self.assertAlmostEqual(metricas["taxa_sucesso"], 66.7, places=1)
        self.assertAlmostEqual(metricas["tempo_medio_ms"], (12.5 + 25.0 + 8.0) / 3, places=1)

        # Status HTTP
        self.assertEqual(metricas["distribuicao_status"]["2xx"], 2)
        self.assertEqual(metricas["distribuicao_status"]["4xx"], 1)
        self.assertEqual(metricas["distribuicao_status"]["5xx"], 0)

    def test_cenario_sem_dados(self):
        """Garante resiliência e ausência de divisões por zero quando o banco estiver vazio."""
        Atendimento.objects.all().delete()
        Senha.objects.all().delete()
        ApiRequestLog.objects.all().delete()

        kpis = KpiService.obter_kpis_completos(periodo="hoje")["kpis"]
        self.assertEqual(kpis["senhas_emitidas"]["total"], 0)
        self.assertEqual(kpis["atendimentos_realizados"]["total"], 0)
        self.assertEqual(kpis["tempo_medio"]["minutos"], 0.0)
        self.assertEqual(kpis["requisicoes_api"]["total"], 0)

        charts = ChartService.obter_graficos_dashboard(periodo="hoje")
        self.assertIsInstance(charts["serie_temporal_comparativa"]["labels"], list)

        metricas = ApiMonitoringService.obter_metricas_api(periodo="hoje")
        self.assertEqual(metricas["total_requisicoes"], 0)
        self.assertEqual(metricas["taxa_sucesso"], 100.0)
