from django.contrib import admin
from .models import Senha, Propaganda, Historico

admin.site.register(Senha)
admin.site.register(Historico)

@admin.register(Propaganda)
class PropagandaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativa', 'criada_em')
    list_filter = ('ativa',)
    search_fields = ('titulo',)
