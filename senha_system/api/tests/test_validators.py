from django.test import TestCase
from rest_framework.exceptions import ValidationError

from accounts.models import Guiche
from filas.models import Senha
from filas.validators import FilaValidator, SenhaValidator
from atendimentos.validators import AtendimentoValidator


class ValidatorsTestCase(TestCase):
    """
    Testes unitários dos validadores de domínio (Fila, Senha, Atendimento).
    """

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
