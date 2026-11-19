import datetime
from django.db.models import Count
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
            qs_atual = qs_atual.filter(guiche=guiche_id)
            qs_ant = qs_ant.filter(guiche=guiche_id)
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
        # Atendimento.guiche guarda o ID do cadastro como inteiro legado, sem
        # ForeignKey. Use o cadastro ativo como fonte de verdade e ignore IDs
        # históricos sem correspondência ou associados a guichês inativos.
        guiches_cadastrados = {
            g.id: g.nome
            for g in Guiche.objects.filter(ativo=True).order_by("id")
        }
        dados_atual = dict(
            qs_atual.filter(guiche__in=guiches_cadastrados)
            .values('guiche')
            .annotate(total=Count('id'))
            .values_list('guiche', 'total')
        )
        dados_ant = dict(
            qs_ant.filter(guiche__in=guiches_cadastrados)
            .values('guiche')
            .annotate(total=Count('id'))
            .values_list('guiche', 'total')
        )

        resultado = []

        for gid, nome in guiches_cadastrados.items():
            total = dados_atual.get(gid, 0)
            anterior = dados_ant.get(gid, 0)
            percentual = round((total / total_geral) * 100, 1) if total_geral > 0 else 0.0

            # Tempo médio específico do guichê
            qs_g = qs_atual.filter(guiche=gid)
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
