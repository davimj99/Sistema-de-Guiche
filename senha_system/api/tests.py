from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Guiche
from filas.models import Senha, Historico


class ApiEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.guiche = Guiche.objects.create(nome="Guichê 01 Teste", ativo=True)
        self.senha_normal = Senha.objects.create(
            prefixo="A",
            numero=1,
            tipo="normal",
            status="espera"
        )
        self.senha_pref = Senha.objects.create(
            prefixo="P",
            numero=1,
            tipo="preferencial",
            status="chamando",
            guiche=self.guiche
        )
        self.historico = Historico.objects.create(
            senha=self.senha_pref,
            guiche=self.guiche,
            acao="chamando"
        )
        # Usuário para testes de autenticação JWT
        self.jwt_user = User.objects.create_user(
            username="api_test_user",
            password="ApiPassword123!",
            email="api_user@iscon.edu.br"
        )

    def test_api_root(self):
        response = self.client.get(reverse("api:root"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["versao"], "v1.0")
        self.assertIn("endpoints", data)

    def test_guiches_api(self):
        response = self.client.get(reverse("api:guiches"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertGreaterEqual(data["total"], 1)
        nomes = [g["nome"] for g in data["guiches"]]
        self.assertIn("Guichê 01 Teste", nomes)

    def test_status_fila_api(self):
        response = self.client.get(reverse("api:status_filas"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertIn("em_espera", data)
        self.assertEqual(data["em_espera"]["normal"], 1)
        self.assertEqual(data["chamando"], 1)

    def test_painel_api(self):
        response = self.client.get(reverse("api:painel"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertIsNotNone(data["ultima"])
        self.assertEqual(data["ultima"]["senha"], "P1")
        self.assertEqual(data["ultima"]["guiche"], "Guichê 01 Teste")

    def test_method_not_allowed_on_post(self):
        response = self.client.post(reverse("api:painel"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 405)

    # ============================================================
    # TESTES DE SWAGGER E OPENAPI
    # ============================================================
    def test_swagger_ui_endpoint(self):
        response = self.client.get("/swagger/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger", response.content.decode("utf-8").lower())

    def test_redoc_endpoint(self):
        response = self.client.get("/redoc/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertIn("redoc", response.content.decode("utf-8").lower())

    def test_swagger_schema_json(self):
        response = self.client.get("/swagger.json", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("swagger", data)
        self.assertEqual(data["swagger"], "2.0")
        self.assertIn("paths", data)
        self.assertIn("/api/v1/painel/", data["paths"])
        self.assertIn("/api/v1/guiches/", data["paths"])
        self.assertIn("/api/v1/filas/status/", data["paths"])

    # ============================================================
    # TESTES DE AUTENTICAÇÃO JWT
    # ============================================================
    def test_jwt_token_obtain_and_refresh(self):
        # 1. Obter tokens de acesso e refresh
        obtain_response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": "api_test_user", "password": "ApiPassword123!"},
            content_type="application/json",
            HTTP_HOST="localhost"
        )
        self.assertEqual(obtain_response.status_code, 200)
        tokens = obtain_response.json()
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

        # 2. Renovar token de acesso usando o refresh token
        refresh_response = self.client.post(
            reverse("api:token_refresh"),
            {"refresh": tokens["refresh"]},
            content_type="application/json",
            HTTP_HOST="localhost"
        )
        self.assertEqual(refresh_response.status_code, 200)
        refresh_data = refresh_response.json()
        self.assertIn("access", refresh_data)

    def test_jwt_protected_profile_endpoint(self):
        # 1. Sem token: retorna 401 Unauthorized
        unauth_response = self.client.get(reverse("api:user_profile"), HTTP_HOST="localhost")
        self.assertEqual(unauth_response.status_code, 401)

        # 2. Obter token
        token_resp = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": "api_test_user", "password": "ApiPassword123!"},
            content_type="application/json",
            HTTP_HOST="localhost"
        )
        access_token = token_resp.json()["access"]

        # 3. Com token válido: retorna 200 com os dados do usuário
        auth_response = self.client.get(
            reverse("api:user_profile"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            HTTP_HOST="localhost"
        )
        self.assertEqual(auth_response.status_code, 200)
        profile_data = auth_response.json()
        self.assertEqual(profile_data["username"], "api_test_user")
        self.assertEqual(profile_data["email"], "api_user@iscon.edu.br")
