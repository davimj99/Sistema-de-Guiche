from rest_framework.exceptions import ValidationError
from atendimentos.models import Atendimento
from accounts.models import Guiche
from filas.models import Senha


class AtendimentoValidator:
    """
    Validador responsável pelas regras de integridade do registro e ciclo de vida do Atendimento.
    """

    @classmethod
    def validar_tipo_atendimento(cls, tipo: str) -> str:
        """
        Valida se o tipo de atendimento está cadastrado nas opções válidas do modelo.
        """
        if not tipo:
            return tipo

        tipos_validos = dict(Atendimento.TIPOS_ATENDIMENTO).keys()
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado not in tipos_validos:
            raise ValidationError({
                "tipo": f"Tipo de atendimento '{tipo}' inválido. Opções válidas: {', '.join(tipos_validos)}."
            })
        return tipo_normalizado

    @classmethod
    def validar_senha_para_atendimento(cls, senha: Senha) -> None:
        """
        Garante que a senha está apta a iniciar um atendimento (status chamando ou em atendimento).
        """
        if senha.status not in ["chamando", "chamando_novamente", "atendimento"]:
            raise ValidationError({
                "senha": f"A senha {senha.prefixo}{senha.numero} não pode iniciar atendimento pois seu status é '{senha.status}'."
            })

    @classmethod
    def validar_encerramento(cls, atendimento: Atendimento) -> None:
        """
        Garante que um atendimento não seja encerrado mais de uma vez.
        """
        if atendimento.fim is not None:
            raise ValidationError({
                "atendimento": f"O atendimento #{atendimento.id} já foi encerrado em {atendimento.fim}."
            })

    @classmethod
    def validar_transferencia(cls, guiche_origem_id: int, guiche_destino_id: int) -> Guiche:
        """
        Valida os guichês na transferência de atendimento.
        """
        if guiche_origem_id == guiche_destino_id:
            raise ValidationError({
                "guiche_destino": "O guichê de destino deve ser diferente do guichê de origem."
            })

        try:
            destino = Guiche.objects.get(id=guiche_destino_id)
        except Guiche.DoesNotExist:
            raise ValidationError({
                "guiche_destino": f"Guichê de destino ID {guiche_destino_id} não encontrado."
            })

        if not destino.ativo:
            raise ValidationError({
                "guiche_destino": f"O guichê de destino '{destino.nome}' está inativo."
            })

        return destino
