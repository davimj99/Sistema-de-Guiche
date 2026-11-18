import base64
from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Guiche
from filas.models import Senha
from atendimentos.models import Atendimento


class ListFilteringTestCase(TestCase):
    """
    Testes automatizados para a funcionalidade de filtragem, busca e ordenação
    de listas via Django REST Framework nos ViewSets de Guichês, Senhas e Atendimentos.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="operador_filtros",
            password="FiltrosPass2026!",
            email="filtros@iscon.edu.br"
        )
        creds = "operador_filtros:FiltrosPass2026!"
        self.auth_header = "Basic " + base64.b64encode(creds.encode()).decode("utf-8")

        # 1. Guichês para teste de filtros
        self.g1 = Guiche.objects.create(nome="Guichê Financeiro Alfa", ativo=True)
        self.g2 = Guiche.objects.create(nome="Guichê Secretaria Beta", ativo=False)
        self.g3 = Guiche.objects.create(nome="Guichê Atendimento Geral", ativo=True)

        # 2. Senhas para teste de filtros
        self.s1 = Senha.objects.create(prefixo="A", numero=10, tipo="normal", status="espera")
        self.s2 = Senha.objects.create(prefixo="P", numero=11, tipo="preferencial", status="chamando", guiche=self.g1)
        self.s3 = Senha.objects.create(prefixo="A", numero=12, tipo="normal", status="finalizado", guiche=self.g1)

        # 3. Atendimentos para teste de filtros
        self.a1 = Atendimento.objects.create(
            senha=self.s2,
            guiche=1,
            atendente="Rafael",
            aluno="Carlos Eduardo",
            tipo="matricula",
            fim=None
        )
        self.a2 = Atendimento.objects.create(
            senha=self.s3,
            guiche=2,
            atendente="Alessandra",
            aluno="Mariana Souza",
            tipo="financeiro",
            fim=timezone.now()
        )

    # ============================================================
    # FILTRAGEM DE GUICHÊS
    # ============================================================
    def test_filter_guiches_by_ativo(self):
        # Apenas ativos
        resp_ativos = self.client.get("/api/v1/guiches/?ativo=true")
        self.assertEqual(resp_ativos.status_code, 200)
        data_ativos = resp_ativos.json()["guiches"]
        self.assertTrue(all(g["ativo"] is True for g in data_ativos))
        nomes_ativos = [g["nome"] for g in data_ativos]
        self.assertIn("Guichê Financeiro Alfa", nomes_ativos)
        self.assertNotIn("Guichê Secretaria Beta", nomes_ativos)

        # Apenas inativos
        resp_inativos = self.client.get("/api/v1/guiches/?ativo=false")
        self.assertEqual(resp_inativos.status_code, 200)
        data_inativos = resp_inativos.json()["guiches"]
        self.assertEqual(len(data_inativos), 1)
        self.assertEqual(data_inativos[0]["nome"], "Guichê Secretaria Beta")

    def test_filter_guiches_by_search_and_ordering(self):
        # Busca textual
        resp_search = self.client.get("/api/v1/guiches/?search=Secretaria")
        self.assertEqual(resp_search.status_code, 200)
        nomes = [g["nome"] for g in resp_search.json()["guiches"]]
        self.assertEqual(len(nomes), 1)
        self.assertEqual(nomes[0], "Guichê Secretaria Beta")

        # Ordenação descendente por nome
        resp_ord = self.client.get("/api/v1/guiches/?ordering=-nome")
        self.assertEqual(resp_ord.status_code, 200)
        nomes_ord = [g["nome"] for g in resp_ord.json()["guiches"]]
        self.assertEqual(nomes_ord, sorted(nomes_ord, reverse=True))

    # ============================================================
    # FILTRAGEM DE SENHAS
    # ============================================================
    def test_filter_senhas_by_status(self):
        resp_espera = self.client.get("/api/v1/senhas/?status=espera")
        self.assertEqual(resp_espera.status_code, 200)
        senhas_espera = resp_espera.json()
        self.assertEqual(len(senhas_espera), 1)
        self.assertEqual(senhas_espera[0]["status"], "espera")
        self.assertEqual(senhas_espera[0]["prefixo"], "A")

        resp_chamando = self.client.get("/api/v1/senhas/?status=chamando")
        self.assertEqual(resp_chamando.status_code, 200)
        senhas_chamando = resp_chamando.json()
        self.assertEqual(len(senhas_chamando), 1)
        self.assertEqual(senhas_chamando[0]["status"], "chamando")

    def test_filter_senhas_by_tipo_and_guiche(self):
        # Filtro por tipo preferencial
        resp_pref = self.client.get("/api/v1/senhas/?tipo=preferencial")
        self.assertEqual(resp_pref.status_code, 200)
        self.assertTrue(all(s["tipo"] == "preferencial" for s in resp_pref.json()))

        # Filtro por guichê associado
        resp_g1 = self.client.get(f"/api/v1/senhas/?guiche={self.g1.id}")
        self.assertEqual(resp_g1.status_code, 200)
        self.assertTrue(len(resp_g1.json()) >= 2)

    def test_filter_senhas_hoje_and_ordering(self):
        # Filtro hoje=true
        resp_hoje = self.client.get("/api/v1/senhas/?hoje=true")
        self.assertEqual(resp_hoje.status_code, 200)
        self.assertEqual(len(resp_hoje.json()), 3)

        # Ordenação por número crescente
        resp_ord = self.client.get("/api/v1/senhas/?ordering=numero")
        self.assertEqual(resp_ord.status_code, 200)
        numeros = [s["numero"] for s in resp_ord.json()]
        self.assertEqual(numeros, sorted(numeros))

    # ============================================================
    # FILTRAGEM DE ATENDIMENTOS
    # ============================================================
    def test_filter_atendimentos_by_tipo(self):
        resp = self.client.get(
            "/api/v1/atendimentos/?tipo=matricula",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["tipo"], "matricula")
        self.assertEqual(data[0]["aluno"], "Carlos Eduardo")

    def test_filter_atendimentos_by_atendente_and_search(self):
        # Filtro exato/parcial por atendente
        resp = self.client.get(
            "/api/v1/atendimentos/?atendente=Alessandra",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["atendente"], "Alessandra")

        # Busca textual DRF por nome do aluno
        resp_search = self.client.get(
            "/api/v1/atendimentos/?search=Mariana",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(resp_search.status_code, 200)
        self.assertEqual(len(resp_search.json()), 1)
        self.assertEqual(resp_search.json()[0]["aluno"], "Mariana Souza")

    def test_filter_atendimentos_by_finalizado(self):
        # Em andamento (finalizado=false)
        resp_andamento = self.client.get(
            "/api/v1/atendimentos/?finalizado=false",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(resp_andamento.status_code, 200)
        data_andamento = resp_andamento.json()
        self.assertEqual(len(data_andamento), 1)
        self.assertIsNone(data_andamento[0]["fim"])

        # Finalizado (finalizado=true)
        resp_concluido = self.client.get(
            "/api/v1/atendimentos/?finalizado=true",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(resp_concluido.status_code, 200)
        data_concluido = resp_concluido.json()
        self.assertEqual(len(data_concluido), 1)
        self.assertIsNotNone(data_concluido[0]["fim"])
