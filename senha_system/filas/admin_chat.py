from django.contrib import admin
from .models import ChatbotMensagem


@admin.register(ChatbotMensagem)
class ChatbotMensagemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "criado_em",
    )

    search_fields = (
        "pergunta",
        "resposta",
        "usuario__username",
    )

    list_filter = (
        "criado_em",
    )

    readonly_fields = (
        "criado_em",
    )