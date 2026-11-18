from rest_framework.authentication import BasicAuthentication


class CustomBasicAuthentication(BasicAuthentication):
    """
    Autenticação HTTP Basic baseada no Django User model oficial.
    Não armazena senhas manualmente nem altera o hashing de segurança nativo do Django.
    """
    www_authenticate_realm = "Sistema de Guiche API"
