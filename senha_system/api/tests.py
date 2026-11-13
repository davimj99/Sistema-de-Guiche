import base64
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from accounts.models import Guiche
from filas.models import Senha, Historico, ControleFila
from atendimentos.models import Atendimento
from filas.validators import FilaValidator, SenhaValidator
from atendimentos.validators import AtendimentoValidator
from filas.services import FilaService
from atendimentos.services import AtendimentoService


# ============================================================
# 1. SUÍTE ORIGINAL DE REGRESSÃO DE ENDPOINTS E JWT
# ============================================================
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
        unauth_response = self.client.get(reverse("api:user_profile"), HTTP_HOST="localhost")
        self.assertEqual(unauth_response.status_code, 401)

        token_resp = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": "api_test_user", "password": "ApiPassword123!"},
            content_type="application/json",
            HTTP_HOST="localhost"
        )
        access_token = token_resp.json()["access"]

        auth_response = self.client.get(
            reverse("api:user_profile"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            HTTP_HOST="localhost"
        )
        self.assertEqual(auth_response.status_code, 200)
        profile_data = auth_response.json()
        self.assertEqual(profile_data["username"], "api_test_user")
        self.assertEqual(profile_data["email"], "api_user@iscon.edu.br")


# ============================================================
# 2. TESTES DE AUTENTICAÇÃO BÁSICA (BasicAuthentication)
# ============================================================
class BasicAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "operador_basic"
        self.password = "BasicPass2026!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="basic@iscon.edu.br"
        )
        credentials = f"{self.username}:{self.password}"
        self.valid_basic_header = "Basic " + base64.b64encode(credentials.encode()).decode("utf-8")

    def test_basic_auth_success(self):
        response = self.client.get(
            reverse("api:user_profile"),
            HTTP_AUTHORIZATION=self.valid_basic_header
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["email"], "basic@iscon.edu.br")

    def test_basic_auth_invalid_password(self):
        invalid_creds = f"{self.username}:senha_incorreta"
        invalid_header = "Basic " + base64.b64encode(invalid_creds.encode()).decode("utf-8")
        response = self.client.get(
            reverse("api:user_profile"),
            HTTP_AUTHORIZATION=invalid_header
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["status"], "erro")
        self.assertEqual(data["codigo"], 401)

    def test_basic_auth_nonexistent_user(self):
        creds = "usuario_inexistente:senha123"
        header = "Basic " + base64.b64encode(creds.encode()).decode("utf-8")
        response = self.client.get(
            reverse("api:user_profile"),
            HTTP_AUTHORIZATION=header
        )
        self.assertEqual(response.status_code, 401)


# ============================================================
# 3. TESTES DE VALIDATORS (Fila, Senha, Atendimento)
# ============================================================
class ValidatorsTestCase(TestCase):
    def setUp(self):
        self.guiche_ativo = Guiche.objects.create(nome="Guichê Ativo", ativo=True)
        self.guiche_inativo = Guiche.objects.create(nome="Guichê Inativo", ativo=False)
        self.senha = Senha.objects.create(numero=1, prefixo="A", tipo="normal", status="espera")

    def test_fila_validator_tipo_valido(self):
        self.assertEqual(FilaValidator.validar_tipo_fila("normal"), "normal")
        self.assertEqual(FilaValidator.validar_tipo_fila("PREFERENCIAL"), "preferencial")

    def test_fila_validator_tipo_invalido_dispara_validation_error(self):
        with self.assertRaises(ValidationError):
            FilaValidator.validar_tipo_fila("vip_invalido")

    def test_fila_validator_guiche_ativo(self):
        valido = FilaValidator.validar_guiche_ativo(self.guiche_ativo.id)
        self.assertEqual(valido.id, self.guiche_ativo.id)

    def test_fila_validator_guiche_inativo_ou_inexistente(self):
        with self.assertRaises(ValidationError):
            FilaValidator.validar_guiche_ativo(self.guiche_inativo.id)
        with self.assertRaises(ValidationError):
            FilaValidator.validar_guiche_ativo(9999)

    def test_senha_validator_transicao_valida_e_invalida(self):
        # Transição válida: espera -> chamando
        SenhaValidator.validar_transicao_status(self.senha, "chamando")
        # Transição inválida: espera -> atendimento direto sem chamar
        with self.assertRaises(ValidationError):
            SenhaValidator.validar_transicao_status(self.senha, "atendimento")

    def test_atendimento_validator_tipo_valido_e_invalido(self):
        self.assertEqual(AtendimentoValidator.validar_tipo_atendimento("matricula"), "matricula")
        with self.assertRaises(ValidationError):
            AtendimentoValidator.validar_tipo_atendimento("tipo_inexistente")

    def test_atendimento_validator_transferencia_mesmo_guiche(self):
        with self.assertRaises(ValidationError):
            AtendimentoValidator.validar_transferencia(
                self.guiche_ativo.id,
                self.guiche_ativo.id
            )


