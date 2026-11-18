from datetime import datetime, time
from django.utils import timezone
from django.db.models import Count, Q
<<<<<<< Updated upstream
from django.contrib.auth.models import User
=======
>>>>>>> Stashed changes
from accounts.models import Guiche
from filas.models import Senha
from atendimentos.models import Atendimento
from dashboard.models import ApiRequestLog
from .date_filter import calcular_intervalo_filtro, calcular_variacao_percentual


class KpiService:
    """
    Serviço de cálculo de indicadores-chave de desempenho (KPIs)
    para o Painel Administrativo ISCON.
    """

    @classmethod
    def obter_kpis_completos(
        cls,
        periodo: str = "7d",
        data_inicio: str = None,
        data_fim: str = None,
        guiche_id: int = None,
        atendente: str = None,
        tipo_atendimento: str = None,
        status_senha: str = None,
    ) -> dict:
        """
        Retorna todos os indicadores em cards consolidados com comparações de períodos.
        """
        inicio_atual, fim_atual, inicio_ant, fim_ant, rotulo = calcular_intervalo_filtro(
            periodo, data_inicio, data_fim
        )

        # Filtros base para senhas
        qs_senhas_atual = Senha.objects.filter(criada_em__range=(inicio_atual, fim_atual))
        qs_senhas_ant = Senha.objects.filter(criada_em__range=(inicio_ant, fim_ant))

        # Filtros base para atendimentos
        qs_atend_atual = Atendimento.objects.filter(fim__range=(inicio_atual, fim_atual))
        qs_atend_ant = Atendimento.objects.filter(fim__range=(inicio_ant, fim_ant))

        # Filtros adicionais conforme parâmetros
        if guiche_id:
            qs_senhas_atual = qs_senhas_atual.filter(guiche_id=guiche_id)
            qs_senhas_ant = qs_senhas_ant.filter(guiche_id=guiche_id)
            qs_atend_atual = qs_atend_atual.filter(guiche=guiche_id)
            qs_atend_ant = qs_atend_ant.filter(guiche=guiche_id)

        if atendente:
            qs_atend_atual = qs_atend_atual.filter(atendente=atendente)
            qs_atend_ant = qs_atend_ant.filter(atendente=atendente)

        if tipo_atendimento:
            qs_atend_atual = qs_atend_atual.filter(tipo=tipo_atendimento)
            qs_atend_ant = qs_atend_ant.filter(tipo=tipo_atendimento)

        if status_senha:
            qs_senhas_atual = qs_senhas_atual.filter(status=status_senha)
            qs_senhas_ant = qs_senhas_ant.filter(status=status_senha)

        # 1. Total de Senhas Emitidas
        total_senhas_atual = qs_senhas_atual.count()
        total_senhas_ant = qs_senhas_ant.count()
        var_senhas = calcular_variacao_percentual(total_senhas_atual, total_senhas_ant)

        # 2. Total de Atendimentos Realizados (finalizados no período)
        total_atend_atual = qs_atend_atual.filter(fim__isnull=False).count()
        total_atend_ant = qs_atend_ant.filter(fim__isnull=False).count()
        var_atend = calcular_variacao_percentual(total_atend_atual, total_atend_ant)

        # 3. Total de Atendimentos em Andamento (instantâneo / ao vivo)
        # Identificado por atendimentos com fim nulo ou senhas com status "atendimento"
        atendimentos_em_andamento = Atendimento.objects.filter(fim__isnull=True).count()
        senhas_em_atendimento = Senha.objects.filter(status="atendimento").count()
        total_em_andamento = max(atendimentos_em_andamento, senhas_em_atendimento)

        # 4. Total de Senhas Aguardando Atendimento (instantâneo na fila)
        senhas_aguardando = Senha.objects.filter(status="espera").count()

        # 5. Total de Senhas Canceladas
        # Nota técnica: o sistema ISCON atualmente utiliza status 'espera', 'chamando', 'atendimento', 'finalizado'
        senhas_canceladas = Senha.objects.filter(status="cancelado").count()

        # 6. Total de Requisições da API REST
        qs_api_atual = ApiRequestLog.objects.filter(criado_em__range=(inicio_atual, fim_atual))
        qs_api_ant = ApiRequestLog.objects.filter(criado_em__range=(inicio_ant, fim_ant))
        total_api_atual = qs_api_atual.count()
        total_api_ant = qs_api_ant.count()
        var_api = calcular_variacao_percentual(total_api_atual, total_api_ant)

        # 7. Guichês Ativos
        guiches_ativos = Guiche.objects.filter(ativo=True).count()
        total_guiches = Guiche.objects.count()

        # 8. Atendentes Ativos
        # Conta atendentes cadastrados no sistema com perfil ativo ou atendentes com atendimentos recentes
        atendentes_com_atendimentos = qs_atend_atual.exclude(atendente__isnull=True).exclude(atendente="").values('atendente').distinct().count()
