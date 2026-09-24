from django.db import models

class Senha(models.Model):

    STATUS = (
        ("espera", "Em Espera"),
        ("chamando", "Chamando"),
        ("chamando_novamente", "Chamando_Novamente"),
        ("atendimento", "Em Atendimento"),
        ("finalizado", "Finalizado"),
    )

    TIPO = (
        ("normal", "Normal"),
        ("preferencial", "Preferencial"),
    )

    prefixo = models.CharField(max_length=2)
    numero = models.IntegerField()

    tipo = models.CharField(
        max_length=20,
        choices=TIPO,
        default="normal"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="espera"
    )

    guiche = models.ForeignKey(
        "accounts.Guiche",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prefixo}{self.numero}"