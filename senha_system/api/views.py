from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Guiche
from filas.models import Senha, Historico
from atendimentos.models import Atendimento
from filas.validators import FilaValidator
from filas.services import FilaService
from atendimentos.services import AtendimentoService
from api.permissions import IsAdminOrReadOnly, IsAtendenteOrAdmin
from api.throttles import TotemRateThrottle, PainelRateThrottle, ChamadaRateThrottle
from api.filters import GuicheFilter, SenhaFilter, AtendimentoFilter
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
# API ROOT INTERATIVA NAVEGÁVEL (BROWSABLE API)
# ============================================================
@swagger_auto_schema(
    method='get',
    operation_summary="Catálogo Interativo de Endpoints da API",
    operation_description=(
        "Página inicial interativa da API v1. Apresenta hyperlinks reais e clicáveis "
        "para navegação ponto a ponto na Browsable API do Django REST Framework."
    ),
    responses={200: ApiRootResponseSerializer},
    tags=['Catálogo']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Página inicial interativa da API REST (v1).
    Apresenta hyperlinks clicáveis para todos os recursos operacionais na Browsable API do DRF.
    """
    def res(name):
        try:
            return reverse(f"api:{name}", request=request, format=format)
        except Exception:
            try:
                return reverse(name, request=request, format=format)
            except Exception:
                return None

    endpoints = {
        "painel": res("painel"),
        "guiches": res("guiches-list") or res("guiches"),
        "filas": res("filas") or res("status_filas"),
        "senhas": res("senhas-list"),
        "atendimentos": res("atendimentos-list"),
        "status_filas": res("status_filas"),
        "auth_token": res("token_obtain_pair"),
        "auth_refresh": res("token_refresh"),
        "auth_me": res("user_profile"),
        "swagger": res("schema-swagger-ui"),
        "redoc": res("schema-redoc"),
    }

    data = {
        "nome": "API Sistema de Atendimento & Filas",
        "versao": "v1.0",
        "endpoints": {k: v for k, v in endpoints.items() if v is not None},
        "documentacao": (
            "Endpoints navegáveis via Django REST Framework Browsable API "
            "prontos para consumo por totens, TVs e sistemas externos."
        )
    }
    return Response(data)


# ============================================================
# ENDPOINTS PÚBLICOS DE OPERAÇÃO (TOTEM & PAINEL DE TV)
# ============================================================
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
# VIEWSETS ORGANIZADOS POR DOMÍNIO & BROWSABLE API INTERATIVA
# ============================================================
class GuicheViewSet(viewsets.ModelViewSet):
    """
    ViewSet navegável para consulta e gerenciamento de Guichês de Atendimento.
    Leitura pública para totens e painéis; modificação restrita a administradores.
    Disponibiliza formulários interativos no Browsable API e suporte a filtros.
    """
    queryset = Guiche.objects.all().order_by('id')
    serializer_class = GuicheSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [GuicheFilter, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['id', 'nome', 'ativo']
    ordering = ['id']

    def list(self, request, *args, **kwargs):
        """
        Retorna a lista de guichês no contrato consumido por totens e painéis,
        com hyperlinks individuais para cada guichê.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "sucesso",
            "total": len(serializer.data),
            "guiches": serializer.data
        })


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


# Alias de compatibilidade com views legadas
guiches_api = GuicheViewSet.as_view({'get': 'list', 'post': 'create'})
