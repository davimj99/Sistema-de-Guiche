from django.db import models

class Atendimento(models.Model):

    TIPOS_ATENDIMENTO = [
        ('matricula', 'Matrícula'),
        ('financeiro', 'Financeiro'),
        ('secretaria', 'Secretaria'),
        ('declaração', 'Declaração'),
        ('grade', 'Grade'),
        ('requerimento', 'Requerimento'),
        ('ementario/historico', 'Ementário/Histórico'),
        ('suporte', 'Suporte'),
        ('ti', 'TI'),
    ]

    ATENDENTES = [
    ('Alessandra', 'Alessandra'),
    ('Rafael', 'Rafael'),
    ('Geovanna', 'Geovanna'),
    ('Fátima', 'Fátima'),
    ('Fernando', 'Fernando'),
    ('Jane', 'Jane'),
    ]

    atendente = models.CharField(max_length=100,choices=ATENDENTES,null=True,blank=True)
    aluno = models.CharField(max_length=100, null=True, blank=True)
    guiche = models.IntegerField(null=True, blank=True)
    senha = models.ForeignKey("filas.Senha", on_delete=models.PROTECT)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_ATENDIMENTO,
        null=True,
        blank=True
    )
    inicio = models.TimeField(null=True, blank=True)
    fim = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.senha} - {self.tipo} - {self.guiche}'