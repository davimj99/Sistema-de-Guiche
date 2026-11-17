import base64
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class BasicAuthenticationTestCase(TestCase):
    """
    Testes de autenticação básica HTTP (RFC 7617) nos endpoints protegidos.
    """

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
