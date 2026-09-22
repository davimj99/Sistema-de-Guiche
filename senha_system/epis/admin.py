from django.contrib import admin

from .models import EPI, EntregaEPI, Funcionario


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "codigo",
        "categoria",
        "unidade",
        "quantidade_estoque",
        "estoque_minimo",
        "status_estoque",
        "ativo",
    )

    search_fields = (
        "nome",
        "codigo",
        "categoria",
    )

    list_filter = (
        "categoria",
        "unidade",
        "ativo",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    def status_estoque(self, obj):
        if obj.quantidade_estoque <= obj.estoque_minimo:
            return "Estoque baixo"

        return "Normal"

    status_estoque.short_description = "Status"


@admin.register(EntregaEPI)
class EntregaEPIAdmin(admin.ModelAdmin):

    list_display = (
        "epi",
        "funcionario",
        "quantidade",
        "data_entrega",
        "data_proxima_troca",
    )

    search_fields = (
        "epi__nome",
        "epi__codigo",
        "funcionario__nome",
        "funcionario__matricula",
        "funcionario__setor",
        "funcionario__cargo",
    )

    list_filter = (
        "data_entrega",
        "data_proxima_troca",
        "epi",
    )

    readonly_fields = (
        "criado_em",
    )


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "matricula",
        "setor",
        "cargo",
        "ativo",
    )

    search_fields = (
        "nome",
        "matricula",
        "setor",
        "cargo",
    )

    list_filter = (
        "setor",
        "cargo",
        "ativo",
    )