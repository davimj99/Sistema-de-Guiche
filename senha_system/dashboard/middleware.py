import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .models import ApiRequestLog

logger = logging.getLogger(__name__)


class ApiMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware não-intrusivo para monitoramento de métricas da API REST.
    Mede a latência e contabiliza chamadas em endpoints iniciados com /api/.
    Não armazena payloads, tokens, senhas ou cabeçalhos sensíveis.
    """

    def process_request(self, request):
        if request.path.startswith('/api/'):
            request._api_start_time = time.perf_counter()

    def process_response(self, request, response):
        if hasattr(request, '_api_start_time') and request.path.startswith('/api/'):
            try:
                duracao = (time.perf_counter() - request._api_start_time) * 1000.0  # ms
                
                # Obter IP mascarado ou direto de forma segura
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR')

                # Validação básica de IP para evitar erros de campo
                if ip and len(ip) > 45:
                    ip = ip[:45]

                # Endpoint normalizado (limitar até 255 caracteres)
                endpoint = request.path[:255]
                metodo = request.method[:10]
                status_code = response.status_code

                ApiRequestLog.objects.create(
                    endpoint=endpoint,
                    metodo=metodo,
                    status_code=status_code,
                    tempo_resposta_ms=round(duracao, 2),
                    ip_origem=ip,
                )
            except Exception as e:
                # Falhas de auditoria/log não devem afetar a entrega da resposta ao cliente
                logger.warning(f"Erro ao registrar métrica da API: {e}")

        return response
