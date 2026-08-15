from django.contrib import admin
from .models import Atendimento
from .forms import AtendimentoForm


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    form = AtendimentoForm

    list_display = (
        'senha',
        'aluno',
        'atendente',
        'guiche',
        'tipo',
        'inicio',
        'fim',
    )

    list_filter = (
        'atendente',
        'guiche',
        'tipo',
    )

    search_fields = (
        'aluno',
        'atendente',
    )

    ordering = ('-fim',)