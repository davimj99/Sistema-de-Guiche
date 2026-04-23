from django.db import models

class Atendimento(models.Model):
    senha = models.ForeignKey("filas.Senha", on_delete=models.CASCADE)
    inicio = models.DateTimeField(auto_now_add=True)
    fim = models.DateTimeField(null=True, blank=True)