from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import Guiche
from filas.models import Senha, Historico
from atendimentos.models import Atendimento
from filas.services import FilaService
from atendimentos.services import AtendimentoService
from api.permissions import IsAdminOrReadOnly, IsAtendenteOrAdmin
from api.throttles import TotemRateThrottle, PainelRateThrottle, ChamadaRateThrottle
from .serializers import (
    ApiRootResponseSerializer,
    PainelResponseSerializer,
    GuichesListResponseSerializer,
    StatusFilaResponseSerializer,
    UserProfileSerializer,
    GuicheSerializer,
    SenhaModelSerializer,
    SenhaEmitirSerializer,
    ChamadaProximaSerializer,
    ChamadaNovamenteSerializer,
    AtendimentoSerializer,
    AtendimentoIniciarSerializer,
    AtendimentoTransferirSerializer,
)


# ============================================================
# ENDPOINTS LEGADOS / OPERACIONAIS (100% RETROCOMPATÍVEIS)
# ============================================================
@swagger_auto_schema(
    method='get',
    operation_summary="Catálogo de Endpoints da API",
    operation_description="Retorna o mapa de navegação dos endpoints públicos, autenticados e routers da API v1.",
    responses={200: ApiRootResponseSerializer},
    tags=['Catálogo']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Índice da API v1 do Sistema de Atendimento.
    Documentação navegável dos endpoints públicos e operacionais.
    """
    data = {
        "nome": "API Sistema de Atendimento & Filas",
        "versao": "v1.0",
        "endpoints": {
            "painel": "/api/v1/painel/",
            "guiches": "/api/v1/guiches/",
            "status_filas": "/api/v1/filas/status/",
            "auth_token": "/api/v1/auth/token/",
            "auth_refresh": "/api/v1/auth/token/refresh/",
            "auth_me": "/api/v1/auth/me/",
            "senhas_router": "/api/v1/senhas/",
            "atendimentos_router": "/api/v1/atendimentos/",
            "guiches_router": "/api/v1/routers/guiches/",
            "swagger": "/swagger/",
            "redoc": "/redoc/",
        },
        "documentacao": "Endpoints em formato JSON REST prontos para consumo por totens, TVs e sistemas externos."
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Estado em Tempo Real do Painel de TV",
    operation_description=(
        "Retorna os dados ao vivo para exibição nos monitores da sala de espera:\n"
        "- Última senha chamada com guichê e tipo\n"
        "- Histórico recente das últimas 10 chamadas\n"
        "- Fila de espera do dia atual"
    ),
    responses={200: PainelResponseSerializer},
    tags=['Painel & Totem']
)
@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PainelRateThrottle])
def painel_api(request):
    """
    Retorna o estado em tempo real do painel de chamadas consumindo o FilaService.
    """
    data = FilaService.obter_estado_painel()
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Listar Guichês Ativos",
    operation_description="Retorna a lista de todos os guichês de atendimento ativos cadastrados no sistema.",
    responses={200: GuichesListResponseSerializer},
    tags=['Guichês']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def guiches_api(request):
    """
    Retorna a lista de guichês de atendimento cadastrados e ativos.
    Executa apenas 1 query eficiente no banco.
    """
    guiches = list(Guiche.objects.filter(ativo=True).order_by("id"))

    data = {
        "status": "sucesso",
        "total": len(guiches),
        "guiches": [
            {
                "id": g.id,
                "nome": g.nome,
                "ativo": g.ativo,
            }
            for g in guiches
        ]
    }
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Status e Métricas das Filas do Dia",
    operation_description="Retorna métricas em tempo real das filas do dia atual via FilaService.",
    responses={200: StatusFilaResponseSerializer},
    tags=['Filas']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def status_fila_api(request):
    """
    Retorna métricas em tempo real das filas do dia.
    """
    data = FilaService.obter_status_filas()
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary="Perfil do Usuário Autenticado",
    operation_description="Retorna os dados do usuário autenticado via BasicAuthentication ou Bearer JWT.",
    responses={200: UserProfileSerializer},
    tags=['Autenticação']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Endpoint autenticado via BasicAuth ou Bearer JWT.
    Retorna o perfil do usuário atualmente autenticado.
    """
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    }
    return Response(data)


