from rest_framework import serializers
from accounts.models import Guiche
from filas.models import Senha, Historico


# ============================================================
# SERIALIZERS DE GUICHÊ
# ============================================================
class GuicheSerializer(serializers.ModelSerializer):
    """Representação serializada de um Guichê de Atendimento."""
    class Meta:
        model = Guiche
        fields = ['id', 'nome', 'ativo']


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
# SERIALIZERS DE METADADOS E PERFIL (JWT)
# ============================================================
class ApiRootResponseSerializer(serializers.Serializer):
    nome = serializers.CharField()
    versao = serializers.CharField()
    endpoints = serializers.DictField(child=serializers.CharField())
    documentacao = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    """Dados do usuário autenticado via Bearer JWT."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()
