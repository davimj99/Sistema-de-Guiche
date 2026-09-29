from django.db import models

from .solicitacao import SolicitacaoWifi


class AcessoWifi(models.Model):

    solicitacao = models.OneToOneField(
        SolicitacaoWifi,
        on_delete=models.CASCADE,
        related_name='acesso'
    )

    ssid = models.CharField(max_length=100, blank=True, null=True)

    usuario = models.CharField(max_length=100)

    senha = models.CharField(max_length=255)

    ativo = models.BooleanField(default=True, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    expira_em = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f'{self.usuario} - {self.ssid}'