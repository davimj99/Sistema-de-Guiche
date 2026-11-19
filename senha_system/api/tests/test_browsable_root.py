import base64
from django.test import Client, TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Guiche


class InteractiveApiRootTestCase(TestCase):
    """
    Testes da API Root Interativa e navegabilidade completa na Browsable API do DRF.
    """

    def setUp(self):
        self.client = APIClient()
        self.guiche = Guiche.objects.create(nome="Guichê 01 Interativo", ativo=True)
        self.user = User.objects.create_user(
            username="operador_interativo",
            password="InterativoPass2026!",
            email="interativo@iscon.edu.br"
        )
        self.staff_user = User.objects.create_user(
            username="admin_interativo",
            password="AdminPass2026!",
            email="admin@iscon.edu.br",
            is_staff=True
        )
        creds = "operador_interativo:InterativoPass2026!"
        self.auth_header = "Basic " + base64.b64encode(creds.encode()).decode("utf-8")
        staff_creds = "admin_interativo:AdminPass2026!"
        self.staff_header = "Basic " + base64.b64encode(staff_creds.encode()).decode("utf-8")

    def test_api_root_returns_200_and_interactive_hyperlinks(self):
        response = self.client.get("/api/v1/", HTTP_HOST="localhost:8000")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["nome"], "API Sistema de Atendimento & Filas")
        self.assertEqual(data["versao"], "v1.0")
        self.assertIn("endpoints", data)

        endpoints = data["endpoints"]
        for key in ["painel", "guiches", "filas", "senhas", "atendimentos"]:
            self.assertIn(key, endpoints)
            url = endpoints[key]
            self.assertTrue(url.startswith("http://") or url.startswith("https://"))
            self.assertIn("/api/v1/", url)
        self.assertNotIn("swagger", endpoints)
        self.assertNotIn("redoc", endpoints)

    def test_documentation_links_are_only_listed_for_superuser(self):
        root = User.objects.create_superuser(
            username="root_docs", password="RootPass123!", email="root@iscon.edu.br"
        )
        self.client.force_authenticate(user=root)
        endpoints = self.client.get("/api/v1/", HTTP_HOST="localhost:8000").json()["endpoints"]
        self.assertIn("swagger", endpoints)
        self.assertIn("redoc", endpoints)

    def test_browsable_api_html_contains_clickable_anchors(self):
        response = self.client.get("/api/v1/", HTTP_ACCEPT="text/html", HTTP_HOST="localhost:8000")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        self.assertIn('href="http://localhost:8000/api/v1/painel/"', html)
        self.assertIn('href="http://localhost:8000/api/v1/guiches/"', html)
        self.assertIn('href="http://localhost:8000/api/v1/filas/"', html)
        self.assertIn('href="http://localhost:8000/api/v1/senhas/"', html)
        self.assertIn('href="http://localhost:8000/api/v1/atendimentos/"', html)

    def test_all_root_hyperlinks_resolve_without_404(self):
        response = self.client.get("/api/v1/", HTTP_HOST="localhost:8000")
        endpoints = response.json()["endpoints"]

        for name, full_url in endpoints.items():
            path = full_url.replace("http://localhost:8000", "")
            get_resp = self.client.get(path, HTTP_HOST="localhost:8000")
            self.assertNotEqual(
                get_resp.status_code,
                404,
                f"Endpoint '{name}' ({path}) retornou 404 Not Found"
            )
            self.assertIn(
                get_resp.status_code,
                [200, 401, 403, 405],
                f"Endpoint '{name}' ({path}) retornou status inesperado {get_resp.status_code}"
            )

    def test_hyperlinked_serializers_in_responses(self):
        guiches_resp = self.client.get("/api/v1/guiches/", HTTP_HOST="localhost:8000")
        self.assertEqual(guiches_resp.status_code, 200)
        guiches_data = guiches_resp.json()
        self.assertTrue(len(guiches_data["guiches"]) > 0)
        primeiro_guiche = guiches_data["guiches"][0]
        self.assertIn("url", primeiro_guiche)
        self.assertTrue(primeiro_guiche["url"].startswith("http://localhost:8000/api/v1/guiches/"))

        emitir_resp = self.client.post("/api/v1/senhas/emitir/", {"tipo": "normal"}, format="json", HTTP_HOST="localhost:8000")
        self.assertEqual(emitir_resp.status_code, 201)
        senha_data = emitir_resp.json()["senha"]
        self.assertIn("url", senha_data)
        self.assertTrue(senha_data["url"].startswith("http://localhost:8000/api/v1/senhas/"))

    def test_action_endpoints_support_get_and_display_forms(self):
        emitir_get = self.client.get("/api/v1/senhas/emitir/", HTTP_HOST="localhost:8000")
        self.assertEqual(emitir_get.status_code, 200)
        self.assertIn("tipos_suportados", emitir_get.json())

        chamar_get = self.client.get(
            "/api/v1/senhas/chamar_proxima/",
            HTTP_AUTHORIZATION=self.auth_header,
            HTTP_HOST="localhost:8000"
        )
        self.assertEqual(chamar_get.status_code, 200)
        self.assertIn("guiches_ativos", chamar_get.json())

        iniciar_get = self.client.get(
            "/api/v1/atendimentos/iniciar/",
            HTTP_AUTHORIZATION=self.auth_header,
            HTTP_HOST="localhost:8000"
        )
        self.assertEqual(iniciar_get.status_code, 200)
        self.assertIn("tipos_atendimento", iniciar_get.json())

    def test_guiche_crud_and_permissions(self):
        post_unauth = self.client.post(
            "/api/v1/guiches/",
            {"nome": "Guichê Não Permitido", "ativo": True},
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
            HTTP_HOST="localhost:8000"
        )
        self.assertEqual(post_unauth.status_code, 403)

        post_staff = self.client.post(
            "/api/v1/guiches/",
            {"nome": "Guichê Novo Staff", "ativo": True},
            format="json",
            HTTP_AUTHORIZATION=self.staff_header,
            HTTP_HOST="localhost:8000"
        )
        self.assertEqual(post_staff.status_code, 201)
        novo_id = post_staff.json()["id"]

        detail_resp = self.client.get(f"/api/v1/guiches/{novo_id}/", HTTP_HOST="localhost:8000")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["nome"], "Guichê Novo Staff")


