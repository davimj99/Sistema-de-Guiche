from rest_framework import filters, viewsets
from rest_framework.response import Response

from accounts.models import Guiche
from api.filters import GuicheFilter
from api.permissions import IsAdminOrReadOnly
from api.serializers import GuicheSerializer
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



guiches_api = GuicheViewSet.as_view({'get': 'list', 'post': 'create'})

