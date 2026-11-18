from datetime import datetime, time

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.utils import timezone

from accounts.models import Guiche
from filas.models import Senha
from .models import Atendimento


class AtendimentoReportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("relatorio", password="SenhaSegura123!")
        permission = Permission.objects.get(codename="view_atendimento")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.guiche = Guiche.objects.create(nome="Guichê relatório")
        self.senha = Senha.objects.create(prefixo="A", numero=101, status="finalizado")
        Atendimento.objects.create(
            senha=self.senha,
            atendente="Alessandra",
            guiche=self.guiche.id,
            tipo="matricula",
            inicio=time(9, 0),
            fim=timezone.make_aware(datetime(2026, 11, 10, 10, 0)),
        )
        self.senha_sem_atendente = Senha.objects.create(prefixo="B", numero=202, status="atendimento")
        Atendimento.objects.create(
            senha=self.senha_sem_atendente,
            atendente=None,
            guiche=None,
            tipo="financeiro",
            fim=timezone.make_aware(datetime(2026, 11, 12, 11, 0)),
        )

    def test_filters_cover_date_attendant_gauge_category_status_and_ticket(self):
        response = self.client.get("/atendimentos/relatorio/", {
            "data_inicio": "2026-11-10",
            "data_fim": "2026-11-10",
            "atendente": "aless",
            "guiche": str(self.guiche.id),
            "categoria": "matricula",
            "status": "finalizado",
            "senha": "101",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pagina"].paginator.count, 1)
        self.assertEqual(response.context["atendimentos"][0].atendente, "Alessandra")

    def test_null_attendant_and_gauge_are_kept_in_complete_history(self):
        response = self.client.get("/atendimentos/relatorio/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pagina"].paginator.count, 2)
        self.assertTrue(any(item.atendente is None and item.guiche is None for item in response.context["atendimentos"]))

    def test_invalid_date_is_reported_without_crashing(self):
        response = self.client.get("/atendimentos/relatorio/", {"data_inicio": "data-invalida"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["erro_filtro"])
        self.assertEqual(response.context["pagina"].paginator.count, 0)

    def test_user_without_report_permission_is_forbidden(self):
        self.client.force_login(User.objects.create_user("sem_permissao", password="SenhaSegura123!"))
        self.assertEqual(self.client.get("/atendimentos/relatorio/").status_code, 403)
