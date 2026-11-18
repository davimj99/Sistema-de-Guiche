from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless

from django.db import connection, connections
from django.test import TransactionTestCase

from accounts.models import Guiche
from filas.models import ControleFila, Historico, Senha
from filas.services import FilaService


@skipUnless(
    connection.vendor == "postgresql",
    "PostgreSQL advisory-lock concurrency coverage requires PostgreSQL.",
)
class QueueConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.guiches = [
            Guiche.objects.create(nome=f"Guichê {index}", ativo=True)
            for index in range(1, 5)
        ]

    @staticmethod
    def _emit_one():
        connections.close_all()
        try:
            return FilaService.emitir_senha("normal").numero
        finally:
            connections.close_all()

    def test_concurrent_first_issuances_receive_unique_numbers(self):
        with ThreadPoolExecutor(max_workers=8) as executor:
            numeros = list(executor.map(lambda _: self._emit_one(), range(16)))

        self.assertEqual(sorted(numeros), list(range(1, 17)))
        self.assertEqual(
            Senha.objects.filter(tipo="normal").values("numero").distinct().count(),
            16,
        )

    def test_concurrent_calls_assign_each_waiting_ticket_once(self):
        senhas = [FilaService.emitir_senha("normal") for _ in range(12)]
        guiche_ids = [guiche.id for guiche in self.guiches]

        def chamar(index):
            connections.close_all()
            try:
                senha = FilaService.chamar_proxima(guiche_ids[index % len(guiche_ids)])
                return senha.id if senha else None
            finally:
                connections.close_all()

        # Exercise simultaneous first-time creation of the control row as well.
        self.assertFalse(ControleFila.objects.exists())
        with ThreadPoolExecutor(max_workers=8) as executor:
            chamadas = list(executor.map(chamar, range(len(senhas))))

        self.assertEqual(len(set(chamadas)), len(senhas))
        self.assertEqual(set(chamadas), {senha.id for senha in senhas})
        self.assertEqual(
            Historico.objects.filter(senha_id__in=chamadas, acao="chamando").count(),
            len(senhas),
        )
