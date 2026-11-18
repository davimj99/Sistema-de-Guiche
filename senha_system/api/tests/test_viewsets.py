import base64
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Guiche


class RoutersAndViewSetsTestCase(TestCase):
    """
    Testes de roteamento DRF, ViewSets e manipulação centralizada de exceções.
    """

    def setUp(self):
        self.client = APIClient()
        self.guiche1 = Guiche.objects.create(nome="Guichê 01 Router", ativo=True)
        self.guiche2 = Guiche.objects.create(nome="Guichê 02 Router", ativo=True)
        self.user = User.objects.create_user(
            username="operador_router",
            password="RouterPass2026!",
            email="router@iscon.edu.br"
        )
        creds = "operador_router:RouterPass2026!"
        self.auth_header = "Basic " + base64.b64encode(creds.encode()).decode("utf-8")

    def test_emitir_senha_publica_via_router(self):
        url = "/api/v1/senhas/emitir/"
        response = self.client.post(url, {"tipo": "normal"}, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertEqual(data["senha"]["tipo"], "normal")
        self.assertEqual(data["senha"]["prefixo"], "A")

    def test_chamar_proxima_exige_autenticacao(self):
        url = "/api/v1/senhas/chamar_proxima/"
        unauth_resp = self.client.post(url, {"guiche_id": self.guiche1.id}, format="json")
        self.assertEqual(unauth_resp.status_code, 401)

        self.client.post("/api/v1/senhas/emitir/", {"tipo": "normal"}, format="json")

        auth_resp = self.client.post(
            url,
            {"guiche_id": self.guiche1.id},
            format="json",
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(auth_resp.status_code, 200)
        data = auth_resp.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertIsNotNone(data["senha"])

    def test_atendimentos_viewset_protegido(self):
        list_resp = self.client.get("/api/v1/atendimentos/")
        self.assertEqual(list_resp.status_code, 401)

        auth_list = self.client.get("/api/v1/atendimentos/", HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(auth_list.status_code, 200)

    def test_custom_exception_handler_format(self):
        response = self.client.post(
            "/api/v1/senhas/emitir/",
            {"tipo": "invalido_desconhecido"},
            format="json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "erro")
        self.assertEqual(data["codigo"], 400)
        self.assertIn("mensagem", data)
        self.assertIn("detalhes", data)
