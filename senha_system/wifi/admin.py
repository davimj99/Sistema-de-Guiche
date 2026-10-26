from django.contrib import admin

from .models import SolicitacaoWifi, AcessoWifi


@admin.register(SolicitacaoWifi)
class SolicitacaoWifiAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nome_aluno',
        'matricula',
        'curso',
        'status',
        'criado_em',
    )

    list_filter = (
        'status',
        'curso',
        'criado_em',
    )

    search_fields = (
        'nome_aluno',
        'matricula',
        'email',
    )

    readonly_fields = (
        'criado_em',
        'atualizado_em',
    )

    ordering = (
        '-criado_em',
    )


@admin.register(AcessoWifi)
class AcessoWifiAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'solicitacao',
        'ssid',
        'usuario',
        'ativo',
        'criado_em',
        'expira_em',
    )

    list_filter = (
        'ativo',
        'ssid',
        'criado_em',
    )

    search_fields = (
        'usuario',
        'ssid',
        'solicitacao__nome_aluno',
        'solicitacao__matricula',
    )

    readonly_fields = (
        'criado_em',
    )

    ordering = (
        '-criado_em',
    )