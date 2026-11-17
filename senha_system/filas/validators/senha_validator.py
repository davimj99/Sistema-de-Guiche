from django.utils import timezone
from rest_framework.exceptions import ValidationError
from filas.models import Senha


class SenhaValidator:
    """
    Validador com foco no ciclo de vida e transições de estado das Senhas.
    """

    TRANSIÇÕES_PERMITIDAS = {
        "espera": ["chamando", "finalizado"],
        "chamando": ["chamando_novamente", "atendimento", "finalizado"],
        "chamando_novamente": ["chamando_novamente", "atendimento", "finalizado"],
        "atendimento": ["finalizado"],
        "finalizado": [],  # Estado terminal
    }

    @classmethod
    def validar_transicao_status(cls, senha: Senha, novo_status: str) -> None:
        """
        Garante que a mudança de status da senha respeita a máquina de estados.
        """
        status_atual = senha.status
        permitidos = cls.TRANSIÇÕES_PERMITIDAS.get(status_atual, [])

        if novo_status not in permitidos:
            raise ValidationError({
                "status": (
                    f"Transição inválida de status: de '{status_atual}' para '{novo_status}'. "
                    f"Transições válidas para este estado: {', '.join(permitidos) if permitidos else 'nenhuma (estado terminal)'}."
                )
            })

    @classmethod
    def validar_senha_do_dia(cls, senha: Senha) -> None:
        """
        Impede operações de atendimento/chamada em senhas emitidas em datas anteriores.
        """
        hoje = timezone.localdate()
        if senha.criada_em.date() != hoje:
            raise ValidationError({
                "senha": f"A senha #{senha.id} foi emitida em {senha.criada_em.date()} e não pode ser operada no dia de hoje ({hoje})."
            })

    @classmethod
    def validar_senha_para_chamada(cls, senha: Senha) -> None:
        """
        Verifica se a senha está em condições de ser chamada (em espera ou já em chamada).
        """
        if senha.status not in ["espera", "chamando", "chamando_novamente"]:
            raise ValidationError({
                "senha": f"A senha #{senha.id} não pode ser chamada porque seu status atual é '{senha.status}'."
            })
