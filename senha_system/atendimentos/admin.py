from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import Atendimento
from .forms import AtendimentoForm


class PeriodoAtendimentoFilter(admin.SimpleListFilter):
    title = 'Período'
    parameter_name = 'periodo'

    def lookups(self, request, model_admin):
        return (
            ('hoje', 'Hoje'),
            ('ontem', 'Ontem'),
            ('7_dias', 'Últimos 7 dias'),
            ('mes', 'Este mês'),
            ('mes_anterior', 'Mês passado'),
        )

    def queryset(self, request, queryset):
        agora = timezone.localtime(timezone.now())
        hoje = agora.date()

        if self.value() == 'hoje':
            return queryset.filter(fim__date=hoje)

        if self.value() == 'ontem':
            ontem = hoje - timedelta(days=1)
            return queryset.filter(fim__date=ontem)

        if self.value() == '7_dias':
            data_inicio = hoje - timedelta(days=6)
            return queryset.filter(
                fim__date__gte=data_inicio,
                fim__date__lte=hoje
            )

        if self.value() == 'mes':
            data_inicio = hoje.replace(day=1)
            return queryset.filter(
                fim__date__gte=data_inicio,
                fim__date__lte=hoje
            )

        if self.value() == 'mes_anterior':
            primeiro_dia_mes_atual = hoje.replace(day=1)
            ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
            primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

            return queryset.filter(
                fim__date__gte=primeiro_dia_mes_anterior,
                fim__date__lte=ultimo_dia_mes_anterior
            )

        return queryset


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
        PeriodoAtendimentoFilter,
        'atendente',
        'guiche',
        'tipo',
    )

    search_fields = (
        'aluno',
        'atendente',
    )

    ordering = ('-fim',)