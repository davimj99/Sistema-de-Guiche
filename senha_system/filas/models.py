from django.db import models

class Senha(models.Model):

    STATUS = (
        ("espera", "Em Espera"),
        ("chamando", "Chamando"),
        ("atendimento", "Em Atendimento"),
        ("finalizado", "Finalizado"),
    )

    TIPO = (
        ("normal", "Normal"),
        ("preferencial", "Preferencial"),
    )

    numero = models.IntegerField()
    prefixo = models.CharField(max_length=2)

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
    
class ControleFila(models.Model):
    contador = models.IntegerField(default=0)
    def __str__(self):
        return f"Contador: {self.contador}"

class Propaganda(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='propagandas/')
    video = models.FileField(upload_to='propagandas/videos/', blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Historico(models.Model):
    senha = models.ForeignKey(
        "Senha",
        on_delete=models.CASCADE
    )

    guiche = models.ForeignKey(
        "accounts.Guiche",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    acao = models.CharField(max_length=20)  # chamando / finalizado

    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senha} - {self.acao}"