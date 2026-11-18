from django.utils import timezone
from rest_framework.filters import BaseFilterBackend


class GuicheFilter(BaseFilterBackend):
    """
    Filtro para listagem de Guichês:
    - ?ativo=true|false : filtra pelo status ativo/inativo
    - ?nome=texto       : filtra pelo nome do guichê (case-insensitive)
    """

    def filter_queryset(self, request, queryset, view):
        ativo_param = request.query_params.get('ativo', None)
        if ativo_param is not None:
            if ativo_param.lower() in ['true', '1', 't', 'yes']:
                queryset = queryset.filter(ativo=True)
            elif ativo_param.lower() in ['false', '0', 'f', 'no']:
                queryset = queryset.filter(ativo=False)

        nome_param = request.query_params.get('nome', None)
        if nome_param:
            queryset = queryset.filter(nome__icontains=nome_param.strip())

        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'ativo',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por guichês ativos (true/false)',
                'schema': {'type': 'boolean'},
            },
            {
                'name': 'nome',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por parte do nome do guichê',
                'schema': {'type': 'string'},
            },
        ]


class SenhaFilter(BaseFilterBackend):
    """
    Filtro para listagem de Senhas:
    - ?status=espera|chamando|atendimento|finalizado : status da senha
    - ?tipo=normal|preferencial                     : tipo da senha
    - ?guiche=<id> ou ?guiche_id=<id>               : filtrar por guichê alocado
    - ?prefixo=A|P                                  : prefixo da senha
    - ?hoje=true|1                                  : senhas emitidas hoje
    - ?data=YYYY-MM-DD                              : senhas emitidas em data específica
    """

    def filter_queryset(self, request, queryset, view):
        # 1. Filtro por status
        status_param = request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.strip().lower())

        # 2. Filtro por tipo
        tipo_param = request.query_params.get('tipo', None)
        if tipo_param:
            queryset = queryset.filter(tipo=tipo_param.strip().lower())

        # 3. Filtro por guichê
        guiche_param = request.query_params.get('guiche', None) or request.query_params.get('guiche_id', None)
        if guiche_param:
            queryset = queryset.filter(guiche_id=guiche_param)

        # 4. Filtro por prefixo
        prefixo_param = request.query_params.get('prefixo', None)
        if prefixo_param:
            queryset = queryset.filter(prefixo__iexact=prefixo_param.strip())

        # 5. Filtro por data de hoje
        hoje_param = request.query_params.get('hoje', None)
        if hoje_param is not None and hoje_param.lower() in ['true', '1', 't', 'yes']:
            queryset = queryset.filter(criada_em__date=timezone.localdate())

        # 6. Filtro por data arbitrária (YYYY-MM-DD)
        data_param = request.query_params.get('data', None)
        if data_param:
            queryset = queryset.filter(criada_em__date=data_param.strip())

        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'status',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por status (espera, chamando, chamando_novamente, atendimento, finalizado)',
                'schema': {'type': 'string'},
            },
            {
                'name': 'tipo',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por tipo de senha (normal, preferencial)',
                'schema': {'type': 'string'},
            },
            {
                'name': 'guiche',
                'required': False,
                'in': 'query',
                'description': 'ID do guichê associado',
                'schema': {'type': 'integer'},
            },
            {
                'name': 'prefixo',
                'required': False,
                'in': 'query',
                'description': 'Prefixo da senha (A, P, etc.)',
                'schema': {'type': 'string'},
            },
            {
                'name': 'hoje',
                'required': False,
                'in': 'query',
                'description': 'Filtrar apenas senhas de hoje (true/false)',
                'schema': {'type': 'boolean'},
            },
            {
                'name': 'data',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por data específica (YYYY-MM-DD)',
                'schema': {'type': 'string'},
            },
        ]


class AtendimentoFilter(BaseFilterBackend):
    """
    Filtro para listagem de Atendimentos:
    - ?tipo=matricula|financeiro|...  : tipo do serviço atendido
    - ?atendente=nome                 : nome do atendente (parcial ou exato)
    - ?aluno=nome                     : nome do aluno (parcial)
    - ?guiche=<numero>                : número do guichê
    - ?senha_id=<id>                  : id da senha relacionada
    - ?finalizado=true|false          : atendimentos já concluídos ou em andamento
    - ?data=YYYY-MM-DD                : atendimentos finalizados em data específica
    """

    def filter_queryset(self, request, queryset, view):
        # 1. Filtro por tipo
        tipo_param = request.query_params.get('tipo', None)
        if tipo_param:
            queryset = queryset.filter(tipo__iexact=tipo_param.strip())

        # 2. Filtro por atendente
        atendente_param = request.query_params.get('atendente', None)
        if atendente_param:
            queryset = queryset.filter(atendente__icontains=atendente_param.strip())

        # 3. Filtro por aluno
        aluno_param = request.query_params.get('aluno', None)
        if aluno_param:
            queryset = queryset.filter(aluno__icontains=aluno_param.strip())

        # 4. Filtro por guichê
        guiche_param = request.query_params.get('guiche', None)
        if guiche_param:
            try:
                queryset = queryset.filter(guiche=int(guiche_param))
            except ValueError:
                pass

        # 5. Filtro por senha
        senha_param = request.query_params.get('senha', None) or request.query_params.get('senha_id', None)
        if senha_param:
            queryset = queryset.filter(senha_id=senha_param)

        # 6. Filtro por finalizado / em andamento
        finalizado_param = request.query_params.get('finalizado', None)
        if finalizado_param is not None:
            if finalizado_param.lower() in ['true', '1', 't', 'yes']:
                queryset = queryset.filter(fim__isnull=False)
            elif finalizado_param.lower() in ['false', '0', 'f', 'no']:
                queryset = queryset.filter(fim__isnull=True)

        # 7. Filtro por data
        data_param = request.query_params.get('data', None)
        if data_param:
            queryset = queryset.filter(fim__date=data_param.strip())

        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'tipo',
                'required': False,
                'in': 'query',
                'description': 'Tipo de atendimento (matricula, financeiro, etc.)',
                'schema': {'type': 'string'},
            },
            {
                'name': 'atendente',
                'required': False,
                'in': 'query',
                'description': 'Nome do atendente',
                'schema': {'type': 'string'},
            },
            {
                'name': 'aluno',
                'required': False,
                'in': 'query',
                'description': 'Nome do aluno',
                'schema': {'type': 'string'},
            },
            {
                'name': 'guiche',
                'required': False,
                'in': 'query',
                'description': 'Número do guichê',
                'schema': {'type': 'integer'},
            },
            {
                'name': 'senha_id',
                'required': False,
                'in': 'query',
                'description': 'ID da senha associada',
                'schema': {'type': 'integer'},
            },
            {
                'name': 'finalizado',
                'required': False,
                'in': 'query',
                'description': 'Filtrar por status finalizado (true/false)',
                'schema': {'type': 'boolean'},
            },
            {
                'name': 'data',
                'required': False,
                'in': 'query',
                'description': 'Data do atendimento finalizado (YYYY-MM-DD)',
                'schema': {'type': 'string'},
            },
        ]
