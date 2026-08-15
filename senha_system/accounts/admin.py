from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

from .models import Guiche
admin.site.register(Guiche)

logo = static("imagens/iscon2.png")

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