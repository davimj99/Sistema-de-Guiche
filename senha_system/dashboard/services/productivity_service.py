import datetime
from django.db.models import Case, Count, F, IntegerField, Q, When
from django.utils import timezone
from atendimentos.models import Atendimento
from accounts.models import Guiche
from .date_filter import calcular_intervalo_filtro
from .kpi_service import KpiService


class ProductivityService:
    """
    Serviço analítico de desempenho e produtividade operacional de guichês e atendentes.
    """

    @classmethod
    def obter_relatorio_produtividade(
        cls,
        periodo: str = "7d",
        data_inicio: str = None,
        data_fim: str = None,
        guiche_id: int = None,
        atendente: str = None,
        tipo_atendimento: str = None,
    ) -> dict:
        inicio_atual, fim_atual, inicio_ant, fim_ant, rotulo = calcular_intervalo_filtro(
            periodo, data_inicio, data_fim
        )

        qs_atual = Atendimento.objects.filter(fim__range=(inicio_atual, fim_atual))
        qs_ant = Atendimento.objects.filter(fim__range=(inicio_ant, fim_ant))

        if guiche_id:
            # Atendimento.guiche é um inteiro legado e pode estar nulo ou
            # apontar para um cadastro removido. Nesses casos, a FK da senha
            # associada é a fonte oficial do guichê usado no atendimento.
            guiches_validos = Guiche.objects.filter(ativo=True).values_list("id", flat=True)
            filtro_guiche = (
                Q(guiche=guiche_id)
                | (Q(senha__guiche_id=guiche_id) & ~Q(guiche__in=guiches_validos))
            )
            qs_atual = qs_atual.filter(filtro_guiche)
            qs_ant = qs_ant.filter(filtro_guiche)
        if atendente:
            qs_atual = qs_atual.filter(atendente=atendente)
            qs_ant = qs_ant.filter(atendente=atendente)
        if tipo_atendimento:
            qs_atual = qs_atual.filter(tipo=tipo_atendimento)
            qs_ant = qs_ant.filter(tipo=tipo_atendimento)

        total_atual = qs_atual.count()
        total_ant = qs_ant.count()

        # Produtividade por Guichê
        produtividade_guiches = cls._calcular_produtividade_guiches(qs_atual, qs_ant, total_atual)

        # Produtividade por Atendente
        produtividade_atendentes = cls._calcular_produtividade_atendentes(qs_atual, qs_ant, total_atual)

        # Média diária no período
        dias_intervalo = max(1, (fim_atual.date() - inicio_atual.date()).days + 1)
        media_diaria = round(total_atual / dias_intervalo, 1)

        # Tempo médio geral
        tempo_medio_geral = KpiService.calcular_tempo_medio_atendimentos(qs_atual)

        return {
            "periodo": rotulo,
            "total_atendimentos": total_atual,
            "total_periodo_anterior": total_ant,
            "dias_intervalo": dias_intervalo,
            "media_diaria": media_diaria,
            "tempo_medio_geral": tempo_medio_geral,
            "guiches": produtividade_guiches,
            "atendentes": produtividade_atendentes,
        }

    @classmethod
    def _calcular_produtividade_guiches(cls, qs_atual, qs_ant, total_geral) -> list:
        # Atendimento.guiche guarda o ID como inteiro legado, sem ForeignKey.
        # A anotação também recupera registros inválidos pela FK da senha.
        guiches_cadastrados = {
            g.id: g.nome
            for g in Guiche.objects.filter(ativo=True).order_by("id")
        }
        dados_atual = dict(
            cls._com_guiche_efetivo(qs_atual, guiches_cadastrados)
            .filter(guiche_dashboard__in=guiches_cadastrados)
            .values('guiche_dashboard')
            .annotate(total=Count('id'))
            .values_list('guiche_dashboard', 'total')
        )
        dados_ant = dict(
            cls._com_guiche_efetivo(qs_ant, guiches_cadastrados)
            .filter(guiche_dashboard__in=guiches_cadastrados)
            .values('guiche_dashboard')
            .annotate(total=Count('id'))
            .values_list('guiche_dashboard', 'total')
        )

        resultado = []

        for gid, nome in guiches_cadastrados.items():
            total = dados_atual.get(gid, 0)
            anterior = dados_ant.get(gid, 0)
            percentual = round((total / total_geral) * 100, 1) if total_geral > 0 else 0.0

            # Tempo médio específico do guichê
            qs_g = cls._com_guiche_efetivo(qs_atual, guiches_cadastrados).filter(
                guiche_dashboard=gid
            )
            t_medio = KpiService.calcular_tempo_medio_atendimentos(qs_g)

            resultado.append({
                "guiche_id": gid,
                "nome": nome,
                "total": total,
                "anterior": anterior,
                "percentual_total": percentual,
                "tempo_medio": t_medio["formatado"],
                "tempo_medio_minutos": t_medio["minutos"],
            })

        resultado.sort(key=lambda x: x["total"], reverse=True)
        return resultado

    @staticmethod
    def _com_guiche_efetivo(queryset, guiches_cadastrados):
        """Anota o ID do guichê usando a FK da senha para dados legados inválidos."""
        ids_validos = list(guiches_cadastrados)
        return queryset.annotate(
            guiche_dashboard=Case(
                When(guiche__in=ids_validos, then=F("guiche")),
                default=F("senha__guiche_id"),
                output_field=IntegerField(),
            )
        )

    @classmethod
    def _calcular_produtividade_atendentes(cls, qs_atual, qs_ant, total_geral) -> list:
        dados_atual = dict(
            qs_atual.values('atendente')
            .annotate(total=Count('id'))
            .values_list('atendente', 'total')
        )
        dados_ant = dict(
            qs_ant.values('atendente')
            .annotate(total=Count('id'))
            .values_list('atendente', 'total')
        )

        # Usa somente nomes presentes nos registros do período; não fabrica linhas zeradas.
        todos_atendentes = set(dados_atual.keys())

        resultado = []
        for nome in todos_atendentes:
            if not nome and dados_atual.get(nome, 0) == 0:
                continue

            total = dados_atual.get(nome, 0)
            anterior = dados_ant.get(nome, 0)
            percentual = round((total / total_geral) * 100, 1) if total_geral > 0 else 0.0

            qs_at = qs_atual.filter(atendente=nome)
            t_medio = KpiService.calcular_tempo_medio_atendimentos(qs_at)

            # Principais categorias atendidas por este atendente
            top_servicos = list(
                qs_at.values('tipo')
                .annotate(qtd=Count('id'))
                .order_by('-qtd')[:2]
            )
            top_nomes = [s['tipo'].capitalize() for s in top_servicos if s['tipo']]

            resultado.append({
                "nome": nome or "Não Informado",
                "total": total,
                "anterior": anterior,
                "percentual_total": percentual,
                "tempo_medio": t_medio["formatado"],
                "tempo_medio_minutos": t_medio["minutos"],
                "top_servicos": ", ".join(top_nomes) if top_nomes else "N/A",
            })

        resultado.sort(key=lambda x: x["total"], reverse=True)
        return resultado
