from django.contrib import admin
from .models import Atendimento
from .forms import AtendimentoForm

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    form = AtendimentoForm