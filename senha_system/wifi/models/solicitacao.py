
from django.db import models


class SolicitacaoWifi(models.Model):

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANALISE', 'Em análise'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('CANCELADO', 'Cancelado'),
    ]

    protocolo = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    nome_aluno = models.CharField(max_length=150)

    matricula = models.CharField(max_length=50)

    curso = models.CharField(max_length=150)

    email = models.EmailField(blank=True)

    dispositivo = models.CharField(max_length=100, blank=True)

    motivo = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )

    observacao_ti = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.protocolo} - {self.nome_aluno}'