from typing import Optional
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from atendimentos.models import Atendimento
from atendimentos.validators import AtendimentoValidator
from accounts.models import Guiche
from filas.models import Senha, Historico
from filas.validators import FilaValidator, SenhaValidator


class AtendimentoService:
    """
    Service centralizador das regras de negócio de Atendimentos.
    Gerencia início, finalização, transferências entre guichês e auditoria via Histórico.
    """

    @classmethod
    @transaction.atomic
    def iniciar_atendimento(
        cls,
        senha_id: int,
        guiche_id: int,
        atendente: Optional[str] = None,
        aluno: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> Atendimento:
        """
        Inicia o atendimento formal de uma senha chamada em determinado guichê.
        Atualiza o status da senha para 'atendimento' e registra o horário inicial.
        """
        guiche = FilaValidator.validar_guiche_ativo(guiche_id)

        try:
            senha = Senha.objects.select_for_update().get(id=senha_id)
        except Senha.DoesNotExist:
            raise ValidationError({"senha_id": f"Senha #{senha_id} não encontrada."})

        # Validações de integridade
        AtendimentoValidator.validar_senha_para_atendimento(senha)
        if tipo:
            tipo = AtendimentoValidator.validar_tipo_atendimento(tipo)

        # Atualiza a senha
        senha.status = "atendimento"
        senha.guiche = guiche
        senha.save(update_fields=["status", "guiche"])

        # Cria registro do atendimento
        hora_inicio = timezone.localtime().time()
        atendimento = Atendimento.objects.create(
            atendente=atendente,
            aluno=aluno,
            guiche=guiche.id,
            senha=senha,
            tipo=tipo,
            inicio=hora_inicio,
        )

        Historico.objects.create(
            senha=senha,
            guiche=guiche,
            acao="atendimento"
        )

        return atendimento

    @classmethod
    @transaction.atomic
    def finalizar_atendimento(cls, atendimento_id: int) -> Atendimento:
        """
        Finaliza um atendimento em andamento.
        Registra data/hora final e atualiza a senha vinculada para status 'finalizado'.
        """
        try:
            atendimento = Atendimento.objects.select_for_update().get(id=atendimento_id)
        except Atendimento.DoesNotExist:
            raise ValidationError({"atendimento_id": f"Atendimento #{atendimento_id} não encontrado."})

        AtendimentoValidator.validar_encerramento(atendimento)

        agora = timezone.now()
        atendimento.fim = agora
        atendimento.save(update_fields=["fim"])

        senha = atendimento.senha
        if senha:
            senha.status = "finalizado"
            senha.save(update_fields=["status"])

            guiche = None
            if atendimento.guiche:
                guiche = Guiche.objects.filter(id=atendimento.guiche).first()

            Historico.objects.create(
                senha=senha,
                guiche=guiche,
                acao="finalizado"
            )

        return atendimento

    @classmethod
    @transaction.atomic
    def transferir_atendimento(
        cls,
        senha_id: int,
        guiche_origem_id: int,
        guiche_destino_id: int,
        motivo: Optional[str] = None
    ) -> Senha:
        """
        Transfere uma senha em atendimento de um guichê para outro.
        Garante a validação do guichê destino e registro da ação no histórico.
        """
        guiche_destino = AtendimentoValidator.validar_transferencia(
            guiche_origem_id,
            guiche_destino_id
        )

        try:
            senha = Senha.objects.select_for_update().get(id=senha_id)
        except Senha.DoesNotExist:
            raise ValidationError({"senha_id": f"Senha #{senha_id} não encontrada."})

        senha.guiche = guiche_destino
        senha.status = "chamando"
        senha.save(update_fields=["guiche", "status"])

        Historico.objects.create(
            senha=senha,
            guiche=guiche_destino,
            acao=f"transferido_guiche_{guiche_origem_id}_para_{guiche_destino_id}"
        )

        return senha
