from rest_framework import serializers
from rest_framework.reverse import reverse
from accounts.models import Guiche
from filas.models import Senha, Historico
from atendimentos.models import Atendimento
from filas.validators import FilaValidator, SenhaValidator
from atendimentos.validators import AtendimentoValidator


# ============================================================
# SERIALIZERS DE GUICHÊ (HYPERLINKED & RETROCOMPATÍVEL)
# ============================================================
class GuicheSerializer(serializers.ModelSerializer):
    """Representação serializada de um Guichê de Atendimento com link navegável."""
    url = serializers.SerializerMethodField(help_text="Hyperlink navegável para o detalhe do guichê.")

    class Meta:
        model = Guiche
        fields = ['id', 'url', 'nome', 'ativo']

    def get_url(self, obj) -> str | None:
        request = self.context.get('request')
        try:
            return reverse('api:guiches-detail', kwargs={'pk': obj.pk}, request=request)
        except Exception:
            return None


class GuichesListResponseSerializer(serializers.Serializer):
    """Resposta com lista de guichês ativos para o totem e painéis."""
    status = serializers.CharField(default="sucesso")
    total = serializers.IntegerField()
    guiches = GuicheSerializer(many=True)


# ============================================================
# SERIALIZERS DO PAINEL TV
# ============================================================
class UltimaChamadaSerializer(serializers.Serializer):
    senha = serializers.CharField(help_text="Código da senha (ex: P1, A10)")
    tipo = serializers.CharField(help_text="Tipo da senha (normal, preferencial)")
    guiche = serializers.CharField(help_text="Nome do guichê chamador")
    chamada_id = serializers.IntegerField(help_text="ID do histórico da chamada")
    acao = serializers.CharField(help_text="Ação registrada (chamando, chamando_novamente)")
    hora = serializers.CharField(allow_null=True, required=False, help_text="Horário da chamada")


class HistoricoChamadaItemSerializer(serializers.Serializer):
    senha = serializers.CharField(help_text="Código da senha")
    guiche = serializers.CharField(help_text="Nome do guichê")
    chamada_id = serializers.IntegerField()
    acao = serializers.CharField()


class FilaEsperaItemSerializer(serializers.Serializer):
    senha = serializers.CharField()
    tipo = serializers.CharField()
    posicao = serializers.IntegerField(help_text="Posição relativa na fila de espera")


class PainelResponseSerializer(serializers.Serializer):
    """Contrato em tempo real consumido pelo painel de TV e monitores."""
    status = serializers.CharField(default="sucesso")
    timestamp = serializers.DateTimeField()
    ultima = UltimaChamadaSerializer(allow_null=True)
    ultimas = HistoricoChamadaItemSerializer(many=True)
    fila = FilaEsperaItemSerializer(many=True)


# ============================================================
# SERIALIZERS DE STATUS DA FILA
# ============================================================
class StatusEmEsperaSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    normal = serializers.IntegerField()
    preferencial = serializers.IntegerField()


class StatusFilaResponseSerializer(serializers.Serializer):
    """Métricas em tempo real sobre o fluxo de senhas do dia."""
    status = serializers.CharField(default="sucesso")
    data = serializers.CharField(help_text="Data de referência (AAAA-MM-DD)")
    total_emitidas_hoje = serializers.IntegerField()
    em_espera = StatusEmEsperaSerializer()
    chamando = serializers.IntegerField()
    finalizadas = serializers.IntegerField()