class BrowsableApiSessionAuthTestCase(TestCase):
    """Login/logout controls on the API Root use Django's session auth safely."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.first_user = User.objects.create_user(
            username="root_login_um", password="SenhaUm2026!"
        )
        self.second_user = User.objects.create_user(
            username="root_login_dois", password="SenhaDois2026!"
        )

    def test_anonymous_root_displays_login(self):
        response = self.client.get("/api/v1/", HTTP_ACCEPT="text/html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Login</a>")
        self.assertNotContains(response, ">Sair</button>")

    def test_login_failure_and_success_from_browsable_api(self):
        login_url = "/api-auth/login/"
        self.client.get(login_url)
        csrf_token = self.client.cookies["csrftoken"].value

        invalid = self.client.post(login_url, {
            "username": self.first_user.username,
            "password": "senha-incorreta",
            "csrfmiddlewaretoken": csrf_token,
            "next": "/api/v1/",
        })
        self.assertEqual(invalid.status_code, 200)
        self.assertFalse("_auth_user_id" in self.client.session)

        self.client.get(login_url)
        csrf_token = self.client.cookies["csrftoken"].value
        valid = self.client.post(login_url, {
            "username": self.first_user.username,
            "password": "SenhaUm2026!",
            "csrfmiddlewaretoken": csrf_token,
            "next": "/api/v1/",
        })
        self.assertRedirects(valid, "/api/v1/", fetch_redirect_response=False)

        root = self.client.get("/api/v1/", HTTP_ACCEPT="text/html")
        self.assertContains(root, "Autenticado: root_login_um")
        self.assertContains(root, ">Sair</button>")

    def test_logout_requires_post_and_allows_login_as_another_user(self):
        self.client.get("/api-auth/login/")
        token = self.client.cookies["csrftoken"].value
        login = self.client.post("/api-auth/login/", {
            "username": self.first_user.username,
            "password": "SenhaUm2026!",
            "csrfmiddlewaretoken": token,
            "next": "/api/v1/",
        })
        self.assertRedirects(login, "/api/v1/", fetch_redirect_response=False)

        logout_url = "/api-auth/logout/"
        self.assertEqual(self.client.get(logout_url).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

        token = self.client.cookies["csrftoken"].value
        logout = self.client.post(logout_url, {
            "csrfmiddlewaretoken": token,
            "next": "/api/v1/",
        })
        self.assertRedirects(logout, "/api/v1/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

        root = self.client.get("/api/v1/", HTTP_ACCEPT="text/html")
        self.assertContains(root, ">Login</a>")
        self.assertNotContains(root, "Autenticado: root_login_um")

        self.client.get("/api-auth/login/")
        token = self.client.cookies["csrftoken"].value
        relogin = self.client.post("/api-auth/login/", {
            "username": self.second_user.username,
            "password": "SenhaDois2026!",
            "csrfmiddlewaretoken": token,
            "next": "/api/v1/",
        })
        self.assertRedirects(relogin, "/api/v1/", fetch_redirect_response=False)
        self.assertContains(
            self.client.get("/api/v1/", HTTP_ACCEPT="text/html"),
            "Autenticado: root_login_dois",
        )
