from django.db import models


class Historico(models.Model):
    senha = models.ForeignKey(
        "Senha",
        on_delete=models.PROTECT
    )

    guiche = models.ForeignKey(
        "accounts.Guiche",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    acao = models.CharField(max_length=20)

    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senha} - {self.acao}"