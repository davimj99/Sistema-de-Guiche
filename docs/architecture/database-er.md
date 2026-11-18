# Modelo entidade-relacionamento

Diagrama derivado das classes `models.Model` atuais em `accounts`, `filas`, `atendimentos`, `wifi`, `epis` e `dashboard`. Campos são resumidos para leitura; PKs `id` são implícitas quando não declaradas. Relações para `auth.User` correspondem ao usuário padrão do Django. Migrations podem conter evolução histórica; este diagrama descreve o estado atual dos Models.

```mermaid
erDiagram
    GUICHE {
        bigint id PK
        varchar nome
        boolean ativo
    }
    SENHA {
        bigint id PK
        varchar prefixo
        int numero
        varchar tipo
        varchar status
        bigint guiche_id FK
        datetime criada_em
    }
    CONTROLE_FILA {
        bigint id PK
        int contador
    }
    HISTORICO {
        bigint id PK
        bigint senha_id FK
        bigint guiche_id FK
        varchar acao
        datetime criada_em
    }
    ATENDIMENTO {
        bigint id PK
        bigint senha_id FK
        varchar atendente
        varchar aluno
        int guiche
        varchar tipo
        time inicio
        datetime fim
    }
    PROPAGANDA {
        bigint id PK
        varchar titulo
        varchar imagem
        varchar video
        boolean ativa
        datetime criada_em
    }
    CHATBOT_MENSAGEM {
        bigint id PK
        bigint usuario_id FK
        text pergunta
        text resposta
        datetime criado_em
    }
    SOLICITACAO_WIFI {
        bigint id PK
        varchar protocolo UK
        varchar nome_aluno
        varchar matricula
        varchar curso
        varchar email
        varchar dispositivo
        text motivo
        varchar status
        text observacao_ti
        datetime criado_em
        datetime atualizado_em
    }
    ACESSO_WIFI {
        bigint id PK
        bigint solicitacao_id FK, UK
        varchar ssid
        varchar usuario
        varchar senha
        boolean ativo
        datetime criado_em
        datetime expira_em
    }
    FUNCIONARIO {
        bigint id PK
        varchar nome
        varchar matricula UK
        varchar setor
        varchar cargo
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }
    EPI {
        bigint id PK
        varchar nome
        varchar codigo UK
        varchar categoria
        text descricao
        varchar unidade
        int quantidade_estoque
        int estoque_minimo
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }
    ENTREGA_EPI {
        bigint id PK
        bigint funcionario_id FK
        bigint epi_id FK
        varchar funcionario_nome
        varchar epi_nome
        int quantidade
        date data_entrega
        date data_proxima_troca
        text observacao
        datetime criado_em
    }
    API_REQUEST_LOG {
        bigint id PK
        varchar endpoint
        varchar metodo
        int status_code
        float tempo_resposta_ms
        ip ip_origem
        datetime criado_em
    }
    AUTH_USER {
        bigint id PK
    }
    GUICHE o|--o{ SENHA : associado
    GUICHE o|--o{ HISTORICO : registra
    SENHA ||--o{ HISTORICO : possui
    SENHA ||--o{ ATENDIMENTO : atendida_em
    AUTH_USER o|--o{ CHATBOT_MENSAGEM : envia
    SOLICITACAO_WIFI ||--o| ACESSO_WIFI : gera
    FUNCIONARIO ||--o{ ENTREGA_EPI : recebe
    EPI ||--o{ ENTREGA_EPI : entregue
```

**Observações de integridade:** `Atendimento.guiche` é um inteiro, não uma ForeignKey; portanto não foi desenhada relação para `Guiche`. `ControleFila`, `Propaganda` e `ApiRequestLog` não têm relações explícitas com outras entidades. O estado atual dos Models não declara unicidade composta para a numeração diária de `Senha`.
