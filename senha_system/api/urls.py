from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from .routers import router

app_name = 'api'

urlpatterns = [
    # Catálogo e Índices
    path('', views.api_root, name='root'),
    path('v1/', views.api_root, name='v1_root'),

    # Endpoints Públicos de Operação (Totens, Painel TV) — Retrocompatibilidade Garantida
    path('v1/painel/', views.painel_api, name='painel'),
    path('v1/guiches/', views.guiches_api, name='guiches'),
    path('v1/filas/status/', views.status_fila_api, name='status_filas'),

    # Autenticação JWT e Básica (Tokens para Apps, Sistemas Externos e Operadores)
    path('v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/me/', views.user_profile_api, name='user_profile'),

    # Endpoints Estruturados via ViewSets & DRF Routers
    path('v1/', include(router.urls)),
]