# ============================================================
# 4. TESTES DE SERVICES (FilaService, AtendimentoService)
# ============================================================
class ServicesTestCase(TestCase):
    def setUp(self):
        self.guiche = Guiche.objects.create(nome="Guichê 01", ativo=True)
        ControleFila.objects.create(contador=0)

    def test_fila_service_emitir_senha(self):
        senha_norm = FilaService.emitir_senha(tipo="normal")
        self.assertEqual(senha_norm.prefixo, "A")
        self.assertEqual(senha_norm.numero, 1)
        self.assertEqual(senha_norm.tipo, "normal")
        self.assertEqual(senha_norm.status, "espera")

        senha_pref = FilaService.emitir_senha(tipo="preferencial")
        self.assertEqual(senha_pref.prefixo, "P")
        self.assertEqual(senha_pref.numero, 1)

    def test_fila_service_chamar_proxima_com_alternancia(self):
        # Emite 1 normal e 1 preferencial
        s_norm = FilaService.emitir_senha(tipo="normal")
        s_pref = FilaService.emitir_senha(tipo="preferencial")

        # Primeira chamada (contador 0+1=1, 1 % 3 == 1 -> deve priorizar PREFERENCIAL)
        chamada = FilaService.chamar_proxima(guiche_id=self.guiche.id)
        self.assertIsNotNone(chamada)
        self.assertEqual(chamada.id, s_pref.id)
        self.assertEqual(chamada.status, "chamando")
        self.assertEqual(chamada.guiche_id, self.guiche.id)

        # Verifica histórico criado
        self.assertTrue(Historico.objects.filter(senha=chamada, acao="chamando").exists())

    def test_fila_service_chamar_novamente(self):
        FilaService.emitir_senha(tipo="normal")
        chamada = FilaService.chamar_proxima(guiche_id=self.guiche.id)
        rechamada = FilaService.chamar_novamente(guiche_id=self.guiche.id)
        self.assertEqual(rechamada.id, chamada.id)
        self.assertTrue(Historico.objects.filter(senha=chamada, acao="chamando_novamente").exists())

    def test_atendimento_service_ciclo_completo(self):
        # 1. Emite e chama senha
        FilaService.emitir_senha(tipo="normal")
        senha = FilaService.chamar_proxima(guiche_id=self.guiche.id)

        # 2. Inicia atendimento
        atendimento = AtendimentoService.iniciar_atendimento(
            senha_id=senha.id,
            guiche_id=self.guiche.id,
            atendente="Rafael",
            aluno="Aluno Teste",
            tipo="matricula"
        )
        self.assertIsNotNone(atendimento.inicio)
        self.assertIsNone(atendimento.fim)
        senha.refresh_from_db()
        self.assertEqual(senha.status, "atendimento")

        # 3. Finaliza atendimento
        finalizado = AtendimentoService.finalizar_atendimento(atendimento.id)
        self.assertIsNotNone(finalizado.fim)
        senha.refresh_from_db()
        self.assertEqual(senha.status, "finalizado")


# ============================================================
# 5. TESTES DE VIEWSETS E ROUTERS (/api/v1/senhas, /api/v1/atendimentos)
# ============================================================
class RoutersAndViewSetsTestCase(TestCase):
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
        # Sem autenticação -> 401
        unauth_resp = self.client.post(url, {"guiche_id": self.guiche1.id}, format="json")
        self.assertEqual(unauth_resp.status_code, 401)

        # Emite uma senha
        self.client.post("/api/v1/senhas/emitir/", {"tipo": "normal"}, format="json")

        # Com BasicAuthentication -> 200
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
        # 1. Sem credenciais -> 401
        list_resp = self.client.get("/api/v1/atendimentos/")
        self.assertEqual(list_resp.status_code, 401)

        # 2. Com BasicAuthentication -> 200
        auth_list = self.client.get("/api/v1/atendimentos/", HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(auth_list.status_code, 200)

    def test_custom_exception_handler_format(self):
        # Força um 400 Bad Request enviando payload inválido
        response = self.client.post(
            "/api/v1/senhas/emitir/",
            {"tipo": "invalido_desconhecido"},
            format="json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        # Valida padronização do custom exception handler
        self.assertEqual(data["status"], "erro")
        self.assertEqual(data["codigo"], 400)
        self.assertIn("mensagem", data)
        self.assertIn("detalhes", data)
