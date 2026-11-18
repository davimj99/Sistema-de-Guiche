import re
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from accounts.models import Guiche


class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "operador_teste"
        self.password = "SenhaSegura123!"
        self.email = "operador@iscon.edu.br"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )
        self.guiche = Guiche.objects.create(nome="Guichê 01 Central", ativo=True)

    def test_login_page_renders_successfully(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Acesso ao Sistema")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_login_successful_redirects_to_default(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("core:index"))
        # Verifica se o cliente de teste está autenticado
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_with_invalid_credentials_fails(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.username, "password": "SenhaErrada999!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertContains(response, "Usuário ou senha incorretos")

    def test_login_protected_view_redirects_and_preserves_next(self):
        protected_url = f"/filas/guiche/{self.guiche.id}/"
        response = self.client.get(protected_url)
        # Redireciona para login com parâmetro next
        expected_redirect = f"{reverse('accounts:login')}?next={protected_url}"
        self.assertRedirects(response, expected_redirect)

        # Agora realiza o login informando o next
        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.username,
                "password": self.password,
                "next": protected_url,
            },
        )
        # Deve redirecionar diretamente para a view protegida solicitada
        self.assertRedirects(login_response, protected_url)

    def test_logout_invalidates_session(self):
        # Primeiro realiza o login
        self.client.login(username=self.username, password=self.password)
        self.assertTrue("_auth_user_id" in self.client.session)

        # Realiza logout seguro via POST
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_password_reset_complete_flow(self):
        # 1. Solicitação de redefinição
        reset_response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": self.email},
        )
        self.assertRedirects(reset_response, reverse("accounts:password_reset_done"))

        # 2. Verifica se o e-mail foi disparado
        self.assertEqual(len(mail.outbox), 1)
        email_sent = mail.outbox[0]
        self.assertIn(self.email, email_sent.to)
        self.assertIn("Redefinição de senha", email_sent.subject)

        # 3. Extrai uidb64 e token do corpo do e-mail
        email_body = email_sent.body
        match = re.search(r"password-reset-confirm/([^/]+)/([^/]+)/", email_body)
        self.assertIsNotNone(match, "Token ou UID não encontrados no corpo do e-mail")
        uidb64, token = match.group(1), match.group(2)

        # 4. Acessa a tela de confirmação (Django redireciona para a URL sem o token por segurança contra vazamento em Referer)
        confirm_url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": uidb64, "token": token},
        )
        get_confirm = self.client.get(confirm_url, follow=True)
        self.assertEqual(get_confirm.status_code, 200)
        self.assertContains(get_confirm, "Definir Nova Senha")

        # 5. Define a nova senha
        new_password = "NovaSenhaForte456#"
        final_confirm_url = get_confirm.redirect_chain[-1][0] if get_confirm.redirect_chain else confirm_url
        post_confirm = self.client.post(
            final_confirm_url,
            {
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )
        self.assertRedirects(post_confirm, reverse("accounts:password_reset_complete"))

        # 6. Valida que a senha antiga não funciona e a nova funciona
        old_login = self.client.login(username=self.username, password=self.password)
        self.assertFalse(old_login)

        new_login = self.client.login(username=self.username, password=new_password)
        self.assertTrue(new_login)

    def test_password_reset_invalid_token(self):
        # Acesso com token adulterado/inválido
        invalid_url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": "invalid-uid", "token": "invalid-token"},
        )
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Link Inválido ou Expirado")

    def test_public_interfaces_remain_accessible_without_auth(self):
        # Validação de que fluxos públicos não foram quebrados
        public_urls = [
            reverse("core:index"),
            "/filas/totem/",
            "/filas/gerar/",
            "/painel/",
        ]
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                200,
                f"Interface pública {url} deveria retornar 200, retornou {response.status_code}",
            )
