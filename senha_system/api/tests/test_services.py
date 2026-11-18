from django.test import TestCase

from accounts.models import Guiche
from filas.models import Historico, ControleFila
from filas.services import FilaService
from atendimentos.services import AtendimentoService


class ServicesTestCase(TestCase):
    """
    Testes dos serviços de regra de negócio de atendimento e emissão de senhas.
    """

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