# ============================================================
# VIEWSETS ORGANIZADOS POR ROUTER
# ============================================================
class GuicheViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consulta e gerenciamento de Guichês de Atendimento.
    Leitura pública para totens e painéis; modificação restrita a administradores.
    """
    queryset = Guiche.objects.all().order_by('id')
    serializer_class = GuicheSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        apenas_ativos = self.request.query_params.get('ativo', None)
        if apenas_ativos is not None:
            ativo_bool = apenas_ativos.lower() in ['true', '1', 't']
            queryset = queryset.filter(ativo=ativo_bool)
        return queryset


class SenhaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de senhas e ações operacionais de atendimento.
    Ações de emissão são públicas (com controle de throttling para totens),
    enquanto ações de chamada exigem operador autenticado.
    """
    queryset = Senha.objects.all().select_related('guiche').order_by('-id')
    serializer_class = SenhaModelSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        hoje = timezone.localdate()
        dia_param = self.request.query_params.get('hoje', None)
        if dia_param is not None and dia_param.lower() in ['true', '1', 't']:
            queryset = queryset.filter(criada_em__date=hoje)
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @swagger_auto_schema(
        operation_summary="Emitir Nova Senha",
        request_body=SenhaEmitirSerializer,
        responses={201: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        throttle_classes=[TotemRateThrottle]
    )
    def emitir(self, request):
        """
        Emite uma nova senha para atendimento no totem.
        Suporta tipo 'normal' ou 'preferencial'.
        """
        serializer = SenhaEmitirSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tipo = serializer.validated_data.get('tipo', 'normal')

        senha = FilaService.emitir_senha(tipo=tipo)
        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Senha {senha.prefixo}{senha.numero} emitida com sucesso.",
                "senha": SenhaModelSerializer(senha).data,
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary="Chamar Próxima Senha",
        request_body=ChamadaProximaSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        throttle_classes=[ChamadaRateThrottle]
    )
    def chamar_proxima(self, request):
        """
        Chama a próxima senha aguardando na fila para o guichê informado.
        Requer autenticação do operador (BasicAuth ou JWT).
        """
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
                "senha": SenhaModelSerializer(senha).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Rechamar Senha Atual",
        request_body=ChamadaNovamenteSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Senhas']
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        throttle_classes=[ChamadaRateThrottle]
    )
    def chamar_novamente(self, request):
        """
        Rechama a senha atual que está em atendimento no guichê informado.
        Requer autenticação do operador.
        """
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
                "senha": SenhaModelSerializer(senha).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Listar Senhas em Espera do Dia",
        responses={200: SenhaModelSerializer(many=True)},
        tags=['Senhas']
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def espera(self, request):
        """
        Lista as senhas atualmente em espera para o dia de hoje.
        """
        hoje = timezone.localdate()
        senhas = Senha.objects.filter(status="espera", criada_em__date=hoje).order_by("criada_em", "id")
        return Response(SenhaModelSerializer(senhas, many=True).data)


class AtendimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento do ciclo de vida de atendimentos nos guichês.
    Requer autenticação (BasicAuth ou JWT) para todas as operações.
    """
    queryset = Atendimento.objects.all().select_related('senha').order_by('-id')
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Iniciar Atendimento",
        request_body=AtendimentoIniciarSerializer,
        responses={201: AtendimentoSerializer},
        tags=['Atendimentos']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def iniciar(self, request):
        """
        Inicia formalmente o atendimento de uma senha chamada.
        """
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
                "atendimento": AtendimentoSerializer(atendimento).data,
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary="Finalizar Atendimento",
        responses={200: AtendimentoSerializer},
        tags=['Atendimentos']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def finalizar(self, request, pk=None):
        """
        Encerra um atendimento em andamento.
        """
        atendimento = AtendimentoService.finalizar_atendimento(atendimento_id=int(pk))
        return Response(
            {
                "status": "sucesso",
                "mensagem": f"Atendimento #{atendimento.id} finalizado.",
                "atendimento": AtendimentoSerializer(atendimento).data,
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Transferir Atendimento para Outro Guichê",
        request_body=AtendimentoTransferirSerializer,
        responses={200: SenhaModelSerializer},
        tags=['Atendimentos']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def transferir(self, request):
        """
        Transfere uma senha em atendimento para outro guichê ativo.
        """
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
                "senha": SenhaModelSerializer(senha).data,
            },
            status=status.HTTP_200_OK
        )
