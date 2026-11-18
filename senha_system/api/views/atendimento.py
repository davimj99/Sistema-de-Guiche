from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from atendimentos.models import Atendimento
from atendimentos.services import AtendimentoService
from api.filters import AtendimentoFilter
from api.serializers import (
    AtendimentoSerializer,
    AtendimentoIniciarSerializer,
    AtendimentoTransferirSerializer,
    SenhaModelSerializer,
)
class AtendimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento do ciclo de vida de atendimentos nos guichês.
    Requer autenticação (BasicAuth ou JWT) para todas as operações.
    Disponibiliza formulários interativos no Browsable API e suporte a filtros.
    """
    queryset = Atendimento.objects.all().select_related('senha').order_by('-id')
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [AtendimentoFilter, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['atendente', 'aluno', 'tipo', 'senha__prefixo']
    ordering_fields = ['id', 'inicio', 'fim', 'tipo', 'guiche', 'atendente']
    ordering = ['-id']

    @swagger_auto_schema(
        method='get',
        operation_summary="Instruções para Iniciar Atendimento",
        tags=['Atendimentos']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Iniciar Atendimento",
        request_body=AtendimentoIniciarSerializer,
        responses={201: AtendimentoSerializer},
        tags=['Atendimentos']
    )
    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def iniciar(self, request):
        """
        Inicia formalmente o atendimento de uma senha chamada.
        No Browsable API, disponibiliza o formulário interativo para POST.
        """
        if request.method == 'GET':
            return Response({
                "acao": "iniciar_atendimento",
                "descricao": "Envie 'senha_id' e 'guiche_id' via POST para iniciar o atendimento.",
                "tipos_atendimento": [t[0] for t in Atendimento.TIPOS_ATENDIMENTO],
                "exemplo_payload": {
                    "senha_id": 1,
                    "guiche_id": 1,
                    "atendente": "Rafael",
                    "aluno": "João Silva",
                    "tipo": "matricula"
                }
            })

        serializer = AtendimentoIniciarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        atendimento = AtendimentoService.iniciar_atendimento(
            senha_id=serializer.validated_data['senha_id'],
            guiche_id=serializer.validated_data['guiche_id'],
            atendente=serializer.validated_data.get('atendente'),
            aluno=serializer.validated_data.get('aluno'),
            tipo=serializer.validated_data.get('tipo'),
        )

        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Atendimento #{atendimento.id} iniciado.",
                "atendimento": AtendimentoSerializer(atendimento, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        method='get',
        operation_summary="Status do Atendimento para Finalização",
        tags=['Atendimentos']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Finalizar Atendimento",
        responses={200: AtendimentoSerializer},
        tags=['Atendimentos']
    )
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def finalizar(self, request, pk=None):
        """
        Encerra um atendimento em andamento.
        """
        if request.method == 'GET':
            try:
                atendimento = Atendimento.objects.get(id=int(pk))
                return Response({
                    "acao": "finalizar_atendimento",
                    "atendimento_id": atendimento.id,
                    "status_atual": "em_andamento" if atendimento.fim is None else "encerrado",
                    "instrucao": "Envie uma requisição POST para este endpoint para confirmar o encerramento."
                })
            except Atendimento.DoesNotExist:
                return Response(
                    {"status": "erro", "codigo": 404, "mensagem": f"Atendimento #{pk} não encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )

        atendimento = AtendimentoService.finalizar_atendimento(atendimento_id=int(pk))
        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Atendimento #{atendimento.id} finalizado.",
                "atendimento": AtendimentoSerializer(atendimento, context={'request': request}).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        method='get',
        operation_summary="Instruções para Transferência de Atendimento",
        tags=['Atendimentos']
    )
    @swagger_auto_schema(
        method='post',
        operation_summary="Transferir Atendimento para Outro Guichê",
        request_body=AtendimentoTransferirSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Atendimentos']
    )
    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def transferir(self, request):
        """
        Transfere uma senha em atendimento para outro guichê ativo.
        """
        if request.method == 'GET':
            return Response({
                "acao": "transferir_atendimento",
                "descricao": "Envie 'senha_id', 'guiche_origem_id' e 'guiche_destino_id' via POST.",
                "exemplo_payload": {
                    "senha_id": 1,
                    "guiche_origem_id": 1,
                    "guiche_destino_id": 2,
                    "motivo": "Encaminhamento para suporte especializado"
                }
            })

        serializer = AtendimentoTransferirSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        senha_id = request.data.get('senha_id')
        if not senha_id:
            return Response(
                {
                    "status": "erro",
                    "codigo": 400,
                    "mensagem": "O campo 'senha_id' é obrigatório para transferência.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        senha = AtendimentoService.transferir_atendimento(
            senha_id=int(senha_id),
            guiche_origem_id=serializer.validated_data['guiche_origem_id'],
            guiche_destino_id=serializer.validated_data['guiche_destino_id'],
            motivo=serializer.validated_data.get('motivo'),
        )

        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Senha {senha.prefixo}{senha.numero} transferida para guichê #{senha.guiche_id}.",
                "senha": SenhaModelSerializer(senha, context={'request': request}).data,
            },
            status=status.HTTP_200_OK
        )



