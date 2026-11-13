from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Permissão que concede leitura pública (GET, HEAD, OPTIONS) para totens e painéis,
    mas restringe mutações (POST, PUT, PATCH, DELETE) a administradores/equipe autenticados.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAtendenteOrAdmin(BasePermission):
    """
    Permissão para operadores de guichê, atendentes e administradores.
    Exige autenticação válida (via BasicAuth, JWT ou Session).
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_active)
        )


class IsSuperAdminUser(BasePermission):
    """
    Permissão estrita para superusuários do sistema.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
