from django.db import models

class Guiche(models.Model):
    numero = models.CharField(max_length=10)

    def __str__(self):
        return f"Guichê {self.numero}"


class Senha(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Normal'),
        ('preferencial', 'Preferencial'),
    ]

    STATUS_CHOICES = [
        ('espera', 'Em espera'),
        ('chamando', 'Chamando'),
        ('finalizado', 'Finalizado'),
    ]

    codigo = models.CharField(max_length=10)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='espera')

    guiche = models.ForeignKey(Guiche, on_delete=models.SET_NULL, null=True, blank=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    chamada_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo