import datetime
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone

from filas.models import Senha
from atendimentos.models import Atendimento
from .date_filter import calcular_intervalo_filtro


class ChartService:
    """
    Serviço gerador de estruturas de dados para visualização de gráficos com Chart.js.
    Garante integridade com o banco de dados e otimização de consultas ORM.
    """

    CORES_PALETA = [
        "#0d6efd",  # Azul ISCON
        "#0a3d91",  # Azul Escuro
        "#d32f2f",  # Vermelho ISCON
        "#20c997",  # Verde Água / Sucesso
        "#fd7e14",  # Laranja
        "#6f42c1",  # Roxo
        "#0dcaf0",  # Ciano
        "#ffc107",  # Amarelo
        "#6c757d",  # Cinza
        "#b71c1c",  # Vermelho Escuro
    ]

    @classmethod
    def obter_graficos_dashboard(
        cls,
        periodo: str = "7d",
        data_inicio: str = None,
        data_fim: str = None,
        guiche_id: int = None,
        atendente: str = None,
        tipo_atendimento: str = None,
    ) -> dict:
        """
        Retorna todos os datasets de gráficos para o Dashboard Principal e Análise de Atendimentos.
        """
        inicio_atual, fim_atual, _, _, rotulo = calcular_intervalo_filtro(
            periodo, data_inicio, data_fim
        )

        qs_atend = Atendimento.objects.filter(fim__range=(inicio_atual, fim_atual))
        qs_senhas = Senha.objects.filter(criada_em__range=(inicio_atual, fim_atual))

        if guiche_id:
            qs_atend = qs_atend.filter(guiche=guiche_id)
            qs_senhas = qs_senhas.filter(guiche_id=guiche_id)
        if atendente:
            qs_atend = qs_atend.filter(atendente=atendente)
        if tipo_atendimento:
            qs_atend = qs_atend.filter(tipo=tipo_atendimento)

        return {
            "periodo": rotulo,
            "serie_temporal_comparativa": cls.obter_comparacao_senhas_atendimentos(inicio_atual, fim_atual, qs_senhas, qs_atend),
            "atendimentos_por_dia": cls.obter_atendimentos_por_dia(inicio_atual, fim_atual, qs_atend),
            "atendimentos_por_semana": cls.obter_atendimentos_por_semana(qs_atend),
            "atendimentos_por_mes": cls.obter_atendimentos_por_mes(qs_atend),
            "distribuicao_tipo": cls.obter_distribuicao_por_tipo(qs_atend),
            "distribuicao_guiche": cls.obter_distribuicao_por_guiche(qs_atend),
            "distribuicao_atendente": cls.obter_distribuicao_por_atendente(qs_atend),
            "horarios_movimento": cls.obter_horarios_maior_movimento(qs_atend),
        }

    @classmethod
    def obter_comparacao_senhas_atendimentos(cls, inicio, fim, qs_senhas, qs_atend) -> dict:
        """
        Gera série temporal diária comparando Senhas Emitidas vs Atendimentos Concluídos.
        """
        # Agregação diária de senhas
        senhas_por_dia = dict(
            qs_senhas.annotate(dia=TruncDate('criada_em'))
            .values('dia')
            .annotate(total=Count('id'))
            .values_list('dia', 'total')
        )

        # Agregação diária de atendimentos
        atend_por_dia = dict(
            qs_atend.filter(fim__isnull=False)
            .annotate(dia=TruncDate('fim'))
            .values('dia')
            .annotate(total=Count('id'))
            .values_list('dia', 'total')
        )

        # Preenche todos os dias do intervalo (inclusive os com zero)
        labels = []
        dados_senhas = []
        dados_atendimentos = []

        curr = inicio.date()
        fim_date = fim.date()
        while curr <= fim_date:
            labels.append(curr.strftime("%d/%m"))
            dados_senhas.append(senhas_por_dia.get(curr, 0))
            dados_atendimentos.append(atend_por_dia.get(curr, 0))
            curr += datetime.timedelta(days=1)

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Senhas Emitidas",
                    "data": dados_senhas,
                    "borderColor": "#0d6efd",
                    "backgroundColor": "rgba(13, 110, 253, 0.15)",
                    "borderWidth": 2,
                    "tension": 0.3,
                    "fill": True,
                },
                {
                    "label": "Atendimentos Realizados",
                    "data": dados_atendimentos,
                    "borderColor": "#20c997",
                    "backgroundColor": "rgba(32, 201, 151, 0.15)",
                    "borderWidth": 2,
                    "tension": 0.3,
                    "fill": True,
                }
            ]
        }

    @classmethod
    def obter_atendimentos_por_dia(cls, inicio, fim, qs_atend) -> dict:
        """Série diária de atendimentos."""
        atend_por_dia = dict(
            qs_atend.filter(fim__isnull=False)
            .annotate(dia=TruncDate('fim'))
            .values('dia')
            .annotate(total=Count('id'))
            .values_list('dia', 'total')
        )
        labels = []
        valores = []
        curr = inicio.date()
        while curr <= fim.date():
            labels.append(curr.strftime("%d/%m/%Y"))
            valores.append(atend_por_dia.get(curr, 0))
            curr += datetime.timedelta(days=1)

        return {
            "labels": labels,
            "datasets": [{
                "label": "Atendimentos",
                "data": valores,
                "backgroundColor": "#0d6efd",
                "borderRadius": 4,
            }]
        }

    @classmethod
    def obter_atendimentos_por_semana(cls, qs_atend) -> dict:
        """Agregação de atendimentos agrupados por semana."""
        dados = (
            qs_atend.filter(fim__isnull=False)
            .annotate(semana=TruncWeek('fim'))
            .values('semana')
            .annotate(total=Count('id'))
            .order_by('semana')
        )
        labels = [d['semana'].strftime("Semana %W/%Y") if d['semana'] else "N/A" for d in dados]
        valores = [d['total'] for d in dados]

        if not labels:
            labels = ["Sem dados no período"]
            valores = [0]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Atendimentos por Semana",
                "data": valores,
                "backgroundColor": "#0a3d91",
                "borderRadius": 4,
            }]
        }

    @classmethod
    def obter_atendimentos_por_mes(cls, qs_atend) -> dict:
        """Agregação de atendimentos agrupados por mês."""
        dados = (
            qs_atend.filter(fim__isnull=False)
            .annotate(mes=TruncMonth('fim'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        labels = []
        for d in dados:
            if d['mes']:
                m = d['mes']
                labels.append(f"{meses_pt[m.month - 1]}/{m.year}")
            else:
                labels.append("N/A")
        valores = [d['total'] for d in dados]

        if not labels:
            labels = ["Sem dados no período"]
            valores = [0]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Atendimentos por Mês",
                "data": valores,
                "backgroundColor": "#d32f2f",
                "borderRadius": 4,
            }]
        }

    @classmethod
    def obter_distribuicao_por_tipo(cls, qs_atend) -> dict:
        """Distribuição percentual e absoluta por tipo de serviço."""
        tipo_dict = dict(Atendimento.TIPOS_ATENDIMENTO)
        dados = (
            qs_atend.values('tipo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = []
        valores = []
        for d in dados:
            tipo_chave = d['tipo'] or 'Outros'
            nome_amigavel = tipo_dict.get(tipo_chave, tipo_chave.capitalize())
            labels.append(nome_amigavel)
            valores.append(d['total'])

        if not labels:
            labels = ["Nenhum registro"]
            valores = [0]

        return {
            "labels": labels,
            "datasets": [{
                "data": valores,
                "backgroundColor": cls.CORES_PALETA[:len(labels)],
                "borderWidth": 1,
            }]
        }

    @classmethod
    def obter_distribuicao_por_guiche(cls, qs_atend) -> dict:
        """Distribuição de atendimentos por Guichê."""
        dados = (
            qs_atend.values('guiche')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = []
        valores = []
        for d in dados:
            guiche_num = d['guiche']
            rotulo = f"Guichê {guiche_num}" if guiche_num else "Não Informado"
            labels.append(rotulo)
            valores.append(d['total'])

        if not labels:
            labels = ["Nenhum guichê"]
            valores = [0]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Atendimentos por Guichê",
                "data": valores,
                "backgroundColor": "#0d6efd",
                "borderRadius": 4,
            }]
        }

    @classmethod
    def obter_distribuicao_por_atendente(cls, qs_atend) -> dict:
        """Distribuição de atendimentos por Atendente."""
        dados = (
            qs_atend.values('atendente')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = []
        valores = []
        for d in dados:
            nome = d['atendente'] or "Não Definido"
            labels.append(nome)
            valores.append(d['total'])

        if not labels:
            labels = ["Nenhum atendente"]
            valores = [0]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Atendimentos por Atendente",
                "data": valores,
                "backgroundColor": "#0a3d91",
                "borderRadius": 4,
            }]
        }

    @classmethod
    def obter_horarios_maior_movimento(cls, qs_atend) -> dict:
        """
        Calcula a concentração de atendimentos por faixa horária do dia (das 07:00 às 22:00).
        """
        # Consulta os horários de início ou fim
        atendimentos = qs_atend.only('inicio', 'fim')
        contagem_horas = defaultdict(int)

        for at in atendimentos:
            hora = None
            if at.inicio:
                hora = at.inicio.hour
            elif at.fim:
                hora = timezone.localtime(at.fim).hour
            
            if hora is not None:
                contagem_horas[hora] += 1

        # Gera faixas horárias fixas de interesse acadêmico (7h às 22h)
        horas = list(range(7, 23))
        labels = [f"{h:02d}:00" for h in horas]
        valores = [contagem_horas[h] for h in horas]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Volume de Atendimentos por Horário",
                "data": valores,
                "backgroundColor": "rgba(211, 47, 47, 0.7)",
                "borderColor": "#d32f2f",
                "borderWidth": 2,
                "borderRadius": 4,
            }]
        }
