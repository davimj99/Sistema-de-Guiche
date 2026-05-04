from django.contrib import admin
from .models import Senha, Propaganda

admin.site.register(Senha)


@admin.register(Propaganda)
class PropagandaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativa', 'criada_em')
    list_filter = ('ativa',)
    search_fields = ('titulo',)