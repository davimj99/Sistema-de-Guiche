from django.db import models

class Atendimento(models.Model):

    TIPOS_ATENDIMENTO = [
        ('matricula', 'Matrícula'),
        ('financeiro', 'Financeiro'),
        ('secretaria', 'Secretaria'),
        ('declaração', 'Declaração'),
        ('grade', 'Grade'),
        ('suporte', 'Suporte'),
    ]

    senha = models.ForeignKey("filas.Senha", on_delete=models.CASCADE)
    inicio = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_ATENDIMENTO,
        null=True,
        blank=True
    )
    fim = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.senha} - {self.tipo}'