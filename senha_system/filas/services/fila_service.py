from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import Guiche
from filas.models import Senha, ControleFila, Historico
from filas.validators import FilaValidator, SenhaValidator


class FilaService:
    """
    Service centralizador das regras de negócio de Filas, Senhas e Chamadas.
    Garante consistência concorrente via transações atômicas e locks pessimistas.
    """

    PREFIXOS = {
        "normal": "A",
        "preferencial": "P",
    }

    @classmethod
    @transaction.atomic
    def emitir_senha(cls, tipo: str = "normal") -> Senha:
        """
        Emite uma nova senha (normal ou preferencial) para o dia atual de forma consistente.
        """
        tipo_validado = FilaValidator.validar_tipo_fila(tipo)
        hoje = timezone.localdate()
        prefixo = cls.PREFIXOS.get(tipo_validado, "A")

        # Busca a última senha do tipo emitida hoje para calcular o próximo número
        ultima = (
            Senha.objects
            .select_for_update()
            .filter(tipo=tipo_validado, criada_em__date=hoje)
            .order_by("-numero")
            .first()
        )
        proximo_numero = 1 if not ultima else ultima.numero + 1

        senha = Senha.objects.create(
            numero=proximo_numero,
            prefixo=prefixo,
            tipo=tipo_validado,
            status="espera"
        )
        return senha

    @classmethod
    @transaction.atomic
    def chamar_proxima(cls, guiche_id: int) -> Optional[Senha]:
        """
        Executa a chamada da próxima senha para um guichê ativo.
        Alterna regra de atendimento 1 Preferencial : 2 Normais com fallback inteligente.
        Finaliza a chamada anterior se houver e atualiza o histórico e controle de fila.
        """
        guiche = FilaValidator.validar_guiche_ativo(guiche_id)
        hoje = timezone.localdate()

        # Garante a existência do registro de controle com lock de linha
        controle = ControleFila.objects.select_for_update().first()
        if not controle:
            controle = ControleFila.objects.create(contador=0)

        # Finaliza a chamada anterior deste guichê
        senha_anterior = (
            Senha.objects
            .select_for_update()
            .filter(guiche=guiche, status="chamando")
            .order_by("-id")
            .first()
        )
        if senha_anterior:
            senha_anterior.status = "finalizado"
            senha_anterior.save(update_fields=["status"])
            Historico.objects.create(
                senha=senha_anterior,
                guiche=guiche,
                acao="finalizado"
            )

        # Verifica se há senhas aguardando atendimento
        tem_espera = Senha.objects.filter(status="espera", criada_em__date=hoje).exists()
        if not tem_espera:
            return None

        # Regra de alternância: 1 Preferencial a cada 3 chamadas (quando resto da divisão por 3 == 1)
        proximo_contador = controle.contador + 1
        tipo_prioritario = "preferencial" if proximo_contador % 3 == 1 else "normal"
        outro_tipo = "normal" if tipo_prioritario == "preferencial" else "preferencial"

        # Tenta obter senha do tipo prioritário
        senha = (
            Senha.objects
            .select_for_update()
            .filter(status="espera", tipo=tipo_prioritario, criada_em__date=hoje)
            .order_by("criada_em", "id")
            .first()
        )

        # Fallback para o outro tipo de senha caso a prioritária não esteja em espera
        if not senha:
            senha = (
                Senha.objects
                .select_for_update()
                .filter(status="espera", tipo=outro_tipo, criada_em__date=hoje)
                .order_by("criada_em", "id")
                .first()
            )

        if not senha:
            return None

        # Valida transição
        SenhaValidator.validar_transicao_status(senha, "chamando")

        senha.status = "chamando"
        senha.guiche = guiche
        senha.save(update_fields=["status", "guiche"])

        Historico.objects.create(
            senha=senha,
            guiche=guiche,
            acao="chamando"
        )

        controle.contador = proximo_contador
        controle.save(update_fields=["contador"])

        return senha

    @classmethod
    @transaction.atomic
    def chamar_novamente(cls, guiche_id: int) -> Optional[Senha]:
        """
        Rechama a senha atual vinculada a um guichê e registra no histórico.
        """
        guiche = FilaValidator.validar_guiche_ativo(guiche_id)

        senha = (
            Senha.objects
            .select_for_update()
            .filter(guiche=guiche, status="chamando")
            .order_by("-id")
            .first()
        )

        if not senha:
            return None

        Historico.objects.create(
            senha=senha,
            guiche=guiche,
            acao="chamando_novamente"
        )
        return senha

    @classmethod
    def obter_status_filas(cls) -> Dict[str, Any]:
        """
        Calcula as métricas operacionais consolidadas das filas do dia.
        """
        hoje = timezone.localdate()
        senhas_hoje = Senha.objects.filter(criada_em__date=hoje)

        espera_normal = senhas_hoje.filter(status="espera", tipo="normal").count()
        espera_pref = senhas_hoje.filter(status="espera", tipo="preferencial").count()
        chamando = senhas_hoje.filter(status="chamando").count()
        finalizadas = senhas_hoje.filter(status="finalizado").count()

        return {
            "status": "sucesso",
            "data": hoje.strftime("%Y-%m-%d"),
            "total_emitidas_hoje": senhas_hoje.count(),
            "em_espera": {
                "total": espera_normal + espera_pref,
                "normal": espera_normal,
                "preferencial": espera_pref,
            },
            "chamando": chamando,
            "finalizadas": finalizadas,
        }

    @classmethod
    def obter_estado_painel(cls) -> Dict[str, Any]:
        """
        Retorna os dados em tempo real consolidados para o Painel de TV / Monitores.
        """
        hoje = timezone.localdate()

        ultima_chamada = (
            Historico.objects
            .filter(acao__in=["chamando", "chamando_novamente"])
            .select_related("senha", "guiche")
            .order_by("-id")
            .first()
        )

        ultimas_chamadas = list(
            Historico.objects
            .filter(acao__in=["chamando", "chamando_novamente"])
            .select_related("senha", "guiche")
            .order_by("-id")[:10]
        )

        fila_espera = list(
            Senha.objects
            .filter(status="espera", criada_em__date=hoje)
            .order_by("criada_em", "id")[:15]
        )

        dados_ultima = None
        if ultima_chamada and ultima_chamada.senha:
            dados_ultima = {
                "senha": f"{ultima_chamada.senha.prefixo}{ultima_chamada.senha.numero}",
                "tipo": ultima_chamada.senha.tipo,
                "guiche": ultima_chamada.guiche.nome if ultima_chamada.guiche else "",
                "chamada_id": ultima_chamada.id,
                "acao": ultima_chamada.acao,
                "hora": timezone.localtime(ultima_chamada.criada_em).strftime("%H:%M:%S") if hasattr(ultima_chamada, "criada_em") and ultima_chamada.criada_em else None,
            }

        return {
            "status": "sucesso",
            "timestamp": timezone.now().isoformat(),
            "ultima": dados_ultima,
            "ultimas": [
                {
                    "senha": f"{h.senha.prefixo}{h.senha.numero}" if h.senha else "",
                    "guiche": h.guiche.nome if h.guiche else "",
                    "chamada_id": h.id,
                    "acao": h.acao,
                }
                for h in ultimas_chamadas
            ],
            "fila": [
                {
                    "senha": f"{s.prefixo}{s.numero}",
                    "tipo": s.tipo,
                    "posicao": idx + 1,
                }
                for idx, s in enumerate(fila_espera)
            ]
        }
