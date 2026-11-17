from rest_framework.exceptions import ValidationError
from accounts.models import Guiche


class FilaValidator:
    """
    Validador responsável por regras de integridade e operação da Fila e Guichês.
    """

    TIPOS_PERMITIDOS = ("normal", "preferencial")

    @classmethod
    def validar_tipo_fila(cls, tipo: str) -> str:
        """
        Valida se o tipo de atendimento/fila informado é suportado pelo sistema.
        """
        if not tipo or not isinstance(tipo, str):
            raise ValidationError({"tipo": "O tipo de fila é obrigatório e deve ser um texto."})
        
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado not in cls.TIPOS_PERMITIDOS:
            raise ValidationError({
                "tipo": f"Tipo de fila '{tipo}' inválido. Tipos permitidos: {', '.join(cls.TIPOS_PERMITIDOS)}."
            })
        return tipo_normalizado

    @classmethod
    def validar_guiche_ativo(cls, guiche_id: int) -> Guiche:
        """
        Valida se o guichê existe e se está ativo para realizar operações de chamada/atendimento.
        """
        if not guiche_id:
            raise ValidationError({"guiche_id": "O identificador do guichê é obrigatório."})

        try:
            guiche = Guiche.objects.get(id=guiche_id)
        except Guiche.DoesNotExist:
            raise ValidationError({"guiche_id": f"Guichê com ID {guiche_id} não foi encontrado."})

        if not guiche.ativo:
            raise ValidationError({"guiche_id": f"O guichê '{guiche.nome}' está inativo no momento."})

        return guiche
