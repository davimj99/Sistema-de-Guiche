from rest_framework.routers import DefaultRouter
from .views import GuicheViewSet, SenhaViewSet, AtendimentoViewSet

# Router central da API REST
router = DefaultRouter()

# Registro de ViewSets por domínio
router.register(r'routers/guiches', GuicheViewSet, basename='guiches-viewset')
router.register(r'senhas', SenhaViewSet, basename='senhas-viewset')
router.register(r'atendimentos', AtendimentoViewSet, basename='atendimentos-viewset')

urlpatterns = router.urls
