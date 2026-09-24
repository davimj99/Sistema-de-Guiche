from django.db import models

class Propaganda(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to="propagandas/")
    video = models.FileField(
        upload_to="propagandas/videos/",
        blank=True,
        null=True
    )
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo