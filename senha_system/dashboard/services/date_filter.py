import datetime
from django.utils import timezone
from typing import Tuple, Dict, Any, Optional


def parse_date_safe(date_str: Optional[str]) -> Optional[datetime.date]:
    """Converte com segurança uma string YYYY-MM-DD em datetime.date."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def calcular_intervalo_filtro(
    periodo: Optional[str] = "7d",
    data_inicio_str: Optional[str] = None,
    data_fim_str: Optional[str] = None
) -> Tuple[datetime.datetime, datetime.datetime, datetime.datetime, datetime.datetime, str]:
    """
    Calcula os limites de data/hora (com timezone ciente) para o período atual
    e o período comparativo anterior equivalente.
    Retorna:
        (inicio_atual, fim_atual, inicio_anterior, fim_anterior, rotulo_periodo)
    """
    hoje = timezone.localdate()
    agora = timezone.localtime()

    periodo = (periodo or "7d").lower().strip()

    if periodo == "hoje":
        inicio_atual_date = hoje
        fim_atual_date = hoje
        inicio_ant_date = hoje - datetime.timedelta(days=1)
        fim_ant_date = hoje - datetime.timedelta(days=1)
        rotulo = "Hoje"

    elif periodo == "ontem":
        ontem = hoje - datetime.timedelta(days=1)
        inicio_atual_date = ontem
        fim_atual_date = ontem
        anteontem = hoje - datetime.timedelta(days=2)
        inicio_ant_date = anteontem
        fim_ant_date = anteontem
        rotulo = "Ontem"

    elif periodo == "30d":
        inicio_atual_date = hoje - datetime.timedelta(days=29)
        fim_atual_date = hoje
        duracao = (fim_atual_date - inicio_atual_date).days + 1
        inicio_ant_date = inicio_atual_date - datetime.timedelta(days=duracao)
        fim_ant_date = inicio_atual_date - datetime.timedelta(days=1)
        rotulo = "Últimos 30 dias"

    elif periodo == "este_mes":
        inicio_atual_date = hoje.replace(day=1)
        fim_atual_date = hoje
        # Mês anterior
        primeiro_dia_mes_atual = inicio_atual_date
        ultimo_dia_mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)
        inicio_ant_date = ultimo_dia_mes_anterior.replace(day=1)
        fim_ant_date = ultimo_dia_mes_anterior
        rotulo = "Este Mês"

    elif periodo == "mes_anterior":
        primeiro_dia_mes_atual = hoje.replace(day=1)
        fim_ant = primeiro_dia_mes_atual - datetime.timedelta(days=1)
        inicio_ant = fim_ant.replace(day=1)

        inicio_atual_date = inicio_ant
        fim_atual_date = fim_ant

        # Mês retrasado para comparação
        ultimo_dia_retrasado = inicio_ant - datetime.timedelta(days=1)
        inicio_ant_date = ultimo_dia_retrasado.replace(day=1)
        fim_ant_date = ultimo_dia_retrasado
        rotulo = "Mês Anterior"

    elif periodo == "personalizado":
        d_inicio = parse_date_safe(data_inicio_str)
        d_fim = parse_date_safe(data_fim_str)
        if not d_inicio:
            d_inicio = hoje - datetime.timedelta(days=6)
        if not d_fim:
            d_fim = hoje
        if d_inicio > d_fim:
            d_inicio, d_fim = d_fim, d_inicio

        inicio_atual_date = d_inicio
        fim_atual_date = d_fim
        duracao = (fim_atual_date - inicio_atual_date).days + 1
        inicio_ant_date = inicio_atual_date - datetime.timedelta(days=duracao)
        fim_ant_date = inicio_atual_date - datetime.timedelta(days=1)
        rotulo = f"{inicio_atual_date.strftime('%d/%m/%Y')} até {fim_atual_date.strftime('%d/%m/%Y')}"

    else:  # Padrão: 7d (Últimos 7 dias)
        inicio_atual_date = hoje - datetime.timedelta(days=6)
        fim_atual_date = hoje
        duracao = (fim_atual_date - inicio_atual_date).days + 1
        inicio_ant_date = inicio_atual_date - datetime.timedelta(days=duracao)
        fim_ant_date = inicio_atual_date - datetime.timedelta(days=1)
        rotulo = "Últimos 7 dias"

    # Converter para Datetime ciente de Timezone abrangendo o dia inteiro
    tz = timezone.get_current_timezone()
    inicio_atual = timezone.make_aware(datetime.datetime.combine(inicio_atual_date, datetime.time.min), tz)
    fim_atual = timezone.make_aware(datetime.datetime.combine(fim_atual_date, datetime.time.max), tz)

    inicio_anterior = timezone.make_aware(datetime.datetime.combine(inicio_ant_date, datetime.time.min), tz)
    fim_anterior = timezone.make_aware(datetime.datetime.combine(fim_ant_date, datetime.time.max), tz)

    return inicio_atual, fim_atual, inicio_anterior, fim_anterior, rotulo


def calcular_variacao_percentual(atual: float, anterior: float) -> Dict[str, Any]:
    """Calcula a variação percentual entre o valor atual e o período anterior."""
    if anterior == 0:
        if atual == 0:
            return {"percentual": 0.0, "tendencia": "neutro", "texto": "0% vs período anterior"}
        return {"percentual": 100.0, "tendencia": "alta", "texto": "+100% vs período anterior"}
    
    variacao = ((atual - anterior) / anterior) * 100.0
    tendencia = "alta" if variacao > 0 else ("baixa" if variacao < 0 else "neutro")
    sinal = "+" if variacao > 0 else ""
    return {
        "percentual": round(variacao, 1),
        "tendencia": tendencia,
        "texto": f"{sinal}{variacao:.1f}% vs período anterior"
    }
