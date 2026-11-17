from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


def is_staff_or_admin(user):
    """Verifica se o usuário possui perfil administrativo ou de equipe."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_dashboard_required(view_func):
    """
    Decorador para páginas HTML do Dashboard Administrativo.
    Se não autenticado, redireciona para accounts:login.
    Se autenticado mas sem perfil administrativo, exibe mensagem e redireciona ou nega acesso.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Acesso restrito: você precisa de perfil administrativo para acessar o Painel de Gestão.")
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_api_required(view_func):
    """
    Decorador para endpoints JSON/AJAX consumidos pelo Dashboard.
    Retorna JSON com código HTTP apropriado se não autorizado.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "erro", "codigo": 401, "mensagem": "Autenticação requerida."}, status=401)
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({"status": "erro", "codigo": 403, "mensagem": "Permissão negada."}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
