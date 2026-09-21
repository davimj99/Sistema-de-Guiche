import re


def normalizar_texto(texto):
    texto = texto.lower().strip()

    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }

    for original, substituto in substituicoes.items():
        texto = texto.replace(original, substituto)

    texto = re.sub(r"\s+", " ", texto)

    return texto


def obter_resposta(pergunta):
    pergunta = normalizar_texto(pergunta)

    if not pergunta:
        return {
            "resposta": (
                "Digite uma dúvida para que eu possa ajudar."
            )
        }

    # SAUDAÇÃO
    if any(palavra in pergunta for palavra in [
        "oi",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "ajuda",
    ]):
        return {
            "resposta": (
                "Olá! Sou o Assistente ISCON. "
                "Posso ajudar você com dúvidas sobre o Sistema de Guichê."
            ),
            "sugestoes": [
                "Como chamar a próxima senha?",
                "Como chamar novamente?",
                "A senha não aparece na TV",
                "A impressora não está funcionando",
            ],
        }

    # PRÓXIMA SENHA
    if any(palavra in pergunta for palavra in [
        "proxima senha",
        "chamar proxima",
        "chamar senha",
        "proxima",
    ]):
        return {
            "resposta": (
                "Para chamar a próxima senha, utilize o botão "
                "\"Chamar Próxima\" no seu guichê. "
                "O sistema selecionará a próxima senha disponível "
                "na fila de atendimento."
            ),
            "sugestoes": [
                "Como chamar novamente?",
                "O que acontece quando a fila está vazia?",
            ],
        }

    # CHAMAR NOVAMENTE
    if any(palavra in pergunta for palavra in [
        "chamar novamente",
        "chamar de novo",
        "repetir senha",
        "repetir chamada",
    ]):
        return {
            "resposta": (
                "Para repetir a chamada da senha atual, utilize o botão "
                "\"Chamar Novamente\". O sistema repetirá a senha "
                "e o guichê no painel de atendimento."
            ),
            "sugestoes": [
                "Como chamar a próxima senha?",
                "A senha não aparece na TV",
            ],
        }

    # PREFERENCIAL
    if any(palavra in pergunta for palavra in [
        "preferencial",
        "preferencialmente",
        "senha preferencial",
    ]):
        return {
            "resposta": (
                "As senhas preferenciais são tratadas pelo sistema "
                "de acordo com a lógica configurada para a fila. "
                "Quando houver uma senha preferencial disponível, "
                "ela poderá ser chamada conforme a prioridade definida."
            ),
        }

    # FILA VAZIA
    if any(palavra in pergunta for palavra in [
        "fila vazia",
        "fila esta vazia",
        "nao tem senha",
        "sem senha",
        "nenhuma senha",
    ]):
        return {
            "resposta": (
                "Se não houver senhas aguardando, o sistema não terá "
                "uma nova senha para chamar. Aguarde a entrada de "
                "novos atendimentos antes de tentar novamente."
            ),
        }

    # TV / PAINEL
    if any(palavra in pergunta for palavra in [
        "tv",
        "painel",
        "senha nao aparece",
        "senha nao esta aparecendo",
        "nao aparece na tv",
    ]):
        return {
            "resposta": (
                "Se a senha chamada não aparecer na TV, verifique "
                "primeiro se o painel está aberto e conectado ao "
                "sistema. Depois, tente utilizar \"Chamar Novamente\". "
                "Se o problema continuar, acione o suporte técnico."
            ),
            "sugestoes": [
                "Como chamar novamente?",
                "A impressora não está funcionando",
            ],
        }

    # IMPRESSORA
    if any(palavra in pergunta for palavra in [
        "impressora",
        "imprimir",
        "nao imprime",
        "nao esta imprimindo",
        "papel",
    ]):
        return {
            "resposta": (
                "Se a impressora de senhas não estiver funcionando, "
                "verifique se ela está ligada, conectada ao computador "
                "e possui papel. Se o problema continuar, entre em "
                "contato com o suporte técnico."
            ),
        }

    # GUICHÊ
    if any(palavra in pergunta for palavra in [
        "guiche",
        "guiches",
        "atendente",
    ]):
        return {
            "resposta": (
                "Cada guichê representa um ponto de atendimento. "
                "O funcionário deve utilizar as opções disponíveis "
                "no painel para chamar e repetir senhas."
            ),
        }

    # ATENDIMENTO
    if any(palavra in pergunta for palavra in [
        "atendimento",
        "atender aluno",
        "finalizar atendimento",
        "atendimento realizado",
    ]):
        return {
            "resposta": (
                "Durante o atendimento, utilize o guichê para chamar "
                "a senha correspondente. Os registros de atendimento "
                "podem ser consultados posteriormente pelos usuários "
                "com permissão."
            ),
        }

    # RELATÓRIO
    if any(palavra in pergunta for palavra in [
        "relatorio",
        "relatorios",
        "relatorio de atendimento",
        "historico",
    ]):
        return {
            "resposta": (
                "O relatório de atendimentos permite consultar os "
                "registros realizados pelo sistema. O acesso é "
                "restrito aos usuários autorizados."
            ),
        }

    # PROBLEMA
    if any(palavra in pergunta for palavra in [
        "erro",
        "problema",
        "travou",
        "nao funciona",
        "não funciona",
    ]):
        return {
            "resposta": (
                "Vamos verificar. Primeiro identifique qual parte "
                "do sistema apresenta o problema: guichê, fila, "
                "TV/painel ou impressora. Se o problema persistir, "
                "entre em contato com o suporte técnico."
            ),
            "sugestoes": [
                "A senha não aparece na TV",
                "A impressora não está funcionando",
                "A fila está vazia",
            ],
        }

    # OBRIGADO
    if any(palavra in pergunta for palavra in [
        "obrigado",
        "obrigada",
        "valeu",
    ]):
        return {
            "resposta": (
                "Por nada! Estou disponível para ajudar com o "
                "Sistema de Guichê."
            ),
        }

    # NÃO ENCONTRADO
    return {
        "resposta": (
            "Ainda não encontrei uma orientação específica para "
            "essa dúvida. Tente perguntar de outra forma ou escolha "
            "uma das opções abaixo."
        ),
        "sugestoes": [
            "Como chamar a próxima senha?",
            "Como chamar novamente?",
            "A senha não aparece na TV",
            "A impressora não está funcionando",
        ],
    }