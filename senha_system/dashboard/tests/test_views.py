from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Guiche
from filas.models import Senha
from atendimentos.models import Atendimento
from dashboard.models import ApiRequestLog


class DashboardViewsTestCase(TestCase):
    """
    Testes de integração das Views HTML e endpoints JSON do Dashboard.
    Valida segurança, permissões e integridade das respostas.
    """

    def setUp(self):
        self.client = Client()

        # Usuário Comum (não staff)
        self.user_comum = User.objects.create_user(
            username="aluno_comum",
            password="password123",
            is_staff=False
        )

        # Usuário Staff (Gestor)
        self.user_staff = User.objects.create_user(
            username="gestor_iscon",
            password="password123",
            is_staff=True
        )

        self.guiche = Guiche.objects.create(nome="Guichê 01", ativo=True)
        self.senha = Senha.objects.create(prefixo="A", numero=1, tipo="normal", status="finalizado", guiche=self.guiche)
        self.atendimento = Atendimento.objects.create(
            senha=self.senha,
            guiche=self.guiche.id,
            atendente="Rafael",
            tipo="matricula",
        )

    def test_bloqueio_usuario_anonimo(self):
        """Usuário não autenticado deve ser redirecionado para a tela de login."""
        urls = [
            reverse('dashboard:index'),
            reverse('dashboard:atendimentos'),
            reverse('dashboard:produtividade'),
            reverse('dashboard:api_monitor'),
            reverse('dashboard:historico'),
        ]
        for u in urls:
            res = self.client.get(u)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/accounts/login/', res.url)

    def test_bloqueio_usuario_sem_permissao_staff(self):
        """Usuário autenticado sem perfil staff/superuser deve ter acesso negado/redirecionado."""
        self.client.login(username="aluno_comum", password="password123")
        res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res.status_code, 302)
        # Redireciona com mensagem de erro para a página inicial
        self.assertEqual(res.url, reverse('core:index'))

    def test_acesso_permitido_usuario_staff(self):
        """Usuário com perfil staff deve acessar todas as páginas HTML do Dashboard com HTTP 200."""
        self.client.login(username="gestor_iscon", password="password123")
        urls = [
            reverse('dashboard:index'),
            reverse('dashboard:atendimentos'),
            reverse('dashboard:produtividade'),
            reverse('dashboard:api_monitor'),
            reverse('dashboard:historico'),
        ]
        for u in urls:
            res = self.client.get(u)
            self.assertEqual(res.status_code, 200, f"Falha ao carregar {u}")
            self.assertContains(res, "ISCON GESTÃO")

        self.assertNotContains(self.client.get(reverse('dashboard:index')), "Swagger API")

    def test_documentacao_dashboard_exibida_somente_para_superuser(self):
        self.client.login(username="gestor_iscon", password="password123")
        response = self.client.get(reverse('dashboard:index'))
        self.assertNotContains(response, "Swagger API")

        root = User.objects.create_superuser(
            username="supervisor_root", password="RootPass123!", email="root@iscon.edu.br"
        )
        self.client.force_login(root)
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, "Swagger API")

    def test_historico_completo_inclui_atendimento_sem_fim(self):
        self.client.login(username="gestor_iscon", password="password123")
        response = self.client.get(reverse('dashboard:historico'), {
            "tabela": "atendimentos", "periodo": "todos", "busca": "Rafael"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['registros'].paginator.count, 1)
        self.assertContains(response, "Rafael")
        self.assertContains(response, "Em Andamento")

    def test_lista_de_atendentes_inclui_nome_historico_fora_das_choices(self):
        Atendimento.objects.create(
            senha=self.senha,
            atendente="Operador legado",
            tipo="matricula",
        )
        self.client.login(username="gestor_iscon", password="password123")
        response = self.client.get(reverse('dashboard:index'))
        self.assertIn("Operador legado", response.context['lista_atendentes'])

    def test_endpoints_api_json_staff(self):
        """Endpoints assíncronos JSON devem retornar HTTP 200 e payload estruturado para staff."""
        self.client.login(username="gestor_iscon", password="password123")

        # KPIs API
        res_kpis = self.client.get(reverse('dashboard:api_kpis'))
        self.assertEqual(res_kpis.status_code, 200)
        data_kpis = res_kpis.json()
        self.assertEqual(data_kpis["status"], "sucesso")
        self.assertIn("kpis", data_kpis["dados"])

        # Charts API
        res_charts = self.client.get(reverse('dashboard:api_charts'))
        self.assertEqual(res_charts.status_code, 200)
        data_charts = res_charts.json()
        self.assertEqual(data_charts["status"], "sucesso")

        # Productivity API
        res_prod = self.client.get(reverse('dashboard:api_productivity'))
        self.assertEqual(res_prod.status_code, 200)
        data_prod = res_prod.json()
        self.assertEqual(data_prod["status"], "sucesso")

        # Live Status API
        res_live = self.client.get(reverse('dashboard:api_live_status'))
        self.assertEqual(res_live.status_code, 200)
        data_live = res_live.json()
        self.assertIn("ao_vivo", data_live)

    def test_endpoints_api_json_bloqueio_anonimo(self):
        """Endpoints assíncronos JSON devem rejeitar anônimos com HTTP 401."""
        res = self.client.get(reverse('dashboard:api_kpis'))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()["codigo"], 401)

    def test_tabela_historico_filtros_e_busca(self):
        """Valida que a página de histórico responde a filtros e buscas."""
        self.client.login(username="gestor_iscon", password="password123")

        # Busca por Rafael
        res = self.client.get(reverse('dashboard:historico') + "?tabela=atendimentos&busca=Rafael")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Rafael")

        # Aba de Senhas
        res_senhas = self.client.get(reverse('dashboard:historico') + "?tabela=senhas")
        self.assertEqual(res_senhas.status_code, 200)
        self.assertContains(res_senhas, "A1")