# ============================================================
# SERIALIZERS DE METADADOS E PERFIL (API ROOT INTERATIVA)
# ============================================================
class ApiRootResponseSerializer(serializers.Serializer):
    nome = serializers.CharField()
    versao = serializers.CharField()
    endpoints = serializers.DictField(child=serializers.URLField(help_text="Hyperlink navegável para o endpoint."))
    documentacao = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    """Dados do usuário autenticado via Bearer JWT ou BasicAuth."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()


# ============================================================
# SERIALIZERS DE SENHAS (HYPERLINKED VIEWSETS & ACTIONS)
# ============================================================
class SenhaModelSerializer(serializers.ModelSerializer):
    """Serializer completo do modelo Senha com links navegáveis de relacionamento."""
    url = serializers.SerializerMethodField(help_text="Hyperlink para o detalhe da senha.")
    guiche_url = serializers.SerializerMethodField(help_text="Hyperlink para o guichê associado.")
    codigo = serializers.SerializerMethodField()
    guiche_nome = serializers.CharField(source='guiche.nome', read_only=True, default=None)

    class Meta:
        model = Senha
        fields = [
            'id',
            'url',
            'codigo',
            'prefixo',
            'numero',
            'tipo',
            'status',
            'guiche',
            'guiche_nome',
            'guiche_url',
            'criada_em',
        ]
        read_only_fields = ['id', 'url', 'codigo', 'prefixo', 'numero', 'status', 'guiche_url', 'criada_em']

    def get_codigo(self, obj) -> str:
        return f"{obj.prefixo}{obj.numero}"

    def get_url(self, obj) -> str | None:
        request = self.context.get('request')
        try:
            return reverse('api:senhas-detail', kwargs={'pk': obj.pk}, request=request)
        except Exception:
            return None

    def get_guiche_url(self, obj) -> str | None:
        if not obj.guiche_id:
            return None
        request = self.context.get('request')
        try:
            return reverse('api:guiches-detail', kwargs={'pk': obj.guiche_id}, request=request)
        except Exception:
            return None


class SenhaEmitirSerializer(serializers.Serializer):
    """Payload para emissão de senha no totem ou via API."""
    tipo = serializers.ChoiceField(
        choices=FilaValidator.TIPOS_PERMITIDOS,
        default="normal",
        help_text="Tipo da senha a ser gerada: 'normal' ou 'preferencial'."
    )

    def validate_tipo(self, value):
        return FilaValidator.validar_tipo_fila(value)


class ChamadaProximaSerializer(serializers.Serializer):
    """Payload para chamar a próxima senha da fila em um guichê."""
    guiche_id = serializers.IntegerField(
        help_text="ID do guichê ativo que está realizando a chamada."
    )

    def validate_guiche_id(self, value):
        FilaValidator.validar_guiche_ativo(value)
        return value


class ChamadaNovamenteSerializer(serializers.Serializer):
    """Payload para rechamar a senha atual do guichê."""
    guiche_id = serializers.IntegerField(
        help_text="ID do guichê ativo que deseja rechamar a senha."
    )

    def validate_guiche_id(self, value):
        FilaValidator.validar_guiche_ativo(value)
        return value


# ============================================================
# SERIALIZERS DE ATENDIMENTOS (HYPERLINKED VIEWSETS & ACTIONS)
# ============================================================
class AtendimentoSerializer(serializers.ModelSerializer):
    """Serializer de leitura e persistência de Atendimento com relacionamentos navegáveis."""
    url = serializers.SerializerMethodField(help_text="Hyperlink para o detalhe do atendimento.")
    senha_url = serializers.SerializerMethodField(help_text="Hyperlink para a senha atendida.")
    senha_codigo = serializers.CharField(source='senha.__str__', read_only=True, default='')

    class Meta:
        model = Atendimento
        fields = [
            'id',
            'url',
            'atendente',
            'aluno',
            'guiche',
            'senha',
            'senha_codigo',
            'senha_url',
            'tipo',
            'inicio',
            'fim',
        ]
        read_only_fields = ['id', 'url', 'senha_codigo', 'senha_url', 'inicio', 'fim']

    def get_url(self, obj) -> str | None:
        request = self.context.get('request')
        try:
            return reverse('api:atendimentos-detail', kwargs={'pk': obj.pk}, request=request)
        except Exception:
            return None

    def get_senha_url(self, obj) -> str | None:
        if not obj.senha_id:
            return None
        request = self.context.get('request')
        try:
            return reverse('api:senhas-detail', kwargs={'pk': obj.senha_id}, request=request)
        except Exception:
            return None


class AtendimentoIniciarSerializer(serializers.Serializer):
    """Payload para iniciar o atendimento de uma senha no guichê."""
    senha_id = serializers.IntegerField(help_text="ID da senha que foi chamada.")
    guiche_id = serializers.IntegerField(help_text="ID do guichê operador.")
    atendente = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    aluno = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    tipo = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")

    def validate_tipo(self, value):
        if value:
            return AtendimentoValidator.validar_tipo_atendimento(value)
        return value


class AtendimentoTransferirSerializer(serializers.Serializer):
    """Payload para transferência de senha entre guichês."""
    guiche_origem_id = serializers.IntegerField(help_text="ID do guichê atual.")
    guiche_destino_id = serializers.IntegerField(help_text="ID do guichê para onde transferir.")
    motivo = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        AtendimentoValidator.validar_transferencia(
            attrs.get("guiche_origem_id"),
            attrs.get("guiche_destino_id")
        )
        return attrs
