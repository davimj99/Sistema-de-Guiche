from django.contrib.auth.models import User
from django.db import models


class ChatbotMensagem(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mensagens_chatbot"
    )

    pergunta = models.TextField()
    resposta = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chatbot_mensagens"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario} - {self.criado_em:%d/%m/%Y %H:%M}"