<<<<<<< Updated upstream
        usuarios_staff_ativos = User.objects.filter(is_active=True, is_staff=True).count()
        atendentes_ativos = max(atendentes_com_atendimentos, usuarios_staff_ativos)
=======
        # O modelo não relaciona atendimentos a usuários; conte operadores identificados
        # nos registros reais do período, sem usar is_staff como substituto de função.
        atendentes_ativos = atendentes_com_atendimentos
>>>>>>> Stashed changes

        # 9. Tempo Médio de Atendimento (em minutos)
        tempo_medio_minutos = cls.calcular_tempo_medio_atendimentos(qs_atend_atual)

        return {
            "periodo_rotulo": rotulo,
            "inicio_atual": inicio_atual.isoformat(),
            "fim_atual": fim_atual.isoformat(),
            "kpis": {
                "senhas_emitidas": {
                    "total": total_senhas_atual,
                    "anterior": total_senhas_ant,
                    "variacao": var_senhas,
                    "icone": "ticket",
                    "titulo": "Senhas Emitidas"
                },
                "atendimentos_realizados": {
                    "total": total_atend_atual,
                    "anterior": total_atend_ant,
                    "variacao": var_atend,
                    "icone": "check-circle",
                    "titulo": "Atendimentos Realizados"
                },
                "em_andamento": {
                    "total": total_em_andamento,
                    "status": "ao_vivo",
                    "icone": "clock",
                    "titulo": "Em Atendimento Agora"
                },
                "aguardando_espera": {
                    "total": senhas_aguardando,
                    "status": "ao_vivo",
                    "icone": "users",
                    "titulo": "Aguardando na Fila"
                },
                "senhas_canceladas": {
                    "total": senhas_canceladas,
<<<<<<< Updated upstream
                    "nota": "Status de cancelamento no fluxo operacional",
=======
                    "nota": "O fluxo atual não define um status oficial de cancelamento.",
>>>>>>> Stashed changes
                    "icone": "x-circle",
                    "titulo": "Senhas Canceladas"
                },
                "requisicoes_api": {
                    "total": total_api_atual,
                    "anterior": total_api_ant,
                    "variacao": var_api,
                    "icone": "server",
                    "titulo": "Requisições da API"
                },
                "guiches_ativos": {
                    "total": guiches_ativos,
                    "total_geral": total_guiches,
                    "icone": "layout",
                    "titulo": "Guichês Ativos"
                },
                "atendentes_ativos": {
                    "total": atendentes_ativos,
                    "icone": "user-check",
                    "titulo": "Atendentes em Operação"
                },
                "tempo_medio": {
                    "valor_minutos": tempo_medio_minutos["minutos"],
                    "minutos": tempo_medio_minutos["minutos"],
                    "formatado": tempo_medio_minutos["formatado"],
                    "amostras": tempo_medio_minutos["amostras"],
                    "icone": "activity",
                    "titulo": "Tempo Médio de Atendimento"
                }
            }
        }

    @classmethod
    def calcular_tempo_medio_atendimentos(cls, queryset_atendimentos) -> dict:
        """
        Calcula a média de duração dos atendimentos que possuem fim e início válidos.
        Lida com o fato de inicio ser TimeField e fim ser DateTimeField.
        """
        atendimentos_completos = queryset_atendimentos.filter(
            fim__isnull=False,
            inicio__isnull=False
        ).only("inicio", "fim")

        duracoes_segundos = []
        tz_local = timezone.get_current_timezone()
        for at in atendimentos_completos:
            try:
                # Converte fim para o timezone local do projeto (America/Sao_Paulo)
                fim_local = timezone.localtime(at.fim)
                dt_inicio = datetime.combine(fim_local.date(), at.inicio)
                dt_inicio = timezone.make_aware(dt_inicio, tz_local)

                segundos = (fim_local - dt_inicio).total_seconds()
                # Considera apenas atendimentos com duração coerente (entre 10s e 4h)
                if 10 <= segundos <= 14400:
                    duracoes_segundos.append(segundos)
            except Exception:
                continue

        if not duracoes_segundos:
            return {
                "segundos": 0,
                "minutos": 0.0,
                "formatado": "00m 00s",
                "amostras": 0
            }

        media_seg = sum(duracoes_segundos) / len(duracoes_segundos)
        minutos = int(media_seg // 60)
        segundos = int(media_seg % 60)
        return {
            "segundos": round(media_seg, 1),
            "minutos": round(media_seg / 60, 1),
            "formatado": f"{minutos:02d}m {segundos:02d}s",
            "amostras": len(duracoes_segundos)
        }
