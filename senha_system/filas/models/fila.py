from django.db import models


class ControleFila(models.Model):
    contador = models.IntegerField(default=0)

    def __str__(self):
        return f"Contador: {self.contador}"