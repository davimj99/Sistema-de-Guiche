from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Guiche
from filas.models import Senha
from filas.validators import FilaValidator
from filas.services import FilaService
from api.filters import SenhaFilter
from api.permissions import IsAdminOrReadOnly
from api.throttles import TotemRateThrottle, ChamadaRateThrottle
from api.serializers import (
    SenhaModelSerializer,
    SenhaEmitirSerializer,
    ChamadaProximaSerializer,
    ChamadaNovamenteSerializer,
)
class SenhaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consulta de senhas e ações operacionais de atendimento.
    Ações de emissão são públicas com formulário interativo no Browsable API;
    ações de chamada exigem operador autenticado.
    Suporta filtros por status, tipo, guichê, hoje, data e busca textual.
    """
    queryset = Senha.objects.all().select_related('guiche').order_by('-id')
    serializer_class = SenhaModelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SenhaFilter, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prefixo', 'guiche__nome', 'status', 'tipo']
    ordering_fields = ['id', 'criada_em', 'numero', 'status', 'tipo']
    ordering = ['-id']

    @swagger_auto_schema(
        method='get',
        operation_summary="Instruções para Emissão de Senha",
        tags=['Senhas']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Emitir Nova Senha",
        request_body=SenhaEmitirSerializer,
        responses={201: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['get', 'post'],
        permission_classes=[AllowAny],
        throttle_classes=[TotemRateThrottle]
    )
    def emitir(self, request):
        """
        Emite uma nova senha para atendimento no totem.
        No Browsable API, exibe o formulário interativo para POST.
        """
        if request.method == 'GET':
            return Response({
                "acao": "emitir_senha",
                "descricao": "Informe 'tipo' ('normal' ou 'preferencial') via POST para emitir uma nova senha no totem.",
                "tipos_suportados": list(FilaValidator.TIPOS_PERMITIDOS),
                "exemplo_payload": {"tipo": "normal"}
            })

        serializer = SenhaEmitirSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tipo = serializer.validated_data.get('tipo', 'normal')

        senha = FilaService.emitir_senha(tipo=tipo)
        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Senha {senha.prefixo}{senha.numero} emitida com sucesso.",
                "senha": SenhaModelSerializer(senha, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        method='get',
        operation_summary="Instruções para Chamar Próxima Senha",
        tags=['Senhas']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Chamar Próxima Senha",
        request_body=ChamadaProximaSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['get', 'post'],
        permission_classes=[IsAuthenticated],
        throttle_classes=[ChamadaRateThrottle]
    )
    def chamar_proxima(self, request):
        """
        Chama a próxima senha aguardando na fila para o guichê informado.
        Requer autenticação do operador (BasicAuth ou JWT).
        """
        if request.method == 'GET':
            guiches_ativos = list(Guiche.objects.filter(ativo=True).values("id", "nome"))
            return Response({
                "acao": "chamar_proxima",
                "descricao": "Envie 'guiche_id' via POST para chamar a próxima senha da fila.",
                "guiches_ativos": guiches_ativos,
                "exemplo_payload": {"guiche_id": guiches_ativos[0]["id"] if guiches_ativos else 1}
            })

        serializer = ChamadaProximaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guiche_id = serializer.validated_data['guiche_id']

        senha = FilaService.chamar_proxima(guiche_id=guiche_id)
        if not senha:
            return Response(
                {
                    "status": "sucesso",
                    "mensagem": "Não há senhas aguardando na fila no momento.",
                    "senha": None,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Senha {senha.prefixo}{senha.numero} chamada com sucesso.",
                "senha": SenhaModelSerializer(senha, context={'request': request}).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        method='get',
        operation_summary="Instruções para Rechamar Senha",
        tags=['Senhas']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Rechamar Senha Atual",
        request_body=ChamadaNovamenteSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['get', 'post'],
        permission_classes=[IsAuthenticated],
        throttle_classes=[ChamadaRateThrottle]
    )
    def chamar_novamente(self, request):
        """
        Rechama a senha atual que está em atendimento no guichê informado.
        Requer autenticação do operador.
        """
        if request.method == 'GET':
            return Response({
                "acao": "chamar_novamente",
                "descricao": "Envie 'guiche_id' via POST para rechamar a senha atual do guichê.",
                "exemplo_payload": {"guiche_id": 1}
            })

        serializer = ChamadaNovamenteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guiche_id = serializer.validated_data['guiche_id']

        senha = FilaService.chamar_novamente(guiche_id=guiche_id)
        if not senha:
            return Response(
                {
                    "status": "erro",
                    "codigo": 404,
                    "mensagem": "Nenhuma senha em chamada ativa encontrada para este guichê.",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Senha {senha.prefixo}{senha.numero} rechamada com sucesso.",
                "senha": SenhaModelSerializer(senha, context={'request': request}).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        method='get',
        operation_summary="Listar Senhas em Espera do Dia",
        responses={200: SenhaModelSerializer(many=True)},
        tags=['Senhas']
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def espera(self, request):
        """
        Lista as senhas atualmente em espera para o dia de hoje com links navegáveis.
        """
        hoje = timezone.localdate()
        senhas = Senha.objects.filter(status="espera", criada_em__date=hoje).order_by("criada_em", "id")
        return Response(SenhaModelSerializer(senhas, many=True, context={'request': request}).data)



