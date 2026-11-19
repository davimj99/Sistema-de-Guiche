from django.test import TestCase, Client
from django.urls import reverse
from dashboard.models import ApiRequestLog


class ApiMonitoringMiddlewareTestCase(TestCase):
    """
    Testes automatizados para o middleware de instrumentação e telemetria da API.
    """

    def setUp(self):
        self.client = Client()

    def test_instrumentacao_endpoint_api(self):
        """Chamadas a rotas /api/... devem ser interceptadas e gravadas no ApiRequestLog."""
        contagem_inicial = ApiRequestLog.objects.count()

        # Chamada a um endpoint público da API (/api/v1/filas/)
        res = self.client.get('/api/v1/filas/')
        self.assertEqual(res.status_code, 200)

        # Verifica se o log foi gerado
        self.assertEqual(ApiRequestLog.objects.count(), contagem_inicial + 1)
        ultimo_log = ApiRequestLog.objects.latest('criado_em')
        self.assertEqual(ultimo_log.endpoint, '/api/v1/filas/')
        self.assertEqual(ultimo_log.metodo, 'GET')
        self.assertEqual(ultimo_log.status_code, 200)
        self.assertGreaterEqual(ultimo_log.tempo_resposta_ms, 0.0)
        self.assertIsNone(ultimo_log.ip_origem)

    def test_ignora_rotas_fora_da_api(self):
        """Requisições a páginas normais (fora de /api/) não devem poluir a tabela de logs da API."""
        contagem_inicial = ApiRequestLog.objects.count()

        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        # Contagem não deve alterar
        self.assertEqual(ApiRequestLog.objects.count(), contagem_inicial)
