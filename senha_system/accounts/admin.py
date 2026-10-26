from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

from .models import Guiche


@admin.register(Guiche)
class GuicheAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)

    def delete_model(self, request, obj):
        obj.ativo = False
        obj.save(update_fields=["ativo"])


logo = static("frontend/img/iscon2.png")

admin.site.site_header = format_html(
    '''
    <div style="text-align: center;">
        <img src="{}" style="height: 60px;">
        <br>
        <strong>ADMINISTRAÇÃO</strong>
        <br>
        Sistema de Senhas ISCON
    </div>
    ''',
    logo
)