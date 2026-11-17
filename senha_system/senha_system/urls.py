"""
URL configuration for senha_system project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ============================================================
# CONFIGURAÇÃO DO SWAGGER / OPENAPI (drf-yasg)
# ============================================================
schema_view = get_schema_view(
    openapi.Info(
        title="API Sistema de Atendimento & Guichês - ISCON",
        default_version="v1",
        description=(
            "Documentação interativa dos serviços e APIs do Sistema de Senhas e Atendimento da Faculdade ISCON.\n\n"
            "Permite o consumo seguro por totens de autoatendimento, monitores de TV, terminais de chamada e integrações externas.\n\n"
            "Para testar endpoints protegidos por autenticação JWT, utilize o botão **Authorize** no topo e insira: `Bearer <seu_token_jwt>`."
        ),
        contact=openapi.Contact(email="ti@iscon.edu.br"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('filas/', include('filas.urls')),
    path('painel/', include('painel.urls')),
    path('atendimentos/', include('atendimentos.urls')),
    path("epis/", include("epis.urls")),
    path('wifi/', include('wifi.urls')),
    path('api/', include('api.urls')),

    # Documentação Swagger & OpenAPI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media manualmente, funciona mesmo com DEBUG=False
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
