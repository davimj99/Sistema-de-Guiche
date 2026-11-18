from django.db import models


class ApiRequestLog(models.Model):
    """
    Registro estruturado de requisições recebidas pela API REST.
    Permite monitoramento de volumetria, códigos HTTP, endpoints mais acessados
    e tempo médio de resposta sem armazenar dados sensíveis, tokens ou credenciais.
    """
    endpoint = models.CharField(max_length=255, db_index=True, verbose_name="Endpoint")
    metodo = models.CharField(max_length=10, db_index=True, verbose_name="Método HTTP")
    status_code = models.PositiveSmallIntegerField(db_index=True, verbose_name="Código HTTP")
    tempo_resposta_ms = models.FloatField(default=0.0, verbose_name="Tempo de Resposta (ms)")
    ip_origem = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de Origem")
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Data/Hora")

    class Meta:
        db_table = "dashboard_api_request_log"
        verbose_name = "Log de Requisição da API"
        verbose_name_plural = "Logs de Requisições da API"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["criado_em", "status_code"]),
            models.Index(fields=["criado_em", "metodo"]),
            models.Index(fields=["endpoint", "criado_em"]),
        ]

    def __str__(self):
        return f"{self.metodo} {self.endpoint} - {self.status_code} ({self.tempo_resposta_ms:.1f}ms)"
