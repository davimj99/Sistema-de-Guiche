from django.db import models

class Funcionario(models.Model):

    nome = models.CharField(
        max_length=150
    )

    matricula = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    setor = models.CharField(
        max_length=100,
        blank=True
    )

    cargo = models.CharField(
        max_length=100,
        blank=True
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "funcionarios"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class EPI(models.Model):

    UNIDADES = (
        ("unidade", "Unidade"),
        ("par", "Par"),
        ("caixa", "Caixa"),
    )

    nome = models.CharField(max_length=100)

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    categoria = models.CharField(
        max_length=100
    )

    descricao = models.TextField(
        blank=True
    )

    unidade = models.CharField(
        max_length=20,
        choices=UNIDADES,
        default="unidade"
    )

    quantidade_estoque = models.PositiveIntegerField(
        default=0
    )

    estoque_minimo = models.PositiveIntegerField(
        default=0
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "epis"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - {self.codigo}"


class EntregaEPI(models.Model):

    epi = models.ForeignKey(
        EPI,
        on_delete=models.PROTECT,
        related_name="entregas"
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="entregas_epi"
    )

    quantidade = models.PositiveIntegerField()

    data_entrega = models.DateField(
        auto_now_add=True
    )

    data_proxima_troca = models.DateField(
        null=True,
        blank=True
    )

    observacao = models.TextField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "entregas_epi"
        ordering = ["-data_entrega"]

    def __str__(self):
        return (
            f"{self.epi.nome} - "
            f"{self.funcionario.nome}"
        